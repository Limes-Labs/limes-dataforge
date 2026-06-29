# limeslabs.eu Fixtures

These files are static examples for building the future `limeslabs.eu`
DataForge page. They are not official leaderboard data.

Use them to render:

- a candidate-only public smoke row;
- a result-card link;
- the local/candidate/verified/promoted/replicated/scaled status language.

Rules for website prototypes:

- show `public_proxy_loss` as local candidate telemetry;
- show `baseline_public_proxy_loss` and `public_proxy_delta` as local
  baseline comparison fields;
- keep `hidden_val_loss` null until trusted replay exists;
- do not render candidate examples as frontier records;
- link back to the repository and result card for provenance.

Validate fixture payloads with:

```bash
python3 scripts/validate_leaderboard.py --input examples/limeslabs/leaderboard.example.json
```
