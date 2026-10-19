# PRIYAN AI Code Testing & Debugging Dataset Builder

Runnable Python pilot + roadmap toward **1,000,000 unique verified debugging tasks**.
This is not a million-task dataset. Read `sample_run/report.json` for actual counts.
No remote repository was downloaded and no external API credit was used in this build.

## Run now (Python 3.10+)

No third-party dependencies are needed for the pilot.

```bash
python builder.py demo --runner local --trusted-bundled-only --workers 4 --workdir work
python -m unittest discover -s tests -v
```

On Windows use `python`; on Linux/macOS `python3` may be needed.
Run these commands inside the extracted project directory.
Local mode is deliberately limited to original bundled code. It is NOT a sandbox.

## Isolated execution for external Python tasks

Install Docker separately, then:

```bash
docker pull python:3.11-slim
python builder.py seed
python builder.py verify --runner docker --workers 2
python builder.py export
```

The verifier resolves the local image to an immutable image ID. No network during
execution; non-root, read-only filesystem, dropped capabilities, CPU, memory and
PID limits. Use a dedicated hardened worker host for untrusted collections.
Docker runner is implemented but was not exercised in the build environment
because Docker was unavailable. Docker startup failures reject tasks, never verify them.

## Import candidate pairs

`python builder.py import --input candidates.jsonl`

Each row needs string fields `group`, `description`, `fixed`, `buggy`, `tests`,
`license`, `source`, `origin`; `license_reviewed: true` is mandatory. Python only.
Allowed origin values: `real_repository`, `original_authored`, `synthetic_mutation`.
License allowlist is an admission convenience, not an automated legal determination.
Review file-level rights, attribution, vendored files, and derived-content obligations.
The importer does not clone repositories or reconstruct environments.
Supply self-contained Python functions and tests for this pilot.
Imported code cannot use the local runner; it requires Docker.

## Outputs

- `jobs.sqlite`: resumable task queue, results and execution evidence.
- `exports/train.jsonl`: input + target patch.
- `exports/validation.jsonl`, `test.jsonl`: code + description only.
- `exports/evaluation_answers.jsonl`: restricted evaluation answers and tests.
- `exports/master.jsonl`: full provenance and evidence; contains answers.
- `report.json`: actual status, split counts, family count and limitations.

Do not expose master or evaluation answers as model evaluation inputs.
Separate all descendants of the same repository/fork into one `group` when importing.
Group hashing gives approximate 80/10/10 proportions, not exact quotas.
Bundled tasks have few families and are only a smoke-test set.

## Implemented

- 20 original seed families; finite AST operator mutations.
- Structural AST exact deduplication (formatting insensitive).
- SQLite resume and bounded parallel verification batches.
- Three before/after repeats by default; passing original, assertion-failing mutant.
- Runtime failures/timeouts rejected; recorded logs, elapsed time, return codes.
- Configuration-aware reverification when runner settings change.
- Group-consistent splits, unified diff targets, answer-separated evaluation export.
- Tests for resume, valid repair, wrong repair, timeout, import review, answer leakage.

## Not implemented yet

Remote GitHub mining; multi-file repository environments; other language runners;
independent hidden-test generation; identifier-normalized near-deduplication;
secret scanning; human review UI; distributed worker leases; Parquet export;
training or benchmarking an LLM. See `BUILD_PLAN.md` for the complete expansion.
A million-task `--limit` is a processing cap, not a generator of a million examples.
Renaming a function or changing constants is not counted as new independent knowledge.

## Reproducibility and limits

An interruption leaves uncommitted tasks pending. Re-running is safe for the bundled
seed collection; previously finished tasks are reused under the same runner settings.
Only one coordinating process should write a work directory at once.
Tests and code are trusted in the bundled local pilot. Assertion logs are not a
secure judge for malicious external code: hardened collection needs a separate
judge protocol, immutable tests and independently checked results before release.
Current tests are visible internally; no independent held-out tests were generated.
Passing them is evidence of correctness within their coverage, not a correctness proof.
The repeated execution check rejects common flakiness, not all nondeterminism.

## Dataset licensing

Original seed programs in `seeds.py` and the synthetic sample records are dedicated
under CC0-1.0. Builder software is MIT licensed (see LICENSE). External imports
retain their own source licenses; no single license overrides those obligations.
"# debug_dataset" 
