# limeslabs.eu Ingestion

This repo includes candidate-only example data for the future DataForge page.
The website should validate leaderboard payloads before rendering them.

## Validation Command

```bash
python3 scripts/validate_leaderboard.py --input examples/limeslabs/leaderboard.example.json
```

The validator reads `verifier/replay-contract.json` and enforces the status
rules used by the public frontier.

## Required Rules

- `local` and `candidate` entries must keep `hidden_val_loss` null.
- `verified`, `promoted`, `replicated`, and `scaled` entries must include a
  numeric `hidden_val_loss`.
- `verified` and later entries must include `replay.trusted_runner`.
- `promoted` and later entries must link a result card.
- `replicated` and `scaled` entries must have enough replay evidence.
- `scaled` entries must mark `replay.scaled_audit` true.

Example fixtures must say that they are not official leaderboard data.

## Website Behavior

Candidate entries may be shown as local telemetry, but they must not appear in
the promoted public frontier. Promotion requires trusted replay evidence from
the verifier contract, not public smoke scores alone.
