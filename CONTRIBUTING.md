# Contributing

DataForge contributions should make one research question easier to test.

## Candidate Submissions

Candidate submissions may edit only:

- `solution/filter.py`
- `solution/rank_documents.py`
- `solution/dedup.py`
- `solution/curriculum.py`
- `configs/submission.json`

Run:

```bash
scripts/run_smoke.sh
python3 -m unittest discover -s tests
```

Open a candidate issue and include public smoke output, search accounting,
agent notes, and expected failure modes. Do not claim a public smoke result is
verified.

## Maintainer Changes

Maintainer-only work may update harness, docs, templates, CI, or verifier
contracts. These changes should explain why the benchmark contract changes and
must keep public smoke reproducible from a clean checkout.

## Review Rule

Prefer honest negative and mixed findings over leaderboard theater. A method
that fails hidden replay is still useful if it teaches future agents what not
to repeat.
