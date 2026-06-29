# Launch TODO

- Define hidden shard generation and hash policy.
- Create fixed dependency lockfile or container.
- Add trusted runner replay script.
- Keep `verifier/replay-contract.json` synchronized with the trusted runner.
- Fill trusted-only `verifier_data/manifest.json` with shard hashes before
  promotion opens.
- Publish baseline repeated-seed result cards.
- Define submission frequency limits and anti-probing rules.
- Add contamination checks for public and hidden data.
- Add downstream mini-eval non-regression tasks.
- Add method-family fields for leaderboard grouping.
- Wire `templates/leaderboard-entry.json` into `limeslabs.eu`.
- Reuse `scripts/validate_leaderboard.py` in the `limeslabs.eu` ingestion job.
- Decide how `scaled` audits are scheduled and funded.
