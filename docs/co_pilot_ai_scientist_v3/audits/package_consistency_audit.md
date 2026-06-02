# Package Consistency Audit

- Audit date: `2026-06-02T11:11:20Z`
- Status: `pass`
- HEAD: `80d30961b2c0a8d4c1df0bdfc79d3422bd85f94e`
- Clean-clone audited commit: `38dc8c8f7baecf85b47de3f1f45b14836b3d9ec4`
- Clean-clone commit is HEAD ancestor: `True`
- Manifest artifacts: `621`
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
