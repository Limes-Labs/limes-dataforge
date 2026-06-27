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

Everything under `harness/`, `data/`, `verifier_data/`, `leaderboard/`,
`challenge.json`, and generated score files is protected for official runs.

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
- `kept_ratio`
- `dedup_rate`
- `runtime_seconds`
- `dataset_hash`

Lower `public_proxy_loss` is better for the public smoke check. It is not an
official leaderboard score.

## Official Verifier Contract

The official verifier will apply the same submitted curation code to larger
public and hidden corpus shards. It will then train a fixed tiny language model
with a fixed tokenizer, architecture, optimizer, schedule, seed policy, and
token budget.

The primary official metric is `hidden_val_loss`, minimized. Promotion requires
repeated-seed improvement over the locked baseline plus downstream mini-eval
non-regression. A result receives the `scaled` label only if it survives a
larger token or model budget audit.

## Status Labels

```text
local -> candidate -> verified -> promoted -> replicated -> scaled
```

Local and public smoke scores are not claims. They are invitations to replay.

## Repository Map

- `challenge.json`: Benchforge-style challenge contract.
- `solution/`: editable participant surface.
- `harness/`: immutable public smoke scorer and verifier-contract check.
- `data/public_smoke/`: tiny public corpus and heldout text.
- `docs/`: anti-cheat, promotion, launch, and agent-notes policies.
- `docs/agent-quickstart.md`: short instructions for coding agents.
- `templates/`: submission, result-card, and leaderboard-entry schemas.
- `examples/limeslabs/`: candidate-only fixtures for website development.
- `tests/`: stdlib tests for contract and scorer behavior.

## Contributing

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Agent-driven attempts should also
read [docs/agent-quickstart.md](docs/agent-quickstart.md) before editing the
solution surface.
