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
- public smoke metrics;
- expected failure modes;
- agent notes or ablation report, if agents were used.

## Reproducibility

Every candidate should include the exact local command:

```bash
scripts/run_smoke.sh
```

Do not include hidden data, generated score files, large corpora, model weights,
or local caches.

## Promotion

A submission can be promoted only after trusted replay. Local results should be
tagged `candidate` at most.
