# Clean-Clone Reproducibility Audit

Audit date: 2026-06-01

Repository source:

- URL: `https://github.com/heguanghui54/ai-research-repro.git`
- Branch: `codex/co-pilot-ai-scientist-v3`
- Commit: `6dfbdc8ee3fef693bdb6ee01910a901fe8e35de1`
- Clean clone path used for audit: `/tmp/copilot-v3-clean-clone`

## Commands Run

```bash
rm -rf /tmp/copilot-v3-clean-clone
git clone --depth 1 --branch codex/co-pilot-ai-scientist-v3 \
  https://github.com/heguanghui54/ai-research-repro.git \
  /tmp/copilot-v3-clean-clone
cd /tmp/copilot-v3-clean-clone
python3 -m pip install -q -r requirements.txt
python3 scripts/audit_taste_insight_coverage.py
python3 scripts/audit_human_gate_attention_cost.py
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
skill = json.loads(Path("docs/co_pilot_ai_scientist_v3/audits/skill_reuse_smoke_audit.json").read_text())
assert taste["gate_records_audited"] == 18
assert taste["complete_taste_insight_records"] == 1
assert attention["gate_records_audited"] == 18
assert attention["complete_attention_cost_logs"] == 0
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
| Skill reuse smoke audit reran | Pass |
| English and Chinese PDFs rebuilt | Pass |
| Manifest artifacts found | Pass: 266/266 |
| Missing manifest artifacts | 0 |
| Taste/insight gate records audited | 18 |
| Complete taste/insight records | 1 |
| Attention-cost gate records audited | 18 |
| Complete attention-cost records | 0 |

## Interpretation

This clean-clone audit verifies that the pushed GitHub branch contains a
self-contained reproducibility package for the current pilot artifacts. A fresh
clone can rebuild the bilingual PDFs, rerun the gate-coverage audits, and find
every artifact listed in the reproducibility manifest.

This audit does not rerun the remote Ubuntu experiments or prove the central
performance claims. It strengthens the artifact-delivery and reproducibility
portion of the objective. It also verifies the reusable skill at the template/schema smoke-test level, while the top-conference evidence gaps remain:
multi-task matched-budget experiments, a full paper-generating trajectory,
prospective human attention-cost measurement, and downstream tests of
taste-gated high-tail outcomes.
