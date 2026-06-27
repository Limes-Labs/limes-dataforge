## Summary

- 
- 

## Challenge Surface

- [ ] This PR changes only allowed participant paths, or it is clearly marked as maintainer-only harness/governance work.
- [ ] No hidden data, generated `score.json`, local cache, or leaderboard artifact is committed.
- [ ] Public smoke results are described as local/candidate evidence only.

## Verification

- [ ] `scripts/run_smoke.sh`
- [ ] `python3 -m unittest discover -s tests`
- [ ] `python3 -m json.tool challenge.json`
- [ ] `python3 -m json.tool templates/submission.json`
- [ ] `python3 -m json.tool templates/leaderboard-entry.json`
- [ ] `git diff --check`

## Research Notes

List failed variants, selection trials, agent notes, and expected failure modes when this PR proposes a candidate method.
