# Focused Paper Quality Review Summary

- Status: `refreshed_after_model_blind_dry_run_integration`
- Review date: `2026-06-03`
- Paper path: `docs/co_pilot_ai_scientist_v3/paper_en_focused.md`

## Context Updates

- Focused paper now includes the model-only blind packet dry run negative result.
- Model-only blind packet dry run reports review-guided wins `0`, context-control wins `7`, tie `1`, and mean delta `-1.1458` over `8` parsed model score rows.
- Focused bilingual PDFs were rebuilt after adding this result.

## Current Successful Reviews

| Model | Recommendation | Novelty | Rigor | Clarity | Evidence | Reproducibility | Significance | Completion |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `gpt-4o-mini` | `Weak accept` | 4 | 3 | 4 | 3 | 3 | 4 | complete |
| `gemini-2.5-flash` | `Borderline` | 5 | 5 | 4 | 3 | 5 | 4 | complete |

## Failed Or Archived Routes

- `claude-3-7-sonnet-latest`: `504 Gateway Time-out`; retained but not counted as current successful review.
- `gemini-2.0-flash`: unsupported-model `412`; retained but not counted as current successful review.

## Aggregate Verdict

Current successful model reviews are one `Weak accept` and one `Borderline`. Both view IGRE/TFR as novel and reproducible, but both keep the work at pilot/method-and-measurement status because independent human ratings, broader matched benchmarks, and system-level superiority evidence remain missing.

## Claim Boundary

Model reviews are iteration evidence only. They do not replace independent human expert review, larger matched benchmark runs, or broad multi-researcher traces.
