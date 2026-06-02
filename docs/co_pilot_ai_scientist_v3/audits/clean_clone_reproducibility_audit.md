# Clean Clone Reproducibility Audit

- Audit date: `2026-06-02T19:41:36Z`
- Repository: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `da62c4764df6590ea1e476e09602716dbcd8662f`
- Clone path: `/tmp/copilot-v3-clean-clone-latest`

## Commands Rerun

```bash
rm -rf /tmp/copilot-v3-clean-clone-latest
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 https://github.com/heguanghui54/ai-research-repro.git /tmp/copilot-v3-clean-clone-latest
cd /tmp/copilot-v3-clean-clone-latest
git rev-parse HEAD
python3 -m pip install -q -r requirements.txt
python3 scripts/audit_base_skill_inheritance.py
python3 scripts/audit_prospective_attention_taste_cost.py
python3 scripts/validate_evaluator_stress_trigger_policy_transfer.py
python3 scripts/audit_delayed_value_replay_multicase.py
python3 scripts/audit_long_horizon_taste_gate.py
python3 scripts/audit_benchmark_coverage.py
python3 scripts/audit_prospective_matched_budget_package.py
python3 scripts/summarize_prospective_matched_packages.py
python3 scripts/audit_focused_figure_table_readiness.py
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 scripts/audit_focused_accessibility_revision.py
python3 scripts/audit_top_conference_evidence_roadmap.py
python3 scripts/audit_objective_delivery.py
python3 scripts/audit_goal_completion_matrix.py
python3 scripts/audit_package_consistency.py
```

## Results

| Check | Result |
| --- | --- |
| Checked-out commit | `da62c4764df6590ea1e476e09602716dbcd8662f` |
| Manifest artifacts | `921/921 present` |
| Base skill inheritance | `pass; base loop preserved True; IGRE gates present True` |
| Prospective attention/taste cost | `pass; gates 7; complete attention 7/7; complete taste 7/7; active review minutes 21.00` |
| Focused figure/table readiness | `pass; EN tables 2; ZH tables 2; stale markers 0` |
| Held-out trigger-policy transfer | `pass, selected class_imbalance_trigger_0_94` |
| Held-out frozen trigger policy | `mean 0.924320, delta +0.003639, wins/losses/ties 2/0/23, triggered 5` |
| Held-out always-on evaluator-stress | `delta +0.002582, wins/losses/ties 2/2/21` |
| Multicase delayed-value replay | `pass_with_no_strict_positive_dvrs; cases 3; strict positive DVRS 0; cross-model strict positive 0; frontier winners {'six_gate_hybrid_guided': 3}` |
| LHTG/DVRS audit | `pass_with_no_positive_dvrs` |
| Benchmark coverage audit | `pass` |
| Prospective packages | `7 passing packages` |
| Candidate-frontier validation | `13 scored reviews; delayed-control delta +0.064` |
| TFR audit status | `pass_with_negative_delayed_value_evidence` |
| Focused English PDF bytes after clean rebuild | `211266` |
| Focused Chinese PDF bytes after clean rebuild | `257424` |
| Top-conference evidence roadmap audit | `pass` |
| Objective delivery audit | `pass_artifact_delivery_with_empirical_gaps` |
| Goal completion matrix | `pass_with_top_conference_gap` |
| Package consistency audit | `pass` |

## Interpretation

Clean clone at commit da62c4764 reproduced the latest pushed verification package with 921/921 manifest artifacts. It reran base-skill inheritance, prospective attention/taste cost, focused figure/table readiness, held-out trigger-policy transfer, multicase delayed-value replay, LHTG/DVRS, benchmark coverage, prospective matched packages, focused bilingual PDF builds, roadmap, objective, goal, and package-consistency audits. The focused figure/table audit confirms that the paper exposes the main figure, the evidence table, the claim-boundary table, and updated 7-package prospective evidence without stale 6-package markers.

## Claim Boundary

Latest pushed verification package is clean-clone reproducible for local artifact checks, including base-skill inheritance, focused figure/table readiness, and prospective attention/taste cost measurement. This is not a fresh remote Ubuntu rerun, independent human expert evidence, or broad co-pilot superiority proof.
