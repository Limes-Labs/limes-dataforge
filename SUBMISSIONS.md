# Submissions

Submit only the editable files plus a completed submission manifest. The
official replay system will check the repository diff before running any score.

## Required Manifest

Use `templates/submission.json` and provide:

- commit SHA;
- changed editable files;
- method summary;
- hardware used for local runs;
- seeds and selection trials;
- public smoke metrics, including baseline delta and selection hash;
- expected failure modes;
- agent notes or ablation report, if agents were used.

## Reproducibility

Every candidate should include the exact local command:

```bash
scripts/run_smoke.sh
```

## Preflight Guard

Before asking for trusted replay, copy `templates/submission.json` to
`submission.json`, fill every placeholder, and run:

```bash
python3 scripts/check_submission.py --manifest submission.json --base origin/main
```

The guard checks that the git diff only touches editable files, that
`changed_files` exactly matches the checked diff, and that public-score fields
needed for triage are present. It is an anti-footgun screen, not a hidden
verifier and not a promotion decision.

Do not include hidden data, generated score files, large corpora, model weights,
or local caches.

## Promotion

A submission can be promoted only after trusted replay. Local results should be
tagged `candidate` at most.
