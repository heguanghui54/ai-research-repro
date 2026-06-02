# Temporal Frontier Replay Operational Spec

## Purpose

Temporal Frontier Replay (TFR) is the offline evaluation and learning module of
IGRE. It tests whether historical human review comments can steer an automated
research workflow toward later field trajectories, rather than merely improving
local paper quality.

TFR is designed for the central high-variance claim of Co-Pilot AI Scientist v3:
human scientific taste can be valuable even when it does not improve the
immediate artifact. The important signal is whether a human comment changes the
search direction toward a later high-value frontier.

TFR is executed under IGRE's Long-Horizon Taste Gate (LHTG). LHTG is a
cross-gate routing policy, not a sixth approval gate. It looks for
Delayed-Value Review Signals (DVRS): review or human-gate interventions that
combine short-term friction with long-horizon directionality. LHTG routes the
actionable part of a candidate signal into one of the five IGRE gates and then
uses TFR to test whether that routing would have improved later-frontier
alignment.

## Inputs

Each replay unit is a historical tuple:

- `paper_t`: paper title, abstract, and optionally body available at submission
  time `t`;
- `reviews_t`: peer-review text, ratings, and decisions available at time `t`;
- `frontier_t_plus_delta`: later field evidence, reconstructed from citations,
  later influential papers, benchmark adoption, method families, or expert
  descriptors after time `t + delta`.

## Replay Conditions

TFR requires at least three matched conditions:

1. `paper_only`: the automated researcher sees only the historical paper
   context.
2. `review_guided`: the automated researcher sees the same paper context plus
   real reviews from the paper.
3. `shuffled_review_control`: the automated researcher sees the same paper
   context plus matched unrelated reviews from other papers.

The optional `future_oracle_upper_bound` condition may be used for headroom
analysis, but it is not a fair baseline.

## Scores

TFR separates immediate quality from later-frontier alignment.

- `short_term_score`: local artifact quality, benchmark fit, reviewer-style
  quality, or original-task score available without future information.
- `frontier_alignment_score`: alignment with later field evidence.
- `actionability_score`: whether the comment or artifact could have changed a
  concrete research plan at time `t`.
- `specificity_score`: whether the signal names methods, benchmarks,
  mechanisms, failure modes, or claim boundaries rather than generic advice.

The primary comparison is between `review_guided` and `paper_only`, with
`shuffled_review_control` used to detect generic reviewer-pressure effects.

## Delayed-Value Label

A replay unit is labeled `delayed_value_review_signal` only when all conditions
below hold:

1. `review_guided.short_term_score < paper_only.short_term_score`;
2. `review_guided.frontier_alignment_score > paper_only.frontier_alignment_score`;
3. `review_guided.frontier_alignment_score > shuffled_review_control.frontier_alignment_score`;
4. at least one responsible review snippet is actionable and specific;
5. the later-frontier evidence passes the match-drift guard.

This definition is intentionally strict. If review guidance improves both
short-term quality and future alignment, the case is positive but not delayed
value. If review guidance improves short-term quality while reducing future
alignment, the case is a `short_term_positive_long_term_negative` failure mode.

## LHTG Routing Rule

For each candidate review or human intervention, LHTG records:

- `short_term_friction`: low rating, rejection, missing evidence, unclear
  claims, failed metric, or worse immediate artifact score;
- `long_horizon_directionality`: mechanism, theory, generalization, scaling,
  benchmark norm, method family, problem reframing, or failure mode that could
  plausibly matter after `t + delta`;
- `gate_route`: one of scientific taste prior, evaluator stress test,
  frontier steering, verifiable micro-evolution, or claim calibration;
- `validation_status`: untested candidate, short-term positive only,
  delayed-value positive, short-term-positive/long-term-negative, or harmful.

LHTG should prioritize expensive TFR replay for candidates with both
short-term friction and long-horizon directionality. It should downweight
comments that are merely positive, merely negative, or generic. A positive
human review is therefore not automatically a useful taste signal, and a
negative review is not automatically harmful.

## Aggregates

Every TFR run should report:

- paper count and usable-frontier paper count;
- retrieved or provided later-frontier evidence count;
- review-guided versus paper-only wins;
- review-guided versus shuffled-control wins;
- delayed-value case count;
- short-term-positive/long-term-negative case count;
- possible match-drift count;
- exact sign-test or binomial-test statistic over non-tie wins;
- qualitative taxonomy of useful and harmful review signals.

## Claim Boundary

TFR does not prove that reviewers predicted the future. It tests a narrower and
more useful proposition: whether historical review text contains reusable
directional signals that, when routed through a co-pilot automated-research
workflow, move generated artifacts toward later field trajectories.

Negative TFR evidence is valuable. If no delayed-value cases are found, the
paper should report that boundary directly and avoid claiming that human review
signals improve long-horizon discovery.
