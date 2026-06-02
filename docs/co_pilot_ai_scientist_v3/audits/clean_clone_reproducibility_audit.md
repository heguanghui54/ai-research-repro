# Clean-Clone Reproducibility Audit

Audit date: 2026-06-02

Repository source:

- URL: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `b06933c319f1f86521fb66b29a04c308096ba0d0`
- Clean clone path used for audit: `/tmp/copilot-v3-clean-clone-latest`

## Commands Run

```bash
rm -rf /tmp/copilot-v3-clean-clone-latest
git clone --depth 1 --branch codex/co-pilot-ai-scientist-v3 \
  https://github.com/heguanghui54/ai-research-repro.git \
  /tmp/copilot-v3-clean-clone-latest
cd /tmp/copilot-v3-clean-clone-latest
python3 -m pip install -q -r requirements.txt
python3 scripts/audit_taste_insight_coverage.py
python3 scripts/audit_human_gate_attention_cost.py
python3 scripts/build_human_copilot_trace_dataset.py
python3 scripts/audit_human_copilot_trace_dataset.py
python3 scripts/validate_copilot_skill.py
python3 scripts/build_copilot_v3_pdfs.py --language both
# Commit-index verification requires full Git history rather than a shallow clone.
git fetch --unshallow
python3 scripts/build_human_copilot_trace_dataset.py
python3 scripts/audit_human_copilot_trace_dataset.py
python3 - <<'PY'
import json
from pathlib import Path

root = Path(".")
manifest = json.loads(Path("docs/co_pilot_ai_scientist_v3/repro_manifest.json").read_text())
missing = [artifact for artifact in manifest["current_artifacts"] if not (root / artifact).exists()]
assert not missing, missing

taste = json.loads(Path("docs/co_pilot_ai_scientist_v3/audits/taste_insight_coverage_audit.json").read_text())
attention = json.loads(Path("docs/co_pilot_ai_scientist_v3/audits/human_gate_attention_cost_audit.json").read_text())
trace = json.loads(Path("docs/co_pilot_ai_scientist_v3/audits/human_copilot_trace_dataset_audit.json").read_text())
skill = json.loads(Path("docs/co_pilot_ai_scientist_v3/audits/skill_reuse_smoke_audit.json").read_text())
assert taste["gate_records_audited"] == 39
assert taste["complete_taste_insight_records"] == 2
assert attention["gate_records_audited"] == 39
assert attention["complete_attention_cost_logs"] == 1
assert trace["status"] == "pass"
assert trace["counts"]["gate_records"] == 52
assert trace["counts"]["commit_index_entries"] == 58
assert trace["counts"]["secret_pattern_hits"] == 0
assert trace["counts"]["raw_log_marker_hits"] == 0
assert skill["overall_status"] == "pass"
assert skill["required_terms_present"] == 9

for pdf in [
    Path("docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_en.pdf"),
    Path("docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_zh.pdf"),
]:
    assert pdf.exists() and pdf.stat().st_size > 1000, pdf
PY
```

## Result

| Check | Result |
| --- | --- |
| GitHub branch cloned from scratch | Pass |
| Python dependencies installed from `requirements.txt` | Pass |
| Taste/insight coverage audit reran | Pass |
| Attention-cost audit reran | Pass |
| Human co-pilot trace dataset rebuilt and audited | Pass |
| Skill reuse smoke audit reran | Pass |
| English and Chinese PDFs rebuilt | Pass |
| Manifest artifacts found | Pass: 409/409 |
| Missing manifest artifacts | 0 |
| Manifest status | `pilot_package_with_attention_taste_priority_gate` |
| Taste/insight gate records audited | 39 |
| Complete taste/insight records | 2 |
| Attention-cost gate records audited | 39 |
| Complete attention-cost records | 1 |
| Human trace gate records | 52 |
| Human trace commit-index entries | 58 |
| Human trace secret-pattern hits | 0 |
| Human trace raw-log marker hits | 0 |
| English PDF bytes | 40706 |
| Chinese PDF bytes | 88743 |

## Interpretation

This clean-clone audit verifies that the pushed GitHub branch at commit
`b06933c319f1f86521fb66b29a04c308096ba0d0` contains a self-contained
reproducibility package for the current pilot artifacts. A fresh clone can
rebuild the bilingual PDFs, rerun the gate-coverage audits, rebuild and audit
the derived Human Co-Pilot Trace Dataset, validate the reusable Codex skill, and
find all 409 artifacts listed in the reproducibility manifest.

This audit does not rerun the remote Ubuntu experiments or prove the central
performance claims. It strengthens the artifact-delivery and reproducibility
portion of the objective. It also verifies that the new operator-recorded
attention/taste priority gate is present in the pushed repository and appears in
strict gate coverage audits: 1 complete attention-cost record and 2 complete
taste/insight records. The top-conference evidence gaps remain: multi-task
matched-budget experiments, independent human paper-quality review, independent
human-subject timing, and downstream tests of taste-gated high-tail outcomes.
