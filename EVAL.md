# Evaluation

The public smoke evaluator is intentionally small. It proves that a submission
implements the required interface and gives agents a cheap local objective.
Official scores require the hidden verifier contract described below.

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
- `kept_ratio`
- `dedup_rate`
- `runtime_seconds`
- `dataset_hash`

The dataset hash is computed from public smoke files so agents can detect local
drift.

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
