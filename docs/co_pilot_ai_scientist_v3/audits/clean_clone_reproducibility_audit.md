# Clean Clone Reproducibility Audit

- Audit date: `2026-06-02T18:45:55Z`
- Repository: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `e9defdde0b59bc242ceb728ec76fc274a8ef8eea`
- Clone path: `/tmp/copilot-v3-clean-clone-latest`

## Commands Rerun

```bash
rm -rf /tmp/copilot-v3-clean-clone-latest
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 https://github.com/heguanghui54/ai-research-repro.git /tmp/copilot-v3-clean-clone-latest
cd /tmp/copilot-v3-clean-clone-latest
git rev-parse HEAD
python3 -m pip install -q -r requirements.txt
python3 scripts/analyze_evaluator_stress_trigger_policy.py
python3 scripts/audit_benchmark_coverage.py
python3 scripts/audit_prospective_matched_budget_package.py
python3 scripts/summarize_prospective_matched_packages.py
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 scripts/audit_objective_delivery.py
python3 scripts/audit_goal_completion_matrix.py
python3 scripts/audit_package_consistency.py
```

## Results

| Check | Result |
| --- | --- |
| Checked-out commit | `e9defdde0b59bc242ceb728ec76fc274a8ef8eea` |
| Manifest artifacts | `898/898` present |
| Trigger-policy analysis | best policy `class_imbalance_trigger_0_94` |
| Best trigger policy | mean `0.927934`, delta `+0.003077`, wins/losses/ties `2`/`0`/`23`, triggered `5` |
| Always-on evaluator-stress | delta `+0.001569`, wins/losses/ties `2`/`2`/`21` |
| Benchmark coverage audit | pass |
| Prospective package audit | pass, `6` packages |
| Focused English PDF bytes after clean rebuild | `210227` |
| Focused Chinese PDF bytes after clean rebuild | `255783` |
| Objective delivery audit | `pass_artifact_delivery_with_empirical_gaps` |
| Goal completion matrix | `pass_with_top_conference_gap` |
| Package consistency audit | pass |
| Candidate-frontier validation | `13` scored reviews; delayed-control delta `+0.064` |
| TFR audit status | `pass_with_negative_delayed_value_evidence` |

## Interpretation

A fresh shallow clone at commit e9defdde0 reproduced the trigger-policy analysis, benchmark coverage audit, prospective package audit and summary, focused PDF builds, objective delivery, goal completion, and package consistency. The best policy class_imbalance_trigger_0_94 improves mean balanced accuracy to 0.927934 with delta +0.003077, 2 wins, 0 losses, 23 ties, and 5 trigger events, compared with always-on evaluator-stress delta +0.001569 with 2 losses.

## Claim Boundary

Latest pushed verification package is clean-clone reproducible for the trigger-policy analysis and local audits. The trigger analysis is post-hoc design evidence over an archived open-data pilot, not a new independent benchmark run or top-conference empirical sufficiency.
