# PRIYAN DEBUG-1M: detailed expansion and execution plan

## 1. Objective and truthful size accounting

Target: 1,000,000 unique, execution-verified testing/debugging tasks, multilingual,
with source attribution, isolated runs, independent tests and family-disjoint splits.
Stretch: 5 million only after quality, rights and economics are measured.
The included implementation is a Python synthetic pilot, not the completed target.
All counts below are planned quotas, not available records.
Count independent source families, unique accepted tasks, training views and tokens
separately. Ten chat formats from one bug are still one underlying task.
Reject identifiers-only and formatting-only variations from growth metrics.

## 2. Language and source targets

| Language | Task target | Planned runner |
|---|---:|---|
| Python | 300,000 | pytest/property tests |
| JavaScript | 180,000 | Node + Vitest |
| TypeScript | 180,000 | Type checking + Vitest |
| Java | 120,000 | JUnit + locked build |
| C++ | 100,000 | CTest + applicable sanitizers |
| Go | 60,000 | go test |
| Rust | 40,000 | cargo test |
| C# | 20,000 | dotnet test |

Origin quotas: 450k real repository bugs, 400k controlled mutations, 150k original
human-reviewed/specification-driven authored tasks. These are ambitious research
quotas, not an assertion that enough redistributable tasks already exist.
Treat source scarcity as a reason to revise quotas, never fabricate real bugs.
Limit verified variants per family to 10; target at least 100k independent families.
Use repository/fork lineage as split unit, even if that produces fewer split units.

## 3. What one accepted task contains

Task ID, schema version, language, requirement, bug category, difficulty,
source URL, repository/issue/base/fix commits, file-level license evidence,
attribution, collection time, content hashes, source family, buggy snapshot,
reference patch, test assets, runner image digest, dependency lock digest,
before/after exit codes and bounded logs, repeated-run evidence, reviewer state,
release eligibility, split and lineage. Real and synthetic origins stay explicit.
Add `task_type` values repair/test_generation/localization/no_change/needs_context.
Code-correctness tasks without a fix require separate acceptance rules.

## 4. Collection workflow

1. Curate a repository allowlist by language, tests, activity and reviewed rights.
2. Mirror exact revisions using a rate-limited GitHub collector with checkpoints.
3. Find issue-linked bug fixes using labels, changed tests and patch inspection.
4. Reject formatting changes, feature additions, missing tests and mixed commits.
5. Reconstruct the pre-fix dependency environment in a disposable worker.
6. Confirm known-good reference tests; distinguish setup failures from bugs.
7. Apply independently reviewed reproducer to pre-fix code; require relevant failure.
8. Apply fix and run reproducer plus regression and independent tests.
9. Remove answer-bearing commit text or comments from model inputs.
10. Record evidence and rights decision before publication.

No unrestricted scraper is shipped. The current importer accepts already prepared
Python code pairs. Automated source mining and license evidence extraction are next
modules; do not interpret an accepted license string as proof of redistribution rights.

## 5. Controlled mutations and authored tasks

Mutation operators: boundaries, boolean logic, arithmetic, wrong index, null checks,
wrong default, omitted await, serialization, state update, resource cleanup.
Reject equivalent/surviving mutations, irrelevant exceptions, syntactically invalid
mutants (unless intentionally building a distinct syntax-repair task class), and
mutants that break environment setup instead of the specified behaviour.
Apply single-edit localization checks; the pilot AST mutator is an initial source,
not a complete realistic bug generator. Audit tree-edit scope before scaling.

Authored tasks: write contract first, reference implementation second, independently
reviewed tests third, buggy variant last. Include APIs, data processing, parsers,
validation, scheduling, file formats, state machines and concurrency only when the
runner can reproduce deterministic outcomes. Avoid thousands of arithmetic renames.

## 6. Verification gates

Admission -> rights -> secrets/PII scan -> environment -> baseline -> bug reproduction
-> reference repair -> independent tests -> regression -> repeated runs -> dedup
-> manual audit -> release eligible.

Separate states: pending, setup_failed, reproduce_failed, repair_failed, flaky,
duplicate, rights_blocked, review_required, verified, release_eligible.
The pilot collapses rejection states in SQLite but preserves run status/log evidence.
A future release must expand this state machine before large collections.

Use immutable judge assets outside the candidate write scope. Separate compiler,
setup and test failures. Never trust code-controlled stdout as an acceptance oracle.
Reference fixes can be incomplete; generate independent tests from specifications,
properties or differential reference behaviours and require human review for ambiguity.
At least three repeat runs for the pilot; add scheduled sample reruns under a second
compatible environment to identify environmental overfitting.

## 7. Isolation and infrastructure

Pilot: one coordinator, SQLite WAL, 2–4 workers, fixed-size batches, JSONL export.
Scale stage: object store for immutable code/logs/images; Postgres metadata;
queue with leased jobs, heartbeat, attempt limit and crash recovery; stateless workers.
One object per content hash, compressed shards, bounded logs, lifecycle policies.
Network only during isolated dependency preparation; execution workers are offline.
Hardened disposable VM/microVM boundaries for adversarial inputs. No host credentials.
Pin images and dependencies, enforce CPU/RAM/PID/time/output limits and disk quotas.

Distributed jobs need unique keys `(task_hash, runner_digest, verifier_version)`;
at-least-once dispatch plus idempotent result writes. Never share the pilot SQLite
work directory between multiple coordinators.

## 8. Deduplication and splitting

Exact file hash, AST structural hash, identifier-normalized AST, token MinHash,
fork detection and shared-source lineage. Merge related records into components
before split assignment. Review cross-language translations as related data.
Use approximately 80/10/10 family-disjoint splits plus a recent private holdout.
Keep benchmark contamination fingerprints separate from training source indexes.
Export evaluation inputs separately from answers, tests, patches and evidence.
With only 20 seed families, the sample hash split may have an empty validation set;
this pilot is not a generalization benchmark. Do not shuffle rows to hide that issue.

## 9. Suggested task mix within the total

Repair/localization 60%, test generation 20%, iterative repair 10%, correct code
(no change) 5%, incomplete context/clarification 5%. Task views can overlap;
underlying task accounting must avoid double counting.
Capture concise evidence-based explanations, never invented terminal output or
purported hidden model reasoning. Iterative attempts must have actual run feedback.

## 10. Size and resource estimates (assumptions, not measurements)

At 10–30 KB per normalized task, 1M rows take about 10–30 GB uncompressed.
Repositories, images, logs and dependencies can dominate: budget hundreds of GB
or more and measure after the 1k pilot. A 32 GB RAM workstation can develop and
run bounded batches; GPU is unnecessary for deterministic verification.
Optional model-generated tests/explanations have separate GPU/API costs.
At 2k–8k tokens/task, 1M records correspond to roughly 2–8B tokens before export
view duplication. Measure the actual tokenizer instead of equating rows to tokens.

Candidates needed = accepted target / measured acceptance rate.
At an assumed 20% acceptance, 1M accepted tasks require 5M candidates.
At an assumed 30 CPU seconds/candidate for all checks, that is about 41,667 CPU
hours, or 54 idealized days on 32 fully utilized workers; setup, retries, idle time
and source collection extend elapsed time. These are scenarios, not a quote.
Track CPU-seconds, image storage, network egress, review minutes, model tokens and
cost per unique accepted family. Stop collection when the agreed budget is reached.

## 11. Milestones and gates

M0 (delivered): executable pilot, original seeds, repeat verification, resumable jobs,
answer-separated JSONL exports, automated tests and evidence report.
M1 (1k tasks): expand independent Python seed families, independent tests, rights
ledger, scanner, stronger dedup, machine-readable candidate validation.
M2 (10k): real issue collector, JS/TS runners, environment manifests, audit tooling.
M3 (100k): all priority runners, distributed leases, Parquet shards, 1k audited tasks,
benchmark contamination checks, baseline repair and regression metrics.
M4 (1M): reviewed quotas, >=100k source families goal, release audit, reproducibility
sample on clean workers, dataset card, attribution bundle and signed shard manifest.
Scale only after error rates and acceptance economics pass the previous milestone.
No fixed 1M completion date is justified before the first thousand-task pilot.

## 12. Quality dashboard and release criteria

Report candidates/accepted/rejected by source, language and failure category;
unique families; mutation survival; timeout/flaky rates; split overlap; license blocks;
manual-audit defect rate with sample size and confidence interval; CPU cost;
patch success, regression rate and no-change accuracy for baseline models.
Require zero detected exact/family leakage, complete provenance, and no known secrets.
For correctness audit, sample by language, origin and difficulty; publish uncertainty
and halt release for critical defects. "Tests pass" is not universal correctness.

## 13. Next implementation files

collectors/github_issues.py; provenance/rights_ledger.py; scanners/secrets.py;
runners/javascript.py; runners/typescript.py; verification/independent_tests.py;
dedup/normalized_ast.py; queue/leases.py; exporters/parquet.py; review/audit_cli.py.
Implement in this order, gated by tests and small source-specific pilots.
