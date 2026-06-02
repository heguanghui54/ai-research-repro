# Clean-Clone Reproducibility Audit

Audit date: 2026-06-02T18:27:11Z

Repository source:

- URL: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `42cf5897d45bb5cac3d5532c7391e97d2506251f`
- Clean clone path used for audit: `/tmp/copilot-v3-clean-clone-latest`
- Clone mode: shallow depth-1 single-branch clone

## Commands Run

```bash
rm -rf /tmp/copilot-v3-clean-clone-latest
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 https://github.com/heguanghui54/ai-research-repro.git /tmp/copilot-v3-clean-clone-latest
cd /tmp/copilot-v3-clean-clone-latest
git rev-parse HEAD
python3 -m pip install -q -r requirements.txt
python3 scripts/audit_long_horizon_taste_gate.py
python3 scripts/audit_temporal_frontier_replay.py
python3 scripts/audit_top_conference_evidence_roadmap.py
python3 scripts/audit_human_expert_blind_review_packet.py
python3 scripts/audit_benchmark_coverage.py
python3 scripts/audit_prospective_matched_budget_package.py
python3 scripts/summarize_prospective_matched_packages.py
python3 scripts/audit_global_skill_engineering_chain.py
python3 scripts/audit_focused_accessibility_revision.py
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 scripts/audit_objective_delivery.py
python3 scripts/audit_package_consistency.py
python3 - <<'PY'
# Validate manifest coverage, audit statuses, prospective package counts, and focused PDF rebuilds.
PY
```

## Result

| Check | Result |
| --- | --- |
| GitHub branch shallow-cloned from scratch | Pass |
| Checked-out commit | `42cf5897d45bb5cac3d5532c7391e97d2506251f` |
| Python dependencies installed from `requirements.txt` | Pass |
| LHTG/DVRS audit reran | Pass |
| LHTG/DVRS audit status | `pass_with_no_positive_dvrs` |
| Delayed-value positive cases | 0 |
| Temporal Frontier Replay audit reran | Pass |
| Temporal Frontier Replay audit status | `pass_with_negative_delayed_value_evidence` |
| Top-conference evidence roadmap audit reran | Pass |
| Human expert blind-review packet audit reran | Pass |
| Human expert blind-review packet audit status | `pass_prepared_no_human_ratings` |
| Benchmark coverage audit reran | Pass |
| Benchmark coverage audit status | `pass` |
| Open-data evaluator-stress pilot | Pass: 5 tasks, delta 0.014944, selection changed 1 time |
| MLAgentBench house-price setup status | `setup_blocked_by_missing_kaggle_cli_and_competition_consent` |
| Prospective matched-budget package audit reran | Pass |
| Prospective package audit status | `pass` |
| Prospective packages summarized | 6; co-pilot wins 3; autonomous/tie 3 |
| Global skill engineering chain audit reran | Pass |
| Global skill engineering chain status | `pass` (6/6 steps) |
| External clean skill reuse smoke | Pass: all six IGRE gates instantiated |
| Focused accessibility revision audit reran | Pass |
| Focused accessibility revision audit status | `pass` |
| Focused English/Chinese PDFs rebuilt | Pass |
| Package consistency audit reran | Pass |
| Objective delivery audit reran | Pass |
| Manifest artifacts found | Pass: 895/895 |
| Missing manifest artifacts | 0 |
| Candidate-frontier attempted reviews | 16 |
| Candidate-frontier scored reviews | 13 |
| Not scored after title-overlap match-drift guard | 3 |
| Delayed-candidate mean review signal | 0.24 |
| Control mean review signal | 0.176 |
| Delayed minus control mean score | 0.064 |
| Package consistency audit status | `pass` |
| Objective delivery audit status | `pass_artifact_delivery_with_empirical_gaps` |
| Focused English PDF bytes | 209536 |
| Focused Chinese PDF bytes | 253395 |

## Interpretation

A fresh shallow clone of the pushed branch at commit 42cf5897d reproduced the current verification package with 895/895 manifest artifacts present. It reran LHTG/DVRS, TFR, the roadmap audit, human-expert packet readiness, benchmark coverage, prospective matched-package audit and summary, the global skill engineering chain audit, the focused accessibility revision audit, focused PDF builds, package consistency, and objective delivery audits. The result supports artifact reproducibility, skill engineering transfer, open-data evaluator-stress auditability, and workflow auditability, not top-conference empirical sufficiency.

The result is bounded. It does not rerun remote Ubuntu experiments, collect independent human expert ratings, or prove top-conference empirical sufficiency. It verifies that the latest pushed verification pipeline is reproducible from a clean clone, that the reusable skill engineering chain passes 6/6 checks including an external clean-environment reuse smoke, that the open-data evaluator-stress package is present and audited, and that the package continues to report 0 positive delayed-value cases.
