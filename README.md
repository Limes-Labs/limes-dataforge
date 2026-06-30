# Limes DataForge

Limes DataForge is a narrow data-curation challenge for small-language-model
training efficiency. Participants edit filtering, ranking, deduplication, and
curriculum code while the benchmark harness, public smoke data, challenge
contract, and future verifier data stay fixed.

The project is designed for humans and agents running serious local research
loops. Public smoke scores are only interface and candidate checks. Public
frontier entries should be promoted only after trusted replay, repeated-seed
verification, and a scaling audit.

## What You Can Edit

- `solution/filter.py`
- `solution/rank_documents.py`
- `solution/dedup.py`
- `solution/curriculum.py`
- `configs/submission.json`

Everything under `harness/`, `data/`, `verifier/`, `verifier_data/`,
`leaderboard/`, `challenge.json`, and generated score files is protected for
official runs.

## Quickstart

Use Python 3.10 or newer. No external packages are required.

```bash
scripts/run_smoke.sh
python3 -m unittest discover -s tests
python3 -m json.tool challenge.json
```

The smoke run applies the editable solution hooks to a tiny public JSONL corpus
and writes `score.json` with:

- `public_proxy_loss`
- `baseline_public_proxy_loss`
- `public_proxy_delta`
- `kept_ratio`
- `dedup_rate`
- `selected_document_count`
- `selected_byte_count`
- `selection_hash`
- `baseline_document_count`
- `baseline_selection_hash`
- `stress_public_proxy_loss`
- `stress_baseline_public_proxy_loss`
- `stress_selection_hash`
- `stress_dataset_hash`
- `runtime_seconds`
- `dataset_hash`

Lower `public_proxy_loss` is better for the primary public smoke check. The
`stress_*` fields are candidate-only diagnostics on a second tiny public suite
with duplicate, boilerplate, and source-mix edge cases. The
`baseline_public_proxy_loss` field is a locked local baseline so agents can
measure whether a candidate changed anything useful on the public fixture. None
of these public fields is an official leaderboard score.

## Submission Preflight

Completed candidates should include a filled `submission.json` based on
`templates/submission.json`. Before requesting trusted replay, run:

```bash
python3 scripts/check_submission.py --manifest submission.json --base origin/main
```

The guard rejects protected-file edits, files outside the editable surface,
placeholder manifest values, and missing public-score fields. Passing preflight
does not imply promotion; it only means the candidate is shaped for review.

## Official Verifier Contract

The official verifier will apply the same submitted curation code to larger
public and hidden corpus shards. It will then train a fixed tiny language model
with a fixed tokenizer, architecture, optimizer, schedule, seed policy, and
token budget.

The primary official metric is `hidden_val_loss`, minimized. Promotion requires
repeated-seed improvement over the locked baseline plus downstream mini-eval
non-regression. A result receives the `scaled` label only if it survives a
larger token or model budget audit.

The machine-readable public verifier contract lives at
`verifier/replay-contract.json`. Trusted runners can inspect the same contract
through:

```bash
python3 harness/verify_hidden.py --public-contract-only
```

Trusted runner outputs should validate before any website ingestion or status
promotion:

```bash
python3 scripts/validate_replay_result.py --input templates/replay-result.example.json
```

Trusted runner setups should also validate their public manifest shape before
promotion opens:

```bash
python3 scripts/validate_runner_manifest.py --input verifier/trusted-runner-manifest.example.json
```

Locked baseline records should validate before promoted comparisons are allowed:

```bash
python3 scripts/validate_baseline_record.py --input verifier/baseline-record.example.json
```

Promotion packets bind the replay result, baseline record, runner manifest,
agent notes, result card, and leaderboard entry into one machine-checkable
evidence bundle before any public frontier status is requested:

```bash
python3 scripts/validate_promotion_packet.py --input templates/promotion-packet.example.json
```

## Status Labels

```text
local -> candidate -> verified -> promoted -> replicated -> scaled
```

Local and public smoke scores are not claims. They are invitations to replay.

## Repository Map

- `challenge.json`: Benchforge-style challenge contract.
- `solution/`: editable participant surface.
- `harness/`: immutable public smoke scorer and verifier-contract check.
- `data/public_smoke/`: tiny public corpus, stress corpus, and heldout text.
- `verifier/replay-contract.json`: public replay, promotion, and ingestion
  contract. It does not include hidden data.
- `verifier/task-spec.json`: public curation hook and hidden replay-axis
  specification. It does not include hidden data.
- `verifier/trusted-runner-manifest.example.json`: schema-only trusted-runner
  setup manifest. It does not include hidden data.
- `verifier/baseline-record.example.json`: schema-only baseline evidence
  record. It is not an official comparison baseline.
- `docs/`: anti-cheat, promotion, launch, and agent-notes policies.
- `docs/verifier-runbook.md`: trusted-runner replay checklist.
- `docs/limeslabs-ingestion.md`: website ingestion and status validation rules.
- `docs/agent-quickstart.md`: short instructions for coding agents.
- `templates/`: submission, result-card, and leaderboard-entry schemas.
- `templates/agent-notes.example.json`: machine-checkable agent trial notes.
- `templates/replay-result.example.json`: schema-only trusted replay result
  packet.
- `templates/promotion-packet.example.json`: schema-only promotion evidence
  bundle. It is not an official promotion packet.
- `examples/limeslabs/`: candidate-only fixtures for website development.
- `tests/`: stdlib tests for contract and scorer behavior.

## Contributing

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Agent-driven attempts should also
read [docs/agent-quickstart.md](docs/agent-quickstart.md) before editing the
solution surface.
