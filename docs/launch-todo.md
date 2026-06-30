# Launch TODO

- Define hidden shard generation and hash policy.
- Create fixed dependency lockfile or container.
- Add trusted runner replay script.
- Keep `verifier/replay-contract.json` synchronized with the trusted runner.
- Freeze a real trusted-runner manifest based on
  `verifier/trusted-runner-manifest.example.json`.
- Require trusted-runner setup manifests to pass
  `scripts/validate_runner_manifest.py --input path/to/trusted-runner-manifest.json`.
- Require trusted runner outputs to pass
  `scripts/validate_replay_result.py --input path/to/replay-result.json`.
- Fill trusted-only `verifier_data/manifest.json` with shard hashes before
  promotion opens.
- Publish baseline repeated-seed result cards.
- Freeze baseline records based on `verifier/baseline-record.example.json`.
- Require promoted comparisons to use baseline records that pass
  `scripts/validate_baseline_record.py --input path/to/baseline-record.json`.
- Define submission frequency limits and anti-probing rules.
- Add contamination checks for public and hidden data.
- Add downstream mini-eval non-regression tasks.
- Add method-family fields for leaderboard grouping.
- Wire `templates/leaderboard-entry.json` into `limeslabs.eu`.
- Reuse `scripts/validate_leaderboard.py` in the `limeslabs.eu` ingestion job.
- Decide how `scaled` audits are scheduled and funded.
