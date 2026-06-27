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
