# Promotion Policy

DataForge uses explicit status labels:

```text
local -> candidate -> verified -> promoted -> replicated -> scaled
```

- `local`: a contributor run on public smoke or private local data.
- `candidate`: a submitted diff worth replay.
- `verified`: trusted runner reproduced the result under the locked protocol.
- `promoted`: accepted into the public frontier.
- `replicated`: repeated seeds satisfy the promotion gate.
- `scaled`: larger token or model budget audit still improves the baseline.

Public smoke scores never receive `verified`, `promoted`, `replicated`, or
`scaled` status by themselves.

Before any trusted replay is scheduled, the candidate must have a validated
replay request. The request binds the candidate packet, replay quota, freeze
state, and anti-probing declarations. A replay request can ask only for
`verified`; later status changes require replay and promotion packets.

Promotion requests must include a validated promotion packet. The packet binds
the submission manifest, agent notes, trusted-runner manifest, locked baseline
record, replay result, result card, and leaderboard entry. A replay result alone
is not enough for `promoted` or later status.

Schema-only examples may validate, but they must keep `promotion_ready` false
and must state that they are not official promotion packets.
