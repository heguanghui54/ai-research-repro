# Clean Clone Reproducibility Audit

- Audit date: `2026-06-02T20:52:13Z`
- Repository: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `fa7269cab5f1b3750c36c5b58b9c5867f002eb44`
- Clone path: `/tmp/copilot-v3-clean-clone-cifar-latest`

## Commands Rerun

```bash
rm -rf /tmp/copilot-v3-clean-clone-cifar-latest
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 https://github.com/heguanghui54/ai-research-repro.git /tmp/copilot-v3-clean-clone-cifar-latest
cd /tmp/copilot-v3-clean-clone-cifar-latest
python3 -m pip install -q -r requirements.txt
python3 scripts/audit_mlagentbench_cifar10_official.py
python3 scripts/audit_second_non_fml_priority_package.py
python3 scripts/audit_benchmark_coverage.py
python3 scripts/audit_top_conference_evidence_roadmap.py
python3 scripts/audit_objective_delivery.py
python3 scripts/audit_goal_completion_matrix.py
python3 scripts/audit_package_consistency.py
```

## Results

| Check | Result |
| --- | --- |
| Checked-out commit | `fa7269cab5f1b3750c36c5b58b9c5867f002eb44` |
| Manifest artifacts | `938/938 present` |
| MLAgentBench CIFAR10/debug official audit | `pass; baseline 0.5103; co-pilot-selected 0.7782; delta +0.2679` |
| Second non-FML priority package | `pass; evidence class scored_official_mlagentbench_non_fml_plus_official_like_package` |
| Benchmark coverage audit | `pass` |
| Top-conference evidence roadmap | `pass` |
| Objective delivery audit | `pass_artifact_delivery_with_empirical_gaps` |
| Goal completion matrix | `pass_with_top_conference_gap` |
| Package consistency audit | `pass` |

## Interpretation

Clean clone at commit `fa7269cab` reproduced the latest pushed verification package with `938/938` manifest artifacts. It reran the new MLAgentBench CIFAR10/debug official audit, the second non-FML priority package audit, benchmark coverage, top-conference roadmap, objective delivery, goal completion, and package-consistency audits.

## Claim Boundary

Latest pushed verification package is clean-clone reproducible for local artifact checks, including the new scored official MLAgentBench CIFAR10/debug audit. This is not a fresh remote Ubuntu rerun, independent human expert evidence, multi-seed CIFAR robustness, another official benchmark task, or broad co-pilot superiority proof.
