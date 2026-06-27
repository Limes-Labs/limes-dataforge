# No-Cheating Protocol

## Frozen Question

- Objective: improve fixed small-LM training by changing data curation only.
- Public metric: `public_proxy_loss`.
- Official metric: `hidden_val_loss`.
- Direction: lower is better.

## Data Boundaries

- Train/proposal data: public smoke data and participant-owned local corpora.
- Validation/selection data: public smoke proxy only.
- Heldout/final data: trusted verifier shards and hidden validation splits.

Heldout labels, hidden shard contents, hidden verifier outputs, and private
leaderboard results may not influence candidate selection.

## Budget Accounting

Submissions must report local hardware, runtime, selection trials, seeds,
preprocessing cost, and any agent search used to choose the candidate.

## Promotion Gate

Promote only after trusted replay shows repeated-seed improvement over the
locked baseline and downstream mini-eval non-regression. Mark as `negative` or
`mixed` when proxy wins do not survive replay.
