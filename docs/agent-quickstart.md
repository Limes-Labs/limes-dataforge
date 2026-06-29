# Agent Quickstart

This file is for coding agents pointed at DataForge.

## Mission

Improve the data-curation surface while preserving the benchmark contract.
Your local objective is `public_proxy_loss`, but your real goal is to produce a
candidate that is worth trusted replay.
Track `public_proxy_delta` against the locked public baseline so you can tell
whether a local change actually improved the smoke fixture.

## Allowed Edits

- `solution/filter.py`
- `solution/rank_documents.py`
- `solution/dedup.py`
- `solution/curriculum.py`
- `configs/submission.json`

Do not edit protected paths listed in `challenge.json`.

## Loop

1. Read `RULES.md`, `EVAL.md`, and `docs/no-cheating-protocol.md`.
2. Make one small curation change.
3. Run `scripts/run_smoke.sh`.
4. Record the score, baseline delta, selection hash, changed files, and failure
   modes.
5. Fill `submission.json` from `templates/submission.json`.
6. Run `python3 scripts/check_submission.py --manifest submission.json --base origin/main`.
7. Keep negative or mixed attempts in notes.
8. Stop when a candidate has a clear method summary and replay rationale.

## Done Criteria

- Public smoke passes.
- Tests pass.
- JSON templates still parse.
- Submission preflight passes for the completed manifest.
- The method summary explains why the change might survive hidden replay.
- Agent notes list failed variants and selection trials.
