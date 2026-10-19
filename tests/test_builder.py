import json, tempfile, unittest
from pathlib import Path
import builder

class PipelineTests(unittest.TestCase):
    def test_seed_resume_and_split_isolation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);db=builder.connection(root)
            n=builder.seed_jobs(db)
            self.assertGreater(n,20)
            self.assertEqual(builder.seed_jobs(db),0)
            groups={}
            for payload, in db.execute('SELECT task FROM jobs'):
                t=json.loads(payload);groups.setdefault(t['group'],set()).add(builder.split(t['group']))
            self.assertTrue(all(len(x)==1 for x in groups.values()))
            db.close()
    def test_real_verification_and_rejection(self):
        seed=builder.seeds()[0]
        mutant=next(code for code,_ in builder.mutations(seed['fixed']) if 'x >= 0' not in code)
        status,ev=builder.verify({**seed,'buggy':mutant},'local','',2,2)
        self.assertEqual(status,'verified');self.assertEqual(len(ev),2)
        status,_=builder.verify({**seed,'buggy':seed['fixed']},'local','',2,1)
        self.assertEqual(status,'rejected')
    def test_timeout(self):
        result=builder.execute('while True: pass','', 'local','',1)
        self.assertEqual(result['status'],'timeout')
    def test_export_answer_separation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);db=builder.connection(root)
            t={**builder.seeds()[0],'id':'test','buggy':'def solve(xs): return -1','group':next(str(i) for i in range(1000) if builder.split(str(i))=='test')}
            db.execute('INSERT INTO jobs(id,content_hash,task,status,evidence) VALUES(?,?,?,?,?)',('test','test',json.dumps(t),'verified','[]'));db.commit()
            builder.export(db,root)
            row=json.loads((root/'exports/test.jsonl').read_text())
            for key in ['fixed','tests','patch','verification']:self.assertNotIn(key,row)
            self.assertIn('fixed',json.loads((root/'exports/evaluation_answers.jsonl').read_text()))
            db.close()
    def test_external_import_requires_review(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);db=builder.connection(root);p=root/'import.jsonl'
            t={**builder.seeds()[0],'buggy':'def solve(xs): return 0','source':'example'}
            p.write_text(json.dumps(t)+'\n')
            with self.assertRaises(ValueError):builder.import_jobs(db,p)
            t['license_reviewed']=True;p.write_text(json.dumps(t)+'\n')
            self.assertEqual(builder.import_jobs(db,p),1)
            payload=json.loads(db.execute('SELECT task FROM jobs').fetchone()[0]);self.assertTrue(payload['source'].startswith('external:'))
            db.close()
if __name__=='__main__':unittest.main()
