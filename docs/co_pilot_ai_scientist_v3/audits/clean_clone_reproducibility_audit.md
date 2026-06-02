# Clean-Clone Reproducibility Audit

Audit date: 2026-06-02

Repository source:

- URL: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `c2d3beefe05cbe7b5611843fd8ed9ca427bd9a94`
- Clean clone path used for audit: `/tmp/copilot-v3-clean-clone-c2d3beefe`
- Clone mode: shallow depth-1 single-branch clone

## Commands Run

```bash
rm -rf /tmp/copilot-v3-clean-clone-c2d3beefe
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 \
  https://github.com/heguanghui54/ai-research-repro.git \
  /tmp/copilot-v3-clean-clone-c2d3beefe
cd /tmp/copilot-v3-clean-clone-c2d3beefe
python3 -m pip install -q -r requirements.txt
python3 scripts/run_delayed_value_candidate_frontier_validation.py \
  --per-label 4 --citation-limit 15 --frontier-terms 20
python3 scripts/audit_temporal_frontier_replay.py
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 - <<'PY'
# Validate manifest coverage, candidate-frontier validation metrics,
# Temporal Frontier Replay audit status, and focused PDF rebuilds.
PY
```

## Result

| Check | Result |
| --- | --- |
| GitHub branch shallow-cloned from scratch | Pass |
| Checked-out commit | `c2d3beefe05cbe7b5611843fd8ed9ca427bd9a94` |
| Python dependencies installed from `requirements.txt` | Pass |
| Candidate-frontier validation reran | Pass |
| Temporal Frontier Replay audit reran | Pass |
| Focused English and focused Chinese PDFs rebuilt | Pass |
| Manifest artifacts found | Pass: 612/612 |
| Missing manifest artifacts | 0 |
| Candidate-frontier attempted reviews | 16 |
| Candidate-frontier scored reviews | 13 |
| Not scored after title-overlap match-drift guard | 3 |
| Delayed-candidate mean review signal | 0.24 |
| Control mean review signal | 0.176 |
| Delayed minus control mean score | 0.064 |
| Temporal Frontier Replay audit status | `pass_with_negative_delayed_value_evidence` |
| Focused English PDF bytes | 32051 |
| Focused Chinese PDF bytes | 60383 |

## Interpretation

This clean-clone audit verifies that the pushed GitHub branch at commit
`c2d3beefe05cbe7b5611843fd8ed9ca427bd9a94` contains the candidate-frontier
validation addition and can reproduce the current TFR-focused artifact set from
a fresh shallow clone. The clean clone reran the OpenAlex-backed validation,
regenerated the TFR audit, rebuilt the focused bilingual PDFs, and found all
612 artifacts listed in the reproducibility manifest.

The result is useful but bounded. The candidate-frontier validation gives a
weak positive screening signal: delayed-value replay candidates score 0.064
above controls against citation-derived frontier terms after a title-overlap
match-drift guard. This supports using the replay queue to prioritize future
TFR runs. It does not prove a positive delayed-value case, because full TFR
still requires paper-only, review-guided, and shuffled-review controls plus
semantic or human future-frontier judgement.

This audit does not rerun remote Ubuntu experiments, independent human review
collection, full-paper PDF rebuilds, or broad benchmark suites. The remaining
top-conference gaps are independent human expert ratings, broader matched
autonomous versus human-gated runs, and validated future-frontier alignment
cases.
