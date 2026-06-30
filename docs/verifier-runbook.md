# Trusted Verifier Runbook

This repository does not bundle hidden data. The public contract in
`verifier/replay-contract.json` describes what a trusted runner must enforce
before a DataForge result can move beyond `candidate`.

## Replay Flow

1. Start from a clean checkout of the submitted commit.
2. Confirm the submission manifest passes:

   ```bash
   python3 scripts/check_submission.py --manifest submission.json --base origin/main
   ```

3. Disable network access for official scoring.
4. Validate the trusted-runner setup manifest:

   ```bash
   python3 scripts/validate_runner_manifest.py --input path/to/trusted-runner-manifest.json
   ```

5. Mount trusted-only `verifier_data/` with a private manifest and SHA-256
   hashes.
6. Validate the locked baseline record for the same runner and seed policy:

   ```bash
   python3 scripts/validate_baseline_record.py --input path/to/baseline-record.json
   ```

7. Apply the submitted curation hooks to the public and hidden corpus shards.
8. Train the fixed tiny LM with the locked tokenizer, architecture, optimizer,
   schedule, seed list, and token budget.
9. Emit the official result fields listed in `verifier/replay-contract.json`.
10. Validate the emitted replay payload:

   ```bash
   python3 scripts/validate_replay_result.py --input path/to/replay-result.json
   ```

11. Promote only if the promotion gates in the contract are satisfied.

## Required Trusted Artifacts

- hidden shard manifest and hashes;
- fixed dependency lockfile or container digest;
- locked baseline result cards for the same seed policy;
- downstream mini-eval definition and non-regression threshold;
- replay log with code hash, dataset hash, seed count, and hardware summary.
- trusted-runner manifest JSON that passes `scripts/validate_runner_manifest.py`;
- baseline record JSON that passes `scripts/validate_baseline_record.py`;
- replay-result JSON that passes `scripts/validate_replay_result.py`.

## Anti-Probing Notes

Hidden scores must not be returned for every local attempt. Failed, timed-out,
or mixed trusted runs should be recorded in result cards when they influenced a
promotion decision. Public smoke telemetry remains candidate-only.
