# OpenReview-Guided Regeneration Probe

- Run ID: `openreview_guided_regeneration_probe_20260602_073500`
- Timestamp UTC: `2026-06-02T05:41:39Z`
- Model: `gpt-4o-mini`
- Live model calls: `2`
- Selected papers: `6`
- Review-guided wins: `5`
- Baseline wins: `1`
- Ties: `0`
- Mean baseline overall: `3.0`
- Mean review-guided overall: `3.8333`
- Mean delta: `0.8333`

## Scope

6 selected ML/AI OpenReview papers are regenerated twice: from title/abstract only, and from title/abstract plus real OpenReview review comments as human scientific taste/insight. The comparison scores mini-paper artifacts only.

## Selected Papers

- `openreview_sample_1` | score=0.53125 | decision=True | Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback
- `openreview_sample_2` | score=0.3 | decision=False | Forked Diffusion for Conditional Graph Generation
- `openreview_sample_17` | score=0.55 | decision=False | Knowledge Unlearning for Mitigating Privacy Risks in Language Models
- `openreview_sample_34` | score=0.8000000000000002 | decision=True | ​​What learning algorithm is in-context learning? Investigations with linear models
- `openreview_sample_49` | score=0.875 | decision=True | Unifying semi-supervised and robust learning by mixup
- `openreview_sample_64` | score=0.25 | decision=False | CausalAF: Causal Autoregressive Flow for Safety-Critical Scenes Generation

## Pairwise Results

- `openreview_sample_1` winner=`review_guided`; baseline overall=3; review-guided overall=4; effect=The review insights provided specific details on the empirical validation and the method's effectiveness, enhancing the overall quality.
- `openreview_sample_2` winner=`review_guided`; baseline overall=3; review-guided overall=4; effect=The insights clarified the motivation and versatility of the proposed method, improving clarity and depth.
- `openreview_sample_17` winner=`review_guided`; baseline overall=3; review-guided overall=4; effect=The review insights highlighted empirical guarantees and reproducibility, enhancing the paper's credibility.
- `openreview_sample_34` winner=`review_guided`; baseline overall=3; review-guided overall=4; effect=The insights provided clarity on the probe technique and the implications of the findings, enhancing overall understanding.
- `openreview_sample_49` winner=`review_guided`; baseline overall=3; review-guided overall=4; effect=The review insights emphasized the importance of the problem and suggested further exploration, enhancing the paper's impact.
- `openreview_sample_64` winner=`baseline`; baseline overall=3; review-guided overall=3; effect=The review insights did not significantly enhance the clarity or depth of the baseline regeneration.

## Design Lessons

- Incorporating reviewer insights can significantly enhance the quality of generated artifacts.
- Clarity and motivation in problem formulation are crucial for understanding.
- Empirical validation and reproducibility are key factors in establishing credibility.

## Claim Boundary

The findings and claims made in the review-guided regenerations are primarily relevant to their specific contexts and may not generalize to other domains or types of models.

This probe uses real review text as human scientific taste/insight,
but it regenerates paper-shaped artifacts only. It does not rerun the
original experiments or constitute independent peer review.
