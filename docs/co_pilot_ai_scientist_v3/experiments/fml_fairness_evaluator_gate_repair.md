# FML Fairness Evaluator-Gate Repair Probe

This probe follows up on `fml_fairness_gated_drafts_failed/`. The online
AI Scientist-v2 Fairness drafts failed validation because the generated code
violated Fairlearn/sklearn API contracts. We therefore ran an evaluator-gate
repair probe outside the agent loop to determine what a human gate should do
before allowing a Fairness branch to continue.

Metric: `abs_demographic_parity_diff_mean`, lower is better. However, the task
also reports accuracy and balanced accuracy, which are essential guardrails.

## Results

| Variant | Val DPD abs | Val balanced acc | Test DPD abs | Test balanced acc | Gate decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Original baseline | 0.186632 | 0.772576 | 0.173030 | 0.763862 | Runnable reference. |
| API-repaired fairness candidate | 0.331207 | 0.823329 | 0.317603 | 0.818491 | Runnable but worse on the target fairness metric. |
| Degenerate all-negative predictor | 0.000000 | 0.500000 | 0.000000 | 0.500000 | Reject despite perfect target metric; it games demographic parity by predicting one class. |

## Interpretation

This is not matched-budget performance evidence for human-gated search. It is
evaluator-gate evidence. The target metric alone can be optimized by a trivial
all-negative classifier, so the co-pilot gate should require executable code and
a minimum utility floor, for example balanced accuracy above a baseline-relative
threshold, before continuing or claiming a fairness improvement.

The result strengthens the system-design claim that human evaluator gates are
needed not only to choose promising branches, but also to prevent metric gaming
and API-incompatible branches from consuming budget.

## Artifact Paths

- Baseline: `fml_fairness_baseline_eval/`
- API-repaired candidate: `fml_fairness_repair_eval/`
- Degenerate metric-gaming candidate: `fml_fairness_degenerate_eval/`
- Failed online drafts: `fml_fairness_gated_drafts_failed/`
- JSON aggregate: `fml_fairness_evaluator_gate_repair_summary.json`
