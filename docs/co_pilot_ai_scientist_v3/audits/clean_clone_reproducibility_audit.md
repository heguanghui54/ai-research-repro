# Clean Clone Reproducibility Audit

- Audit date: `2026-06-02T18:54:36Z`
- Repository: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `0bc6b479c63f6cb68e4d241969c7acfb2b57ff0a`
- Clone path: `/tmp/copilot-v3-clean-clone-latest`

## Commands Rerun

```bash
rm -rf /tmp/copilot-v3-clean-clone-latest
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 https://github.com/heguanghui54/ai-research-repro.git /tmp/copilot-v3-clean-clone-latest
cd /tmp/copilot-v3-clean-clone-latest
git rev-parse HEAD
python3 -m pip install -q -r requirements.txt
python3 scripts/analyze_evaluator_stress_trigger_policy.py --package-id prospective_matched_open_data_multitask_20260603
python3 scripts/analyze_evaluator_stress_trigger_policy.py --package-id prospective_matched_open_data_multitask_holdout_20260603
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
| Checked-out commit | `0bc6b479c63f6cb68e4d241969c7acfb2b57ff0a` |
| Manifest artifacts | `907/907` present |
| Prospective packages | `7` passing packages |
| Held-out trigger-policy analysis | best policy `class_imbalance_trigger_0_94` |
| Held-out best trigger policy | mean `0.924320`, delta `+0.003639`, wins/losses/ties `2`/`0`/`23`, triggered `5` |
| Held-out always-on evaluator-stress | delta `+0.002582`, wins/losses/ties `2`/`2`/`21` |
| Candidate-frontier validation | `13` scored reviews; delayed-control delta `+0.064` |
| TFR audit status | `pass_with_negative_delayed_value_evidence` |
| Focused English PDF bytes after clean rebuild | `210777` |
| Focused Chinese PDF bytes after clean rebuild | `256373` |
| Objective delivery audit | `pass_artifact_delivery_with_empirical_gaps` |
| Goal completion matrix | `pass_with_top_conference_gap` |
| Package consistency audit | pass |

## Interpretation

Clean clone at commit 0bc6b479c reproduced the held-out trigger-policy validation and local audits with 907/907 manifest artifacts. The held-out best policy class_imbalance_trigger_0_94 achieved delta +0.003639, 2 wins, 0 losses, and 23 ties, while held-out always-on evaluator-stress retained 2 losses.

## Claim Boundary

Held-out trigger-policy validation is open-data split validation within one task family; it improves participation-mode design evidence but does not prove broad benchmark or paper-quality superiority.
