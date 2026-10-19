"""Verified Python mutation dataset builder. Standard library only."""
import argparse, ast, concurrent.futures, copy, difflib, hashlib, json, os
import platform, shutil, sqlite3, subprocess, sys, tempfile, time
from pathlib import Path
from seeds import seeds

VERSION='0.1.0'
OPS={ast.Add:[ast.Sub,ast.Mult],ast.Sub:[ast.Add],ast.Mult:[ast.Add],ast.Div:[ast.Mult],ast.Mod:[ast.FloorDiv],ast.Lt:[ast.LtE,ast.Gt],ast.LtE:[ast.Lt,ast.GtE],ast.Gt:[ast.GtE,ast.Lt],ast.GtE:[ast.Gt,ast.LtE],ast.Eq:[ast.NotEq],ast.NotEq:[ast.Eq]}

def digest(x):
    return hashlib.sha256(x.encode()).hexdigest()

def canonical(code):
    return ast.dump(ast.parse(code),include_attributes=False)

def mutations(code):
    tree=ast.parse(code)
    for index,node in enumerate(ast.walk(tree)):
        sites=[]
        if isinstance(node,ast.BinOp):
            sites=[('op',None,node.op)]
        elif isinstance(node,ast.Compare):
            sites=[('ops',j,op) for j,op in enumerate(node.ops)]
        for field,position,operator in sites:
            for replacement in OPS.get(type(operator),[]):
                new=copy.deepcopy(tree)
                target=list(ast.walk(new))[index]
                if position is None:
                    setattr(target,field,replacement())
                else:
                    getattr(target,field)[position]=replacement()
                result=ast.unparse(ast.fix_missing_locations(new))+'\n'
                yield result, f'{type(operator).__name__} -> {replacement.__name__} at line {node.lineno}'

def execute(code, tests, runner, image, timeout):
    script=code+'\n'+tests
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='debugtask-') as directory:
        path=Path(directory)/'task.py';path.write_text(script)
        if runner=='docker':
            # Name permits reliable cleanup even if Docker client times out.
            name='debugtask-'+os.urandom(8).hex()
            command=['docker','run','--name',name,'--rm','--network=none','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges','--pids-limit=64','--memory=256m','--cpus=1','--user=65534:65534','--mount',f'type=bind,src={directory},dst=/work,readonly',image,'python','-I','-B','/work/task.py']
            os.chmod(directory,0o755);os.chmod(path,0o644)
        else:
            command=[sys.executable,'-I','-B',str(path)]
        try:
            result=subprocess.run(command,capture_output=True,text=True,timeout=timeout,env={'PATH':os.environ.get('PATH','')})
            output=(result.stdout+result.stderr)[-12000:]
            status='pass' if result.returncode==0 else ('assertion_failure' if 'AssertionError' in output else 'runtime_failure')
            return dict(status=status,returncode=result.returncode,output=output,seconds=round(time.monotonic()-start,4))
        except subprocess.TimeoutExpired:
            return dict(status='timeout',returncode=None,output='',seconds=timeout)
        finally:
            if runner=='docker':
                subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=15)

def verify(task,runner,image,timeout,repeats):
    evidence=[]
    for _ in range(repeats):
        after=execute(task['fixed'],task['tests'],runner,image,timeout)
        before=execute(task['buggy'],task['tests'],runner,image,timeout)
        evidence.append(dict(before=before,after=after))
        # Require assertion evidence: syntax/import crashes aren't accepted here.
        if before['status']!='assertion_failure' or after['status']!='pass':
            return 'rejected',evidence
    return 'verified',evidence

def connection(root):
    root.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(root/'jobs.sqlite')
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, content_hash TEXT UNIQUE, task TEXT NOT NULL, status TEXT NOT NULL DEFAULT "pending", evidence TEXT, runner_signature TEXT)')
    return db

def seed_jobs(db):
    inserted=0
    for seed in seeds():
        for buggy,mutation in mutations(seed['fixed']):
            h=digest(seed['group']+canonical(buggy))
            task={**seed,'id':h,'buggy':buggy,'origin':'synthetic_mutation','mutation':mutation,'source':'bundled-original-seeds-v1','schema_version':'1.0'}
            before=db.total_changes
            db.execute('INSERT OR IGNORE INTO jobs(id,content_hash,task) VALUES(?,?,?)',(h,h,json.dumps(task)))
            inserted+=db.total_changes-before
    db.commit();return inserted

def import_jobs(db,path):
    inserted=0
    for line in path.read_text().splitlines():
        if not line.strip():continue
        task=json.loads(line)
        for key in ['group','description','fixed','buggy','tests','license','source','origin']:
            if not isinstance(task.get(key),str) or not task[key].strip():raise ValueError('Missing field: '+key)
        if task['origin'] not in ['real_repository','original_authored','synthetic_mutation']:raise ValueError('Invalid origin')
        if task['license'] not in ['MIT','Apache-2.0','BSD-2-Clause','BSD-3-Clause','CC0-1.0']:raise ValueError('License needs review')
        if task.get('license_reviewed') is not True:raise ValueError('Explicit license_reviewed=true required')
        if task.get('language','python')!='python':raise ValueError('Only Python runner implemented')
        # External records can never acquire the bundled local execution exemption.
        task['source']='external:'+task['source']
        h=digest(task['group']+canonical(task['buggy'])+canonical(task['fixed'])+task['tests'])
        task['id']=h;task['schema_version']='1.0'
        n=db.total_changes
        db.execute('INSERT OR IGNORE INTO jobs(id,content_hash,task) VALUES(?,?,?)',(h,h,json.dumps(task)))
        inserted+=db.total_changes-n
    db.commit();return inserted

def split(group):
    n=int(digest(group)[:8],16)%100
    return 'train' if n<80 else 'validation' if n<90 else 'test'

def export(db,root):
    folder=root/'exports';folder.mkdir(exist_ok=True)
    # Recreate exports atomically per file. Inputs never contain answers or tests.
    records={name:[] for name in ['train','validation','test','evaluation_answers','master']}
    for task_json,evidence,signature in db.execute('SELECT task,evidence,runner_signature FROM jobs WHERE status="verified" ORDER BY id'):
        task=json.loads(task_json);task['split']=split(task['group']);task['verification']=json.loads(evidence);task['runner_signature']=json.loads(signature) if signature else None
        patch=''.join(difflib.unified_diff(task['buggy'].splitlines(True),task['fixed'].splitlines(True),fromfile='a/solution.py',tofile='b/solution.py'))
        prompt=dict(id=task['id'],group=task['group'],language='python',description=task['description'],code=task['buggy'])
        records[task['split']].append({**prompt,**({'patch':patch} if task['split']=='train' else {})})
        if task['split']!='train':records['evaluation_answers'].append(dict(id=task['id'],tests=task['tests'],fixed=task['fixed'],patch=patch))
        records['master'].append(task)
    for name,rows in records.items():
        tmp=folder/(name+'.jsonl.tmp');tmp.write_text(''.join(json.dumps(row)+'\n' for row in rows));tmp.replace(folder/(name+'.jsonl'))
    counts=dict(db.execute('SELECT status,count(*) FROM jobs GROUP BY status'))
    report={'version':VERSION,'status_counts':counts,'export_counts':{k:len(v) for k,v in records.items()},'unique_seed_families':len({r['group'] for r in records['master']}),'million_task_target_achieved':False,'limitations':['Python synthetic pilot only','Existing assertions, not independent hidden tests','Structural AST exact dedup only; no identifier-normalized near dedup','Few seed families: not a reliable generalization benchmark','No external repositories collected in bundled sample'],'python':platform.python_version()}
    (root/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['seed','import','verify','export','demo'])
    p.add_argument('--workdir',type=Path,default=Path('work'))
    p.add_argument('--input',type=Path)
    p.add_argument('--runner',choices=['local','docker'],default='docker')
    p.add_argument('--trusted-bundled-only',action='store_true')
    p.add_argument('--image',default='python:3.11-slim')
    p.add_argument('--workers',type=int,default=2)
    p.add_argument('--repeats',type=int,default=3)
    p.add_argument('--timeout',type=int,default=10)
    p.add_argument('--limit',type=int,default=1000000)
    args=p.parse_args()
    if min(args.workers,args.repeats,args.timeout,args.limit)<1:p.error('Numeric limits must be positive')
    db=connection(args.workdir)
    if args.command in ['seed','demo']:print('inserted',seed_jobs(db))
    if args.command=='import':
        if not args.input:p.error('--input required')
        print('inserted',import_jobs(db,args.input))
    if args.command in ['verify','demo']:
        if args.runner=='local' and not args.trusted_bundled_only:p.error('Local runner requires --trusted-bundled-only')
        if args.runner=='docker' and not shutil.which('docker'):p.error('Docker unavailable. Bundled demo only: --runner local --trusted-bundled-only')
        image=args.image
        if args.runner=='docker':
            info=subprocess.run(['docker','image','inspect','--format','{{.Id}}',image],capture_output=True,text=True,check=True)
            image=info.stdout.strip() # execute immutable local image ID
        sig=json.dumps(dict(runner=args.runner,image=image if args.runner=='docker' else sys.version,repeats=args.repeats,timeout=args.timeout),sort_keys=True)
        # Reverify results when execution configuration changes.
        db.execute('UPDATE jobs SET status="pending",evidence=NULL WHERE runner_signature IS NOT NULL AND runner_signature != ?',(sig,));db.commit()
        def jobs():
            for id_,payload in db.execute('SELECT id,task FROM jobs WHERE status="pending" ORDER BY id LIMIT ?',(args.limit,)):
                task=json.loads(payload)
                if args.runner=='local' and task['source']!='bundled-original-seeds-v1':continue
                yield id_,task
        # Bounded batches: no million-future queue in memory.
        stream=iter(jobs())
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            while True:
                batch=[]
                for _ in range(args.workers*2):
                    item=next(stream,None)
                    if item is None:break
                    batch.append(item)
                if not batch:break
                futures={pool.submit(verify,t,args.runner,image,args.timeout,args.repeats):i for i,t in batch}
                for future in concurrent.futures.as_completed(futures):
                    status,evidence=future.result()
                    db.execute('UPDATE jobs SET status=?,evidence=?,runner_signature=? WHERE id=?',(status,json.dumps(evidence),sig,futures[future]))
                db.commit()
    if args.command in ['export','demo']:export(db,args.workdir)
    db.close()
if __name__=='__main__':main()
