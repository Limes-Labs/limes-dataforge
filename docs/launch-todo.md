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
- Require trusted replay requests to pass
  `scripts/validate_replay_request.py --input path/to/replay-request.json`
  before hidden work is scheduled.
- Require promotion packets to pass
  `scripts/validate_promotion_packet.py --input path/to/promotion-packet.json`
  before any `promoted`, `replicated`, or `scaled` website status.
- Populate trusted-only `verifier_data/manifest.json` from the public shape in
  `verifier/hidden-manifest.example.json` and require it to pass
  `scripts/validate_hidden_manifest.py --input path/to/verifier_data/manifest.json`
  before promotion opens.
- Publish baseline repeated-seed result cards.
- Freeze baseline records based on `verifier/baseline-record.example.json`.
- Require promoted comparisons to use baseline records that pass
  `scripts/validate_baseline_record.py --input path/to/baseline-record.json`.
- Define submission frequency limits and anti-probing rules.
- Wire replay-request quotas into the trusted runner queue.
- Add contamination checks for public and hidden data.
- Add downstream mini-eval non-regression tasks.
- Add method-family fields for leaderboard grouping.
- Wire `templates/leaderboard-entry.json` into `limeslabs.eu`.
- Reuse `scripts/validate_leaderboard.py` in the `limeslabs.eu` ingestion job.
- Reuse `scripts/validate_promotion_packet.py` in the `limeslabs.eu` promotion
  ingestion job.
- Decide how `scaled` audits are scheduled and funded.
