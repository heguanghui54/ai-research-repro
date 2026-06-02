# Quickstart

## 1. Validate The Release

```bash
cd release/co-pilot-ai-scientist-v3-skill
python3 scripts/validate_release.py
```

Expected output:

```json
{
  "status": "pass"
}
```

## 2. Start With A Toy Task

Use `examples/toy_task_spec.md` as the first task. It is intentionally small so
the first run can produce a gate log within minutes.

Ask Codex:

```text
Use the co-pilot-ai-scientist-v3 skill on examples/toy_task_spec.md.
Create one scientific_taste_prior gate and one claim_calibration gate.
```

## 3. Save A Gate Log

Copy `templates/human_gate_log_template.json` into your run folder and fill:

- `gate_id`
- `gate_type`
- `research_task_id`
- `options`
- `human_decision`
- `rationale`
- `attention_cost`
- `taste_insight`

## 4. Keep Claims Narrow

A successful quickstart proves only that the skill can be installed and used to
generate auditable gate artifacts. It does not prove that human-gated research
beats autonomous research.
