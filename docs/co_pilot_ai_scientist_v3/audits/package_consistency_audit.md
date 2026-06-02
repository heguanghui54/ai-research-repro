# Package Consistency Audit

- Audit date: `2026-06-02T11:36:32Z`
- Status: `pass`
- HEAD: `36b90bdb01d8c7c7d83ea752481ba23daab0aca9`
- Clean-clone audited commit: `aaa8127cae1c39e3a062eb2e04997ab95f80dfaf`
- Clean-clone commit is HEAD ancestor: `True`
- Manifest artifacts: `629`
- Missing manifest artifacts: `0`
- Candidate-frontier scored reviews: `13`
- Candidate-frontier delayed-control delta: `0.064`
- TFR status: `pass_with_negative_delayed_value_evidence`

## PDF Bytes

- `focused_en`: `32998`
- `focused_zh`: `61838`

## Errors

- None

## Warnings

- clean-clone manifest_artifacts_checked does not match manifest current_artifacts length because clean-clone audit targets an ancestor commit
- readiness clean-clone manifest count is stale because clean-clone audit targets an ancestor commit

## Claim Boundary

This audit checks package consistency, not scientific correctness or top-conference sufficiency. A pass means the artifact metadata agree.
