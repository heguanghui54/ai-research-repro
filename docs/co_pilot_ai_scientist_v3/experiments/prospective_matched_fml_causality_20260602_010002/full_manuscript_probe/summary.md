# Matched Full-Manuscript Generation Probe

This probe generates two full paper-shaped manuscripts from the same
prospective FML matched-budget package. It is archived-evidence manuscript
generation, not a fresh end-to-end research trajectory.

## Artifacts

- Co-pilot full manuscript: `docs/co_pilot_ai_scientist_v3/experiments/prospective_matched_fml_causality_20260602_010002/full_manuscript_probe/co_pilot_full_manuscript.md`
- Autonomous full manuscript: `docs/co_pilot_ai_scientist_v3/experiments/prospective_matched_fml_causality_20260602_010002/full_manuscript_probe/autonomous_full_manuscript.md`
- JSON audit: `docs/co_pilot_ai_scientist_v3/experiments/prospective_matched_fml_causality_20260602_010002/full_manuscript_probe/summary.json`

## Deterministic Rubric

| Variant | Overall | Completeness | Evidence | Calibration | Method distinctness | Metric strength |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IGRE/co-pilot | 4.18 | 5.00 | 5.00 | 3.90 | 4.20 | 2.80 |
| Autonomous baseline | 4.00 | 5.00 | 4.45 | 3.36 | 3.20 | 4.00 |

## Interpretation

The co-pilot manuscript has stronger method distinctness and explicit taste/attention logging, while the autonomous manuscript has the stronger scalar FML result. This supports a manuscript-generation and claim-calibration capability, not a top-conference superiority claim.

## Limits

- Generated from archived evidence rather than a fresh online end-to-end trajectory.
- Deterministic rubric is an internal audit aid, not independent peer review.
- Single FML task, one model family, one short budget, and one human gate.
- Does not prove that human gates improve paper quality or benchmark performance.
