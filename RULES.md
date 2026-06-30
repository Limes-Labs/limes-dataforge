# Rules

Limes DataForge is a data-curation arena. It is not an arbitrary model-training
contest. The point is to test whether filtering, ranking, deduplication, and
curriculum choices improve fixed small-LM training under replay.

## Editable Paths

Official submissions may edit only:

- `solution/filter.py`
- `solution/rank_documents.py`
- `solution/dedup.py`
- `solution/curriculum.py`
- `configs/submission.json`

## Forbidden Paths

Official submissions must not edit:

- `harness/**`
- `data/**`
- `verifier/**`
- `verifier_data/**`
- `challenge.json`
- `score.json`
- `leaderboard/**`

The same forbidden paths are listed in `challenge.json` and enforced by trusted
review before promotion.

The local preflight guard can catch most accidental contract violations before
review:

```bash
python3 scripts/run_public_audit.py
python3 scripts/check_submission.py --manifest submission.json --base origin/main
python3 scripts/validate_local_bundle.py --manifest submission.json --base origin/main
```

## Prohibited Behavior

- Using hidden data, hidden scores, or final verifier outputs to choose a
  candidate.
- Downloading data, models, labels, or external services during official
  scoring.
- Modifying the harness, public smoke data, verifier specs, challenge contract,
  or generated score file.
- Encoding validation or heldout content inside solution code or config.
- Claiming a public smoke result as a verified research finding.
- Omitting failed, timed-out, negative, or mixed runs from agent notes when they
  influenced the selected candidate.

## Tracks

- `public-smoke`: local correctness and interface validation.
- `trusted-replay`: hidden shard replay with fixed tiny-LM training.
- `replicated`: repeated seeds and baseline comparison under the locked
  protocol.
- `scaling-audit`: larger token or model budget replay for top candidates.

Only trusted replay and later tracks can appear on the public frontier.
