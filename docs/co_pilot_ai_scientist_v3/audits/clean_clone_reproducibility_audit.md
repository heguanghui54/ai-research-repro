# Clean-Clone Reproducibility Audit

Audit date: 2026-06-02

Repository source:

- URL: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `38dc8c8f7baecf85b47de3f1f45b14836b3d9ec4`
- Clean clone path used for audit: `/tmp/copilot-v3-clean-clone-38dc8c8f`
- Clone mode: shallow depth-1 single-branch clone

## Commands Run

```bash
rm -rf /tmp/copilot-v3-clean-clone-38dc8c8f
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 \
  https://github.com/heguanghui54/ai-research-repro.git \
  /tmp/copilot-v3-clean-clone-38dc8c8f
cd /tmp/copilot-v3-clean-clone-38dc8c8f
python3 -m pip install -q -r requirements.txt
python3 scripts/audit_long_horizon_taste_gate.py
python3 scripts/run_delayed_value_candidate_frontier_validation.py \
  --per-label 4 --citation-limit 15 --frontier-terms 20
python3 scripts/audit_temporal_frontier_replay.py
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 scripts/audit_package_consistency.py
python3 - <<'PY'
# Validate manifest coverage, LHTG/DVRS audit status,
# candidate-frontier validation metrics, TFR audit status,
# package consistency status, and focused PDF rebuilds.
PY
```

## Result

| Check | Result |
| --- | --- |
| GitHub branch shallow-cloned from scratch | Pass |
| Checked-out commit | `38dc8c8f7baecf85b47de3f1f45b14836b3d9ec4` |
| Python dependencies installed from `requirements.txt` | Pass |
| LHTG/DVRS audit reran | Pass |
| LHTG/DVRS audit status | `pass_with_no_positive_dvrs` |
| Delayed-value positive cases | 0 |
| Candidate-frontier validation reran | Pass |
| Temporal Frontier Replay audit reran | Pass |
| Focused English and focused Chinese PDFs rebuilt | Pass |
| Package consistency audit reran | Pass |
| Manifest artifacts found | Pass: 618/618 |
| Missing manifest artifacts | 0 |
| Candidate-frontier attempted reviews | 16 |
| Candidate-frontier scored reviews | 13 |
| Not scored after title-overlap match-drift guard | 3 |
| Delayed-candidate mean review signal | 0.24 |
| Control mean review signal | 0.176 |
| Delayed minus control mean score | 0.064 |
| Temporal Frontier Replay audit status | `pass_with_negative_delayed_value_evidence` |
| Package consistency audit status | `pass` |
| Focused English PDF bytes | 32998 |
| Focused Chinese PDF bytes | 61838 |

## Interpretation

This clean-clone audit verifies that the pushed GitHub branch at commit
`38dc8c8f7baecf85b47de3f1f45b14836b3d9ec4` contains the LHTG/DVRS audit package and can reproduce it from a
fresh shallow clone. The clean clone reran LHTG/DVRS audit, the OpenAlex-backed
candidate-frontier validation, regenerated the TFR audit, rebuilt the focused
bilingual PDFs, reran package consistency, and found all 618 artifacts listed
in the reproducibility manifest.

The result is useful but bounded. LHTG/DVRS is now operationalized and
clean-clone reproducible, but the archived evidence still contains 0 positive
delayed-value cases. The candidate-frontier validation gives only a weak
screening signal: delayed-value replay candidates score 0.064 above controls
against citation-derived frontier terms after a title-overlap match-drift guard.
This supports replay prioritization, not causal delayed-value proof.

This audit does not rerun remote Ubuntu experiments, independent human review
collection, full-paper PDF rebuilds, or broad benchmark suites. The remaining
top-conference gaps are independent human expert ratings, broader matched
autonomous versus human-gated runs, and validated future-frontier alignment
cases.
