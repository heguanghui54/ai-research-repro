# Scientific Taste and Insight Rubric

This rubric operationalizes the least quantifiable part of IGRE: human
scientific taste. It is not a replacement for benchmark metrics and should not
be treated as a complete reward model. Its purpose is to make qualitative human
judgment auditable enough to compare trajectories without pretending that
scientific taste is fully reducible to a scalar.

## When To Use It

Use this rubric at three IGRE gates:

- `scientific_taste_prior`: before expensive experiments, when choosing or
  rewriting hypotheses.
- `frontier_steering`: during search, when deciding whether to preserve a
  branch that is not metric-best.
- `claim_calibration`: after drafting, when deciding whether a result is worth
  a strong paper claim.

## Scoring

Each dimension is scored from `1` to `5`.

- `1`: weak or absent.
- `3`: plausible but ordinary.
- `5`: unusually strong; worth preserving even if early metrics are not best.

Scores are recorded with short rationales. The final `taste_insight_score`
should be reported as a descriptive audit value, not as the optimization target
for the agent.

## Dimensions

| Dimension | What It Asks | High Score Means |
| --- | --- | --- |
| `problem_depth` | Is the question conceptually deep rather than merely convenient? | The problem can reveal something general about automated science or scientific practice. |
| `novelty_potential` | Could this direction produce a non-obvious result? | The branch is not a minor benchmark tweak and could surprise a knowledgeable reviewer. |
| `mechanistic_value` | Would success or failure explain why a method works? | The trajectory can teach a reusable mechanism, not only improve a number. |
| `failure_informativeness` | Would a negative result still be useful? | Failure would expose an important boundary condition, evaluator flaw, or hidden assumption. |
| `benchmark_taste` | Is the evaluator well matched to the claim? | The benchmark is hard to game, claim-relevant, and not chosen only because it is easy. |
| `claim_significance` | If the result is positive, would the claim matter? | A modest metric gain could still support a meaningful scientific or systems insight. |
| `risk_asymmetry` | Is the upside worth the extra uncertainty or human attention? | The possible high-tail outcome is large enough to justify preserving the branch. |

## Gate Record Fields

Every prospective gate may include:

```json
{
  "taste_insight": {
    "rubric_version": "2026-06-02",
    "scores": {
      "problem_depth": 3,
      "novelty_potential": 4,
      "mechanistic_value": 4,
      "failure_informativeness": 5,
      "benchmark_taste": 3,
      "claim_significance": 4,
      "risk_asymmetry": 4
    },
    "taste_insight_score": 3.86,
    "qualitative_rationale": "Preserve this branch because the failure mode would clarify when human frontier steering harms average benchmark performance but reveals a stronger evaluator.",
    "non_metric_factors": [
      "scientific surprise",
      "failure value",
      "claim relevance"
    ]
  }
}
```

## Reporting Rule

A paper claim should never say "human taste improves performance" from this
rubric alone. The safe claims are:

- the human decision was recorded with explicit non-metric rationale;
- the decision changed the search frontier;
- the downstream trajectory can be compared against an autonomous baseline;
- high-tail outcomes should be analyzed separately from mean benchmark score.

This keeps IGRE distinct from generic co-pilot workflows: human taste is not
treated as approval, preference labeling, or post-hoc explanation. It is a
logged search prior whose value must be tested.
