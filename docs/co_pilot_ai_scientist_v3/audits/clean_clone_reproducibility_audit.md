# Clean-Clone Reproducibility Audit

Audit date: 2026-06-02

Repository source:

- URL: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `23f346e618e4f03b45e9d199efbc6b40e6ceff46`
- Clean clone path used for audit: `/tmp/copilot-v3-clean-clone-23f346e61`
- Clone mode: shallow depth-1 single-branch clone

## Commands Run

```bash
rm -rf /tmp/copilot-v3-clean-clone-23f346e61
git clone --depth 1 --single-branch --branch codex/co-pilot-ai-scientist-v3 \
  https://github.com/heguanghui54/ai-research-repro.git \
  /tmp/copilot-v3-clean-clone-23f346e61
cd /tmp/copilot-v3-clean-clone-23f346e61
git rev-parse HEAD
git status --short
python3 -m pip install -q -r requirements.txt
python3 scripts/audit_taste_insight_coverage.py
python3 scripts/audit_human_gate_attention_cost.py
python3 scripts/build_human_copilot_trace_dataset.py
python3 scripts/audit_human_copilot_trace_dataset.py
python3 scripts/validate_copilot_skill.py
python3 scripts/build_copilot_v3_pdfs.py --language both
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 - <<'PY'
# Validate manifest coverage, gate audits, trace audit, skill smoke,
# structured-feedback artifact, citation-frontier artifact, and four PDFs.
PY
```

## Result

| Check | Result |
| --- | --- |
| GitHub branch shallow-cloned from scratch | Pass |
| Checked-out commit | `23f346e618e4f03b45e9d199efbc6b40e6ceff46` |
| Python dependencies installed from `requirements.txt` | Pass |
| Taste/insight coverage audit reran | Pass |
| Attention-cost audit reran | Pass |
| Human co-pilot trace dataset rebuilt and audited | Pass |
| Skill reuse smoke audit reran | Pass |
| English and Chinese PDFs rebuilt | Pass |
| Focused English and focused Chinese PDFs rebuilt | Pass |
| Structured-feedback probe artifact present | Pass |
| Citation-backed frontier probe artifact present | Pass |
| Manifest artifacts found | Pass: 549/549 |
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
| Citation probe papers | 3 |
| Citation probe relevance-filtered citations | 13 |
| Citation probe possible match-drift papers | 1 |
| Citation probe delayed-value cases | 0 |
| English PDF bytes | 51757 |
| Chinese PDF bytes | 114561 |
| Focused English PDF bytes | 21090 |
| Focused Chinese PDF bytes | 35158 |

## Interpretation

This clean-clone audit verifies that the pushed GitHub branch at commit
`23f346e618e4f03b45e9d199efbc6b40e6ceff46` contains a self-contained reproducibility package for the current
pilot artifacts. A fresh shallow clone can rebuild the bilingual PDFs and the
focused bilingual PDFs, rerun the gate-coverage audits, rebuild and audit the
derived Human Co-Pilot Trace Dataset, validate the reusable Codex skill, and
find all 549 artifacts listed in the reproducibility manifest. It also verifies
that the structured-feedback probe and the three-paper citation-backed
frontier-alignment pilot are present and internally consistent.

Because this run uses `--depth 1`, the trace dataset's commit index contains
only the checked-out commit. That is expected for this audit mode and does not
affect artifact presence or PDF rebuild reproducibility. The earlier full-history
audit checked a larger commit index; this updated audit prioritizes current
pushed-artifact reproducibility at `23f346e61`.

This audit does not rerun the remote Ubuntu experiments or prove the central
performance claims. It strengthens the artifact-delivery and reproducibility
portion of the objective. The top-conference evidence gaps remain: multi-task
matched-budget experiments, independent human paper-quality review, independent
human-subject timing, and downstream tests of taste-gated high-tail outcomes.
