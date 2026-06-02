# Preregistered Analysis Plan for Human Expert Blind Review

Packet ID: `human_expert_blind_review_packet_20260602_143000`

Status: prepared before independent human ratings are collected. This file is a
collection-coordinator artifact and should not be shown to reviewers before
they complete their blind scores, because it names the hidden conditions.

## Objective

Test whether paper-specific expert review guidance produces stronger
mini-paper artifacts than matched-length unrelated review context for the same
OpenReview-derived research cases.

The scientific point is narrower than "human feedback always helps." The
experiment asks which forms of human scientific taste and insight are useful
because they can be converted into better research artifacts: sharper problem
framing, more concrete methods, stronger evaluator stress tests, clearer
limitations, better claim calibration, or a more ambitious but defensible
research direction.

## Design

- Unit of comparison: six anonymized A/B pairs.
- Conditions: `review_guided` versus `context_control`.
- Rating design: within-rater paired judgment.
- Planned rater count: 3 to 5 ML/AI-experienced raters.
- Planned valid rows: at least 18 rows for the minimum 3-rater panel over 6
  pairs.
- Raters remain blind to the condition mapping. The coordinator must not inspect
  deblinded aggregate results until the planned rating batch is collected or all
  invited raters have declined.

## Primary Endpoints

1. Condition winner preference: `review_guided` wins, `context_control` wins,
   and ties after deblinding A/B labels.
2. Mean rubric delta: average score of the `review_guided` side minus the
   comparator side, where each side score is the mean of the six rubric fields.

## Secondary Endpoints

- Per-field deltas for problem framing, method specificity, experiment design,
  limitation honesty, claim calibration, and overall quality.
- Inter-rater agreement over A/B/tie winner choices.
- Qualitative rationale themes, especially whether raters cite concrete
  methodological insight, evaluator pressure, novelty/taste, limitation
  honesty, or merely surface writing quality.

## Validity Rules

- A row is invalid if `pair_id` is unknown, `winner` is missing or not one of
  `A`, `B`, `tie`, or any required rubric score is outside the 1-5 range.
- Invalid rows are excluded before deblinded statistical interpretation.
- Ties are retained for win-rate reporting and inter-rater agreement, but
  excluded from the exact binomial win test.
- Free-text rationales are used only for thematic diagnosis, not to change the
  primary endpoint after collection.

## Statistical Reporting

Use `scripts/summarize_human_expert_blind_reviews.py` to report:

- condition win counts and win rates,
- condition mean scores,
- review-guided minus comparator mean delta with bootstrap confidence interval,
- two-sided exact binomial test for review-guided wins versus comparator wins,
  excluding ties,
- Fleiss' kappa over A/B/tie choices when enough balanced votes exist.

The minimum positive evidence threshold is:

- at least 3 independent raters,
- at least 18 valid rows,
- a positive review-guided mean delta whose bootstrap confidence interval does
  not include 0, or a clear directional win signal in the exact binomial test,
- qualitative rationales that mostly attribute the preference to research
  substance rather than surface fluency.

If these thresholds are not met, report the result as evaluation readiness or
mixed evidence, not as human-validated improvement.

## Useful Taste and Insight Signals

Human review comments count as useful IGRE signals only when they can change at
least one downstream research-control decision:

- Scientific taste prior: reframes the research question, identifies a more
  important failure mode, or makes a high-upside direction more plausible.
- Method-specific insight: proposes a concrete algorithmic, modeling, data, or
  systems change.
- Evaluator stress test: points to a missing baseline, metric, ablation,
  dataset split, robustness check, or failure analysis.
- Structured-feedback signal: improves the organization of evidence so the
  contribution becomes easier to evaluate.
- Claim calibration: narrows, qualifies, or strengthens claims so that the paper
  becomes more honest and defensible.

Comments that only say "interesting," "unclear," "needs more experiments," or
"writing should improve" without actionable direction are coded as low-utility
signals. They may explain reviewer perception, but they should not be treated as
the core human taste/insight mechanism of IGRE.

## Claim Boundary

A positive result would support the claim that paper-specific expert review
signals can guide better regenerated paper artifacts than equal amounts of
unrelated review context. It would not prove that Co-Pilot AI Scientist v3
outperforms autonomous AI Scientist-v2, that all human involvement is
beneficial, or that benchmark performance improves.
