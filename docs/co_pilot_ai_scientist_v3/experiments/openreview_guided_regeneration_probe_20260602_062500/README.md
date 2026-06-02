# OpenReview-Guided Regeneration Probe

- Run ID: `openreview_guided_regeneration_probe_20260602_062500`
- Timestamp UTC: `2026-06-02T05:20:52Z`
- Model: `gpt-4o-mini`
- Live model calls: `2`
- Selected papers: `3`
- Review-guided wins: `3`
- Baseline wins: `0`
- Ties: `0`
- Mean baseline overall: `3.0`
- Mean review-guided overall: `4.0`
- Mean delta: `1.0`

## Scope

Three selected ML/AI OpenReview papers are regenerated twice: from title/abstract only, and from title/abstract plus real OpenReview review comments as human scientific taste/insight. The comparison scores mini-paper artifacts only.

## Selected Papers

- `openreview_sample_1` | score=0.53125 | decision=True | Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback
- `openreview_sample_34` | score=0.8000000000000002 | decision=True | ​​What learning algorithm is in-context learning? Investigations with linear models
- `openreview_sample_49` | score=0.875 | decision=True | Unifying semi-supervised and robust learning by mixup

## Pairwise Results

- `openreview_sample_1` winner=`review_guided`; baseline overall=3; review-guided overall=4; effect=The review insights emphasized the importance of rejection mechanisms, enhancing the framing and clarity of the contribution.
- `openreview_sample_34` winner=`review_guided`; baseline overall=3; review-guided overall=4; effect=Reviewers highlighted the novelty and clarity of the approach, improving the overall presentation and understanding.
- `openreview_sample_49` winner=`review_guided`; baseline overall=3; review-guided overall=4; effect=The insights from reviewers helped clarify the significance of the problem and the need for further development.

## Design Lessons

- Incorporating reviewer insights can significantly enhance the clarity and depth of the research contribution.
- Addressing limitations transparently can improve the perceived reliability of the findings.
- Focusing on broader applicability in experiments can strengthen the overall impact of the research.

## Claim Boundary

The claims made in the review-guided versions are more nuanced and reflect a deeper understanding of the limitations and contexts of the proposed methods, enhancing their credibility.

This probe uses real review text as human scientific taste/insight,
but it regenerates paper-shaped artifacts only. It does not rerun the
original experiments or constitute independent peer review.
