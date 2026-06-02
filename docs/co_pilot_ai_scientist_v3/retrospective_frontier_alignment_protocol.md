# Retrospective Frontier Alignment Protocol

## Motivation

OpenReview and similar peer-review datasets are retrospective rather than live
co-pilot interaction traces. That limitation can be turned into an advantage:
because the reviewed papers are from the past, we can compare reviewer comments
against the later evolution of the research field.

The question is not whether a reviewer liked a paper. The question is whether a
review comment contained scientific taste or insight that, in hindsight, pointed
the work toward ideas that later became mainstream, influential, or technically
important.

## Core Hypothesis

Useful human scientific taste is the subset of review feedback that would have
changed the research trajectory toward a later high-value frontier. A comment is
high-utility if it points to a future-relevant problem framing, missing
experiment, architectural change, benchmark shift, theoretical mechanism,
failure mode, or claim boundary that later research made important.

## Experimental Unit

Each unit is a historical paper-review-future triple:

- `paper_t`: the submitted paper at time `t`;
- `reviews_t`: one or more peer reviews available at time `t`;
- `frontier_t_plus_delta`: later field trajectory or SOTA descriptors from
  time `t + delta`, where `delta` is typically 2 to 5 years.

For ML/AI work, examples of frontier descriptors include later influential
benchmarks, model families, training recipes, evaluation norms, safety or
robustness practices, scaling patterns, retrieval/fine-tuning methods, or
systems constraints that became standard after the original review.

## Conditions

Run the same automatic-research workflow under at least three conditions:

1. `paper_only`: title, abstract, and paper content from time `t`.
2. `review_guided`: same paper context plus reviews from time `t`.
3. `shuffled_review_control`: same paper context plus matched-length reviews
   from unrelated papers at time `t`.

Optional diagnostic condition:

4. `future_oracle_upper_bound`: paper context plus a short neutral descriptor
   of the later frontier. This is not a fair baseline, but it estimates how
   much headroom exists if the system were given the answer.

## Output Task

For each condition, ask the automatic-research workflow to produce one of:

- a revised research proposal,
- an experiment plan,
- a mini-paper,
- a next-paper abstract,
- or a concrete algorithmic direction.

The generated artifact must not receive post-`t` information except in the
optional oracle condition.

## Evaluation

Evaluate each artifact against `frontier_t_plus_delta` using a blinded rubric.
The judge should see the generated artifact and the later frontier descriptor,
but not the condition label.

Primary metric:

- Future-frontier alignment: does the artifact point toward concepts,
  experiments, mechanisms, or claims that became important later?

Secondary metrics:

- Actionability: could the suggestion have guided a real follow-up project at
  time `t`?
- Non-obviousness: is the suggestion more than a generic call for more
  experiments or clearer writing?
- Scientific risk calibration: does the artifact avoid overclaiming while still
  preserving a high-upside direction?
- Specificity: does it name concrete methods, benchmarks, ablations, or failure
  modes?

## Identifying Good Reviews

A review comment is labeled as a high-quality taste/insight signal when it has
all three properties:

1. It is actionable at time `t`.
2. It points toward a later frontier component in `frontier_t_plus_delta`.
3. It improves the generated artifact more than matched unrelated review
   context under the same workflow.

This separates real scientific taste from generic reviewing style. A comment
such as "needs more experiments" is weak unless it names the experiment whose
absence later became central. A comment that identifies a missing benchmark,
failure mode, scaling issue, data assumption, or mechanism that later becomes
important is strong.

## Analysis

Report:

- review-guided versus paper-only win counts;
- review-guided versus shuffled-review-control win counts;
- mean future-frontier alignment delta;
- exact binomial test over non-tie wins;
- qualitative taxonomy of the comments that drove future alignment;
- failure cases where reviews pushed the workflow away from the later frontier.

## Claim Boundary

This protocol does not prove that reviewers could have predicted the future in
a strong sense. It tests whether historical review comments contain reusable
directional signals that, when routed through an automatic-research workflow,
increase alignment with later field evolution. Positive results would support
IGRE's claim that human taste and insight should be treated as selective search
operators, not as generic preference labels.
