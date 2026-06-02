# Review Insight Taxonomy Probe

- Run ID: `review_insight_taxonomy_probe_20260602_064500`
- Timestamp UTC: `2026-06-02T05:22:48Z`
- Model: `gpt-4o-mini`
- Review cases: `32`
- Live model calls: `1`

## Scope

Finite OpenReview sample used to identify which human review comments are actionable as scientific taste/insight for IGRE gates.

## Taxonomy

| Category | Actionability | Primary gate | Useful signal |
| --- | ---: | --- | --- |
| Clarity Issues | 4 | structured_feedback | Indicates areas where the manuscript needs clearer explanations or better organization. |
| Novelty Concerns | 5 | scientific_taste_prior | Highlights whether the research direction is worth pursuing or if it overlaps significantly with existing work. |
| Limitations and Weaknesses | 5 | claim_calibration | Identifies areas where the claims made in the paper may be overstated or unsupported. |
| Metric and Evaluation Issues | 4 | evaluator_stress_test | Indicates potential weaknesses in the evaluation framework that could undermine the results. |
| Suggestions for Improvement | 3 | structured_feedback | Offers actionable suggestions that can enhance the clarity and quality of the manuscript. |

## Most Useful Categories

- Clarity Issues
- Novelty Concerns
- Limitations and Weaknesses

## Workflow Rules

- `structured_feedback`: Prioritize addressing clarity issues in the manuscript. (Improving clarity enhances the overall understanding and impact of the research.)
- `claim_calibration`: Ensure that limitations are clearly stated and discussed. (Acknowledging limitations strengthens the credibility of the research and helps set realistic expectations.)

## Claim Boundary

Claims made in the paper should be supported by robust evidence and clearly articulated limitations to avoid overstating the contributions.

This taxonomy is model-routed and derived from a finite OpenReview
sample. It identifies actionable review patterns for workflow design;
it does not prove that any single category improves final paper quality.
