# Clean-Clone Reproducibility Audit

Audit date: 2026-06-02

Repository source:

- URL: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `eb63cb4b5ea12636abbddf4bb92b2cc8957ea8f0`
- Clean clone path used for audit: `/tmp/copilot-v3-clean-clone-structured-feedback`

## Commands Run

```bash
rm -rf /tmp/copilot-v3-clean-clone-structured-feedback
git clone --branch codex/co-pilot-ai-scientist-v3 \
  https://github.com/heguanghui54/ai-research-repro.git \
  /tmp/copilot-v3-clean-clone-structured-feedback
cd /tmp/copilot-v3-clean-clone-structured-feedback
git rev-parse HEAD
git status --short
python3 -m pip install -q -r requirements.txt
python3 scripts/audit_taste_insight_coverage.py
python3 scripts/audit_human_gate_attention_cost.py
python3 scripts/build_human_copilot_trace_dataset.py
python3 scripts/audit_human_copilot_trace_dataset.py
python3 scripts/validate_copilot_skill.py
python3 scripts/build_copilot_v3_pdfs.py --language both
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
structured = json.loads(Path("docs/co_pilot_ai_scientist_v3/experiments/structured_feedback_probe_20260602_022900/summary.json").read_text())
assert manifest["status"] == "pilot_package_with_structured_feedback_probe"
assert len(manifest["current_artifacts"]) == 431
assert taste["gate_records_audited"] == 39
assert taste["complete_taste_insight_records"] == 2
assert attention["gate_records_audited"] == 39
assert attention["complete_attention_cost_logs"] == 1
assert trace["status"] == "pass"
assert trace["counts"]["gate_records"] == 52
assert trace["counts"]["commit_index_entries"] == 61
assert trace["counts"]["secret_pattern_hits"] == 0
assert trace["counts"]["raw_log_marker_hits"] == 0
assert skill["overall_status"] == "pass"
assert skill["required_terms_present"] == 9
assert structured["score"]["recommendation"] == "structured"
assert structured["live_model_calls"] == 5

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
| Structured-feedback probe artifact present | Pass |
| Manifest artifacts found | Pass: 431/431 |
| Missing manifest artifacts | 0 |
| Manifest status | `pilot_package_with_structured_feedback_probe` |
| Taste/insight gate records audited | 39 |
| Complete taste/insight records | 2 |
| Attention-cost gate records audited | 39 |
| Complete attention-cost records | 1 |
| Human trace gate records | 52 |
| Human trace commit-index entries | 61 |
| Human trace secret-pattern hits | 0 |
| Human trace raw-log marker hits | 0 |
| Structured-feedback recommendation | `structured` |
| Structured-feedback live model calls | 5 |
| English PDF bytes | 42638 |
| Chinese PDF bytes | 93750 |

## Interpretation

This clean-clone audit verifies that the pushed GitHub branch at commit
`eb63cb4b5ea12636abbddf4bb92b2cc8957ea8f0` contains a self-contained
reproducibility package for the current pilot artifacts. A fresh clone can
rebuild the bilingual PDFs, rerun the gate-coverage audits, rebuild and audit
the derived Human Co-Pilot Trace Dataset, validate the reusable Codex skill, and
find all 431 artifacts listed in the reproducibility manifest. This latest
clone also verifies that the `structured_feedback_probe_20260602_022900`
artifact is present and that its archived score recommends the structured
revision after five Monica-routed model calls.

This audit does not rerun the remote Ubuntu experiments or prove the central
performance claims. It strengthens the artifact-delivery and reproducibility
portion of the objective. It also verifies that the new operator-recorded
attention/taste priority gate is present in the pushed repository and appears in
strict gate coverage audits: 1 complete attention-cost record and 2 complete
taste/insight records. It further verifies the new structured-feedback
measurement probe as an artifact, but not as independent paper-quality evidence.
The top-conference evidence gaps remain: multi-task matched-budget experiments,
independent human paper-quality review, independent human-subject timing, and
downstream tests of taste-gated high-tail outcomes.
