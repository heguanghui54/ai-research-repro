# Clean Clone Reproducibility Audit

- Audit date: `2026-06-02T18:37:56Z`
- Repository: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `4180584845efcc1bcc5ddc6bebc8b18dad222699`
- Clone path: `/tmp/copilot-v3-clean-clone-latest`

## Commands Rerun

```bash
rm -rf /tmp/copilot-v3-clean-clone-latest
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 https://github.com/heguanghui54/ai-research-repro.git /tmp/copilot-v3-clean-clone-latest
cd /tmp/copilot-v3-clean-clone-latest
git rev-parse HEAD
python3 -m pip install -q -r requirements.txt
python3 scripts/audit_benchmark_coverage.py
python3 scripts/audit_prospective_matched_budget_package.py
python3 scripts/summarize_prospective_matched_packages.py
python3 scripts/audit_global_skill_engineering_chain.py
python3 scripts/audit_focused_accessibility_revision.py
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 scripts/audit_objective_delivery.py
python3 scripts/audit_goal_completion_matrix.py
python3 scripts/audit_long_horizon_taste_gate.py
python3 scripts/audit_temporal_frontier_replay.py
python3 scripts/audit_top_conference_evidence_roadmap.py
python3 scripts/audit_human_expert_blind_review_packet.py
python3 scripts/audit_package_consistency.py
```

## Results

| Check | Result |
| --- | --- |
| Checked-out commit | `4180584845efcc1bcc5ddc6bebc8b18dad222699` |
| Manifest artifacts | `895/895` present |
| Requirements install | pass |
| Benchmark coverage audit | pass |
| Prospective package audit | pass, `6` packages |
| Prospective package summary | `3` co-pilot wins, `3` autonomous/tie outcomes |
| Open-data evaluator-stress pilot | Pass: `5` tasks x `5` split seeds = `25` paired selections; delta `0.001569`; wins/ties `2`/`2`/`21`; selection changed `4` times |
| Global skill engineering chain | pass, 6/6 steps |
| Focused accessibility audit | pass |
| Focused English PDF bytes after clean rebuild | `209654` |
| Focused Chinese PDF bytes after clean rebuild | `253745` |
| Objective delivery audit | `pass_artifact_delivery_with_empirical_gaps` |
| Goal completion matrix | `pass_with_top_conference_gap` |
| LHTG/DVRS audit | `pass_with_no_positive_dvrs` |
| TFR audit | `pass_with_negative_delayed_value_evidence` |
| Top-conference roadmap audit | pass |
| Human expert blind-review packet audit | `pass_prepared_no_human_ratings` |
| Package consistency audit | pass |

## Interpretation

A fresh shallow clone of the pushed branch at commit 418058484 reproduced the current verification package with 895/895 manifest artifacts present. It reran benchmark coverage, prospective matched-package audit and summary, the global skill engineering chain audit, the focused accessibility revision audit, focused PDF builds, objective delivery, goal completion, LHTG/DVRS, TFR, the roadmap audit, human-expert packet readiness, and package consistency. The multi-seed open-data evaluator-stress pilot is reproducible as mixed but narrowly positive aggregate evidence (25 paired selections, delta +0.001569), not top-conference empirical sufficiency.
