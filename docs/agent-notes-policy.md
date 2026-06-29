# Agent Notes Policy

Agent notes are research hypotheses, not evidence by themselves.

Every agent-run submission should preserve:

- directions tried;
- local scores and failed variants;
- ablations used to justify the final candidate;
- known overfitting risks;
- lineage from previous submissions;
- exact commands used for public smoke runs.

Notes should help future contributors avoid repeated dead ends, but they do not
replace rerunning the harness or trusted verifier.

Use `templates/agent-notes.example.json` as the machine-checkable shape for
agent-run notes. Validate completed notes with:

```bash
python3 scripts/validate_agent_notes.py --input templates/agent-notes.example.json
```

The validator requires exactly one selected attempt, preserves rejected or mixed
attempts when multiple trials were run, and requires known overfitting risks and
negative or mixed findings.
