# Dataset card — PRIYAN Debug Pilot v0.1.0

35 accepted synthetic Python debugging tasks from 17 original seed families.
43 candidates; 8 rejected. Three before/after verification repeats for accepted tasks.
Source: bundled original seed programs, CC0-1.0. No mined repository tasks.
Execution: trusted local Python 3.12.14; no Docker isolation exercised in this build.
Train: 33, validation: 0, test: 2. Group hash split; too few families for evaluation.
Use: pipeline development and smoke testing, not a performance leaderboard.
Limitations: small synthetic set, fixed assertions, no independent hidden tests,
no identifier-normalized near dedup, no human correctness audit or model training.
The million-task configuration describes a future goal, not current data volume.
Evaluation answers and master records are distributed for reproducibility and must
not be passed as evaluation inputs. Local trusted mode must not execute imports.
