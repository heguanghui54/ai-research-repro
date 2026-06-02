# Clean-Clone Reproducibility Audit

Audit date: 2026-06-02T11:38:00Z

Repository source:

- URL: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `7badd8f35a9208ae55a6fa6ea9393869fef897b2`
- Clean clone path used for audit: `/tmp/copilot-v3-clean-clone-latest`
- Clone mode: shallow depth-1 single-branch clone

## Commands Run

```bash
rm -rf /tmp/copilot-v3-clean-clone-latest
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 \
  https://github.com/heguanghui54/ai-research-repro.git \
  /tmp/copilot-v3-clean-clone-latest
cd /tmp/copilot-v3-clean-clone-latest
python3 -m pip install -q -r requirements.txt
python3 scripts/audit_long_horizon_taste_gate.py
python3 scripts/audit_temporal_frontier_replay.py
python3 scripts/audit_top_conference_evidence_roadmap.py
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 scripts/audit_objective_delivery.py || true
python3 scripts/audit_package_consistency.py || true
python3 scripts/audit_objective_delivery.py
python3 scripts/audit_package_consistency.py
python3 - <<'PY'
# Validate manifest coverage, audit statuses, and focused PDF rebuilds.
PY
```

## Result

| Check | Result |
| --- | --- |
| GitHub branch shallow-cloned from scratch | Pass |
| Checked-out commit | `7badd8f35a9208ae55a6fa6ea9393869fef897b2` |
| Python dependencies installed from `requirements.txt` | Pass |
| LHTG/DVRS audit reran | Pass |
| LHTG/DVRS audit status | `pass_with_no_positive_dvrs` |
| LHTG reusable workflow terms present | `True` |
| Delayed-value positive cases | 0 |
| Temporal Frontier Replay audit reran | Pass |
| Temporal Frontier Replay audit status | `pass_with_negative_delayed_value_evidence` |
| Top-conference evidence roadmap audit reran | Pass |
| Top-conference evidence roadmap audit status | `pass` |
| Focused English and focused Chinese PDFs rebuilt | Pass |
| Package consistency audit reran | Pass |
| Objective delivery audit reran | Pass |
| Manifest artifacts found | Pass: 629/629 |
| Missing manifest artifacts | 0 |
| Candidate-frontier attempted reviews | 16 |
| Candidate-frontier scored reviews | 13 |
| Not scored after title-overlap match-drift guard | 3 |
| Delayed-candidate mean review signal | 0.24 |
| Control mean review signal | 0.176 |
| Delayed minus control mean score | 0.064 |
| Package consistency audit status | `pass` |
| Objective delivery audit status | `pass_artifact_delivery_with_empirical_gaps` |
| Focused English PDF bytes | 32998 |
| Focused Chinese PDF bytes | 61838 |

## Interpretation

A fresh shallow clone of the pushed branch at commit `7badd8f35` reproduced
the current verification package with `629/629` manifest artifacts present. It
reran LHTG/DVRS, TFR, the top-conference evidence roadmap audit, focused
bilingual PDF builds, package consistency, and objective delivery audits. The
result supports artifact reproducibility and workflow auditability, not
top-conference empirical sufficiency.

The result is bounded. It does not rerun remote Ubuntu experiments, collect
independent human expert ratings, or prove top-conference empirical
sufficiency. It verifies that the latest pushed verification pipeline is
reproducible from a clean clone and that the package continues to report 0
positive delayed-value cases.
