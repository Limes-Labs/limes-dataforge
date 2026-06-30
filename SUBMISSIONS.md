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
python3 scripts/validate_local_bundle.py --manifest submission.json --base origin/main
```

The guard checks that the git diff only touches editable files, that
`changed_files` exactly matches the checked diff, and that public-score fields
needed for triage are present. It is an anti-footgun screen, not a hidden
verifier and not a promotion decision. The local bundle validator reruns the
public scorer and invariant probes, then checks the manifest and search ledger
against those fresh local outputs. It ignores only unstable runtime telemetry.

Agent-run submissions should also include validated notes:

```bash
python3 scripts/validate_agent_notes.py --input agent-notes.json
```

Requests for `verified`, `promoted`, `replicated`, or `scaled` status must also
include trusted replay evidence that validates locally:

```bash
python3 scripts/validate_replay_result.py --input replay-result.json
```

Do not include hidden data, generated score files, large corpora, model weights,
protected verifier files, or local caches.

## Promotion

A submission can be promoted only after trusted replay. Local results should be
tagged `candidate` at most.
