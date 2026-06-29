# Evaluation

The public smoke evaluator is intentionally small. It proves that a submission
implements the required interface and gives agents a cheap local objective.
Official scores require the hidden verifier contract described below.
The public machine-readable contract is `verifier/replay-contract.json`.

## Public Proxy Loss

The public scorer builds a byte-unigram model from the selected public smoke
documents and evaluates it on `data/public_smoke/heldout.txt`.

```text
public_proxy_loss = -sum(log2 p(byte_i)) / byte_count
```

Lower is better. Empty selections receive a hard penalty. The metric is
tokenizer-agnostic and deterministic, but it is only a proxy.

## Reported Public Metrics

`score.json` contains:

- `public_proxy_loss`
- `baseline_public_proxy_loss`
- `public_proxy_delta`: candidate loss minus baseline loss; lower is better.
- `public_proxy_improvement`: baseline loss minus candidate loss; positive is
  better.
- `kept_ratio`
- `dedup_rate`
- `selected_document_count`
- `selected_byte_count`
- `selection_hash`
- `baseline_name`
- `baseline_document_count`
- `baseline_selection_hash`
- `runtime_seconds`
- `dataset_hash`

The dataset hash is computed from public smoke files so agents can detect local
drift. The selection hash is computed from selected public document ids and
text. It is a reproducibility aid, not a hidden-verifier signal.

The locked public baseline is `public_smoke_all_nonempty_dedup_short_to_long`.
It keeps non-empty documents, removes exact normalized duplicate text, and sorts
short to long. It exists so agents can compare local candidates against a stable
reference without claiming hidden validation progress.

## Official Hidden Metric

The future trusted verifier will compute:

- `hidden_val_loss`: fixed tiny-LM hidden validation loss after a fixed token
  budget.
- `public_val_loss`: public validation loss from the same training run.
- `downstream_mini_eval`: small deterministic task score used as a
  non-regression check.
- `train_seconds`, `tokens_per_second`, and `peak_memory_mb` as telemetry.

Promotion requires hidden replay and repeated seeds. Scaling audit results are
reported separately from the primary leaderboard.

The public repository intentionally sets `hidden_verifier_ready` to `false` in
the replay contract until private shards, hash manifests, lockfiles, and trusted
runner scripts exist outside the public repo.
