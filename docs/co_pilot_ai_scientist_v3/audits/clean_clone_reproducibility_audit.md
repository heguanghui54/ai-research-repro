# Clean-Clone Reproducibility Audit

Audit date: 2026-06-02

Repository source:

- URL: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `8d83909e20f0ab4a20389971b0b448cfe852ee74`
- Clean clone path used for audit: `/tmp/copilot-v3-clean-clone-8d83909e`
- Clone mode: shallow depth-1 single-branch clone

## Commands Run

```bash
rm -rf /tmp/copilot-v3-clean-clone-8d83909e
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 \
  https://github.com/heguanghui54/ai-research-repro.git \
  /tmp/copilot-v3-clean-clone-8d83909e
cd /tmp/copilot-v3-clean-clone-8d83909e
git rev-parse HEAD
git status --short
python3 -m pip install -q -r requirements.txt
python3 scripts/audit_taste_insight_coverage.py
python3 scripts/audit_human_gate_attention_cost.py
python3 scripts/audit_temporal_frontier_replay.py
python3 scripts/build_human_copilot_trace_dataset.py
python3 scripts/audit_human_copilot_trace_dataset.py
python3 scripts/validate_copilot_skill.py
python3 scripts/build_copilot_v3_pdfs.py --language both
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 - <<'PY'
# Validate manifest coverage, gate audits, trace audit, skill smoke,
# structured-feedback artifact, citation-frontier artifact, metric-gaming
# evaluator-stress artifact, live-skill artifact, and four PDFs.
PY
```

## Result

| Check | Result |
| --- | --- |
| GitHub branch shallow-cloned from scratch | Pass |
| Checked-out commit | `8d83909e20f0ab4a20389971b0b448cfe852ee74` |
| Python dependencies installed from `requirements.txt` | Pass |
| Taste/insight coverage audit reran | Pass |
| Attention-cost audit reran | Pass |
| Human co-pilot trace dataset rebuilt and audited | Pass |
| Skill reuse smoke audit reran | Pass |
| English and Chinese PDFs rebuilt | Pass |
| Focused English and focused Chinese PDFs rebuilt | Pass |
| Structured-feedback probe artifact present | Pass |
| Single-gate artifact ablation present | Pass |
| Expanded citation-backed frontier probe artifact present | Pass |
| Review-frontier signal probe artifact present | Pass |
| Semantic frontier judge probe artifact present | Pass |
| Temporal Frontier Replay method text and operational audit present | Pass |
| Metric-gaming evaluator-stress smoke present | Pass |
| Live skill invocation smoke present | Pass |
| Manifest artifacts found | Pass: 594/594 |
| Missing manifest artifacts | 0 |
| Taste/insight gate records audited | 39 |
| Complete taste/insight records | 2 |
| Attention-cost gate records audited | 39 |
| Complete attention-cost records | 1 |
| Human trace gate records | 52 |
| Human trace commit-index entries | 1 |
| Human trace secret-pattern hits | 0 |
| Human trace raw-log marker hits | 0 |
| Structured-feedback recommendation | `structured` |
| Structured-feedback live model calls | 5 |
| Single-gate best mean condition | `single_evaluator_stress_test` |
| Single-gate best-single minus baseline | 0.7501 |
| Single-gate full-review minus best-single | -0.1667 |
| Expanded citation probe papers | 6 |
| Expanded citation probe relevance-filtered citations | 80 |
| Expanded citation probe delayed-value cases | 0 |
| Expanded citation probe short-term-positive/long-term-negative cases | 3 |
| Review-frontier signal snippets | 16 |
| Review-frontier signal review beats paper-context cases | 0 |
| Review-frontier signal latent delayed-value candidates | 0 |
| Semantic judge successful judgements | 5 |
| Semantic judge paper-context wins | 4 |
| Semantic judge review-guided artifact wins | 1 |
| Semantic judge delayed-value candidates | 0 |
| Temporal Frontier Replay audit status | `pass_with_negative_delayed_value_evidence` |
| Metric-gaming primary-only winner | `metric_gaming_all_negative` |
| Metric-gaming evaluator-stress winner | `guardrailed_utility_model` |
| Metric-gaming incidents reduced | 1 |
| Live skill status | `pass` |
| Live skill manifest gate count | 5 |
| Live skill logged gate type | `scientific_taste_prior` |
| English PDF bytes | 51757 |
| Chinese PDF bytes | 114561 |
| Focused English PDF bytes | 26972 |
| Focused Chinese PDF bytes | 48975 |
| Generated files byte-identical after rebuild | No: derived trace-dataset audit files and PDFs were refreshed by rebuild scripts |

## Interpretation

This clean-clone audit verifies that the pushed GitHub branch at commit
`8d83909e20f0ab4a20389971b0b448cfe852ee74` contains a self-contained reproducibility package for the current
pilot artifacts. A fresh shallow clone can rebuild the bilingual PDFs and the
focused bilingual PDFs, rerun the gate-coverage audits, rebuild and audit the
derived Human Co-Pilot Trace Dataset, validate the reusable Codex skill, and
find all 594 artifacts listed in the reproducibility manifest. It also verifies
that the focused bilingual manuscripts and reusable skill contain the Temporal
Frontier Replay method text and operational audit, and that the structured-feedback probe,
single-gate artifact ablation, expanded six-paper citation-backed frontier
probe, review-frontier signal probe, and semantic frontier judge probe are
present and internally consistent. The refreshed audit also verifies the live
skill invocation smoke and the controlled
metric-gaming evaluator-stress smoke in which a primary-only fairness metric
selects `metric_gaming_all_negative`, while the evaluator-stress guardrail
selects `guardrailed_utility_model` and reduces one synthetic metric-gaming
incident.

The latest retrospective frontier probes should be read as a measurement
boundary rather than as positive proof of delayed-value human taste. The expanded
citation probe covers 6 historical papers and 80 relevance-filtered later
citations; it finds 0 delayed-value cases and 3 short-term-positive/long-term
negative cases. The review-frontier signal probe checks 16 review snippets and
finds 0 cases where review snippets beat paper context. The semantic judge probe
successfully judges 5 papers; paper context wins 4 times, the review-guided
artifact wins once, and delayed-value candidates remain 0. This supports the
paper's protocol-readiness claim and the negative evidence boundary: historical
peer-review data can be operationalized for temporal frontier tests, but this
pilot has not yet found a batch of reviews that were bad short-term and
frontier-leading long-term.

Because this run uses `--depth 1`, the trace dataset's commit index contains
only the checked-out commit. That is expected for this audit mode and does not
affect artifact presence or PDF rebuild reproducibility. The earlier full-history
audit checked a larger commit index; this updated audit prioritizes current
pushed-artifact reproducibility at `8d83909e`.

This audit does not rerun the remote Ubuntu experiments or prove the central
performance claims. It strengthens the artifact-delivery and reproducibility
portion of the objective. The top-conference evidence gaps remain: multi-task
matched-budget experiments, independent human paper-quality review, independent
human-subject timing, and downstream tests of taste-gated high-tail outcomes.
