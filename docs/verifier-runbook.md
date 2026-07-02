# Trusted Verifier Runbook

This repository does not bundle hidden data. The public contract in
`verifier/replay-contract.json` describes what a trusted runner must enforce
before a DataForge result can move beyond `candidate`.

## Replay Flow

1. Start from a clean checkout of the submitted commit.
2. Confirm the submission manifest passes:

   ```bash
   python3 scripts/check_submission.py --manifest submission.json --base origin/main
   python3 scripts/validate_local_bundle.py --manifest submission.json --base origin/main
   ```

3. Confirm the local bundle report is clean. It should bind the manifest,
   public score, invariant probes, and search ledger before any hidden replay.
4. Validate the trusted replay request before scheduling hidden work:

   ```bash
   python3 scripts/validate_replay_request.py --input path/to/replay-request.json
   ```

5. Disable network access for official scoring.
6. Validate the trusted-runner setup manifest:

   ```bash
   python3 scripts/validate_runner_manifest.py --input path/to/trusted-runner-manifest.json
   ```

7. Mount trusted-only `verifier_data/` with a private manifest and SHA-256
   hashes, then validate that manifest against the public shape:

   ```bash
   python3 scripts/validate_hidden_manifest.py --input path/to/verifier_data/manifest.json
   ```

8. Validate the locked baseline record for the same runner and seed policy:

   ```bash
   python3 scripts/validate_baseline_record.py --input path/to/baseline-record.json
   ```

9. Apply the submitted curation hooks to the public and hidden corpus shards.
10. Train the fixed tiny LM with the locked tokenizer, architecture, optimizer,
   schedule, seed list, and token budget.
11. Emit the official result fields listed in `verifier/replay-contract.json`.
12. Validate the emitted replay payload:

   ```bash
   python3 scripts/validate_replay_result.py --input path/to/replay-result.json
   ```

13. Build and validate the promotion packet that binds the replay result,
    baseline record, runner manifest, agent notes, result card, and leaderboard
    entry:

    ```bash
    python3 scripts/validate_promotion_packet.py --input path/to/promotion-packet.json
    ```

14. Promote only if the promotion gates in the contract and packet are
    satisfied.

## Required Trusted Artifacts

- hidden shard manifest and hashes;
- fixed dependency lockfile or container digest;
- hidden manifest JSON that passes `scripts/validate_hidden_manifest.py`;
- replay request JSON that passes `scripts/validate_replay_request.py`;
- locked baseline result cards for the same seed policy;
- downstream mini-eval definition and non-regression threshold;
- replay log with code hash, dataset hash, seed count, and hardware summary;
- trusted-runner manifest JSON that passes `scripts/validate_runner_manifest.py`;
- baseline record JSON that passes `scripts/validate_baseline_record.py`;
- replay-result JSON that passes `scripts/validate_replay_result.py`;
- promotion-packet JSON that passes
  `scripts/validate_promotion_packet.py`.

## Anti-Probing Notes

Hidden scores must not be returned for every local attempt. Failed, timed-out,
or mixed trusted runs should be recorded in result cards when they influenced a
promotion decision. Public smoke telemetry remains candidate-only.
