# Focused Paper Quality Review Summary

Review date: 2026-06-02

Manuscript reviewed:

- `docs/co_pilot_ai_scientist_v3/paper_en_focused.md`

Reviewer routes:

- Monica OpenAI-compatible `gpt-4o-mini`
- Monica OpenAI-compatible `claude-3-7-sonnet-latest`

## Aggregate Verdict

The refreshed focused review includes the controlled metric-gaming smoke and the
archived FML-Bench `Fairness_fairlearn` evaluator-stress replay. The added FML
replay strengthens the evaluator-gate design evidence, but it does not change
the central readiness conclusion: the paper is still a strong pilot and
reproducibility package rather than a top-conference-ready systems paper.

| Reviewer | Recommendation | Novelty | Rigor | Clarity | Evidence | Reproducibility | Significance |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | Weak accept | 4 | 3 | 4 | 3 | 3 | 4 |
| `claude-3-7-sonnet-latest` | Weak reject | 3 | 2 | 2 | 1 | 3 | 3 |

## What Improved

- The paper now gives IGRE a distinct five-gate architecture instead of reading
  as a direct collage of AI Co-Scientist, AI Scientist-v2, and AlphaEvolve.
- Human scientific taste is framed as a high-variance search operator whose
  value must be measured, not assumed.
- The new FML Fairness evaluator-stress replay shows a real archived benchmark
  failure mode: primary-only selection chooses a degenerate all-negative
  predictor, while the gate rejects metric gaming and aborts no-valid
  continuation.
- OpenReview evidence is more carefully bounded as offline taste/insight proxy
  data, with equal-context ablation and cross-model review caveats.
- Negative short-budget FML outcomes are reported as design pressure for gate
  selection rather than hidden.

## Remaining Blocking Issues

- The primary empirical evidence is still mixed or negative for broad
  human-gated superiority: FML Causality packages favor autonomous baselines,
  Fairness has no valid co-pilot continuation, and frontier-alignment probes do
  not yet find delayed-value cases.
- Regenerated artifact comparisons still rely on model-routed scoring; the
  preregistered blind human expert packet has zero completed human rows.
- The manuscript is structurally overloaded, mixing architecture, review mining,
  benchmark pilots, retrospective frontier alignment, micro-evolution, fairness
  replay, and audit tooling.
- The OpenReview-derived taste/insight classifier has not been validated against
  independent expert labels.
- Benchmark coverage and matched-budget sample size remain too narrow for a
  strong systems claim.

## Next Required Evidence

1. Collect the planned blind human expert ratings and report inter-rater
   agreement.
2. Run more matched autonomous versus human-gated trajectories across at least
   three tasks and multiple seeds.
3. Add a formal gate-structure ablation: no-gate, single-gate, random-gate, and
   full IGRE.
4. Rewrite the paper around one primary falsifiable contribution, with secondary
   probes moved to supporting evidence.
5. Keep the safest claim at workflow architecture, logging protocol, and
   measurement-readiness level until stronger evidence exists.
