# Package Consistency Audit

- Audit date: `2026-06-02T12:01:22Z`
- Status: `pass`
- HEAD: `7672c30b51d846371b6c968f6054ef312d398a12`
- Clean-clone audited commit: `fb3e666b6f75e1342a59289aa24ee61552356bd8`
- Clean-clone commit is HEAD ancestor: `True`
- Manifest artifacts: `636`
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
