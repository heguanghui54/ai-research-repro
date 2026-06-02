# Clean-Clone Reproducibility Audit

Audit date: 2026-06-02

Repository source:

- URL: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `da140a8455cb2a195751aa66170ace61d7040d97`
- Clean clone path used for audit: `/tmp/copilot-v3-clean-clone-da140a845`
- Clone mode: shallow depth-1 single-branch clone

## Commands Run

```bash
rm -rf /tmp/copilot-v3-clean-clone-da140a845
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 \
  https://github.com/heguanghui54/ai-research-repro.git \
  /tmp/copilot-v3-clean-clone-da140a845
cd /tmp/copilot-v3-clean-clone-da140a845
python3 -m pip install -q -r requirements.txt
python3 scripts/run_delayed_value_review_candidate_mining.py
python3 scripts/audit_temporal_frontier_replay.py
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 - <<'PY'
# Validate manifest coverage, delayed-value candidate counts,
# Temporal Frontier Replay audit status, and focused PDF rebuilds.
PY
```

## Result

| Check | Result |
| --- | --- |
| GitHub branch shallow-cloned from scratch | Pass |
| Checked-out commit | `da140a8455cb2a195751aa66170ace61d7040d97` |
| Python dependencies installed from `requirements.txt` | Pass |
| Delayed-value candidate-mining script reran | Pass |
| Temporal Frontier Replay audit reran | Pass |
| Focused English and focused Chinese PDFs rebuilt | Pass |
| Manifest artifacts found | Pass: 608/608 |
| Missing manifest artifacts | 0 |
| Delayed-value replay candidates | 120 |
| Delayed-value candidate rate | 0.2537 |
| Long-horizon positive candidates | 84 |
| Short-term repair signals | 90 |
| Temporal Frontier Replay audit status | `pass_with_negative_delayed_value_evidence` |
| Focused English PDF bytes | 30528 |
| Focused Chinese PDF bytes | 58212 |

## Interpretation

This clean-clone audit verifies that the pushed GitHub branch at commit
`da140a8455cb2a195751aa66170ace61d7040d97` contains the delayed-value
candidate-mining addition and can reproduce the current TFR-focused artifact
set from a fresh shallow clone. The clean clone reran the new candidate-mining
script, regenerated the TFR audit, rebuilt the focused bilingual PDFs, and
found all 608 artifacts listed in the reproducibility manifest.

The result preserves the paper's evidence boundary. The candidate-mining screen
finds 120 reviews worth expensive TFR replay, but the TFR audit status remains
`pass_with_negative_delayed_value_evidence`: no validated delayed-value human
review signal is claimed yet. Candidate mining is therefore a replay
prioritization mechanism, not positive long-horizon evidence.

This audit is intentionally narrower than earlier clean-clone audits: it checks
the newly added delayed-value candidate-mining path and the focused paper
artifacts. It does not rerun remote Ubuntu experiments, independent human
review collection, full-paper PDF rebuilds, or broad benchmark suites. The
remaining top-conference gaps are independent human expert ratings, broader
matched autonomous versus human-gated runs, and validated future-frontier
alignment cases.
