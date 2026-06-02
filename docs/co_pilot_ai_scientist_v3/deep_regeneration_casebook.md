# Deep Regeneration Casebook

This casebook turns the OpenReview replay evidence from aggregate win counts
into inspectable paper-level cases. Its purpose is to make the experiment
section more concrete under the current budget: a broad mini-paper screen can
select cases, but a convincing human-AI co-science paper should also show a few
deep replays with the original paper, the actual human reviews, the regenerated
artifact, the experiment data, and the later-field comparison.

The current package has not yet completed full deep re-execution for three
papers. It has completed a lower-cost pilot screen over six OpenReview papers:
real review snippets, review-guided regenerated mini-paper artifacts,
equal-context controls, short-term model reviews, and citation/frontier probes.
The three cases below should be treated as selected deep-replay candidates and
as transparent evidence of what the current pilot does and does not support.

## Why Deep Cases Are Needed

Aggregate model-review statistics are not enough for this paper's claim. The
claim is about how human scientific taste and insight can change an automated
research trajectory. Reviewers need to see the trajectory itself:

- what the original paper tried to do;
- which concrete human review comments were used as guidance;
- what the automatic researcher produced after using those comments;
- what experiments or metrics changed;
- whether the resulting direction resembles later mainstream or SOTA work;
- whether the case is short-term positive, long-term positive, delayed-value,
  or a failure.

The strongest future version of this paper should include about three deep
cases, not hundreds of shallow replays. Each case should include the original
paper ID, review excerpts, generated research plan or mini-paper, runnable
experiment code or logs, short-term metrics, later-frontier evidence, and a
plain account of the scientific route from the reviewed paper to later work.

## Case Selection Rule

Use the broad OpenReview screen to pick cases that are informative rather than
only positive:

1. one case where human review improves the regenerated artifact and plausibly
   points to a future-relevant direction;
2. one case where review guidance improves local paper quality but does not
   improve later-frontier alignment;
3. one case where the review exposes a concrete missing experiment, benchmark,
   metric, or scale question that can be rerun as a deeper automatic-research
   experiment.

This selection makes the paper more credible: human participation is
high-variance, so negative and mixed cases are part of the method's evidence.

## Candidate Case 1: LLM Refusal And Reliability

- Paper ID: `openreview_sample_1`
- Title: `Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback`
- arXiv: `2403.18349`
- Source artifacts:
  - `experiments/openreview_guided_regeneration_probe_20260602_073500/selected_papers.json`
  - `experiments/openreview_guided_regeneration_probe_20260602_073500/regenerated_artifacts.json`
  - `experiments/openreview_equal_context_ablation_20260602_142000/summary.json`
  - `experiments/retrospective_frontier_citation_probe_20260602_213000/summary.json`

Concrete review guidance used in the pilot:

- reviewers identify the central mechanism as training models to prefer saying
  "I don't know" rather than outputting an incorrect answer;
- reviewers note the experiment limitation: the benchmark set is narrow,
  especially arithmetic-heavy, so broader knowledge-intensive and nuanced
  question types should be tested.

Regenerated artifact behavior:

- baseline artifact proposes RLKF-style rejection training and standard
  accuracy/rejection-rate evaluation;
- review-guided artifact makes the preference data more specific:
  `(correct, refuse-to-answer)`, `(refuse-to-answer, incorrect)`, and
  `(correct, incorrect)`;
- review-guided artifact explicitly expands the intended experiments beyond
  arithmetic toward knowledge-intensive tasks and claim-calibrates that the
  findings may not generalize to all question types.

Observed pilot data:

- equal-context model review: review-guided wins over context control;
- GPT-style review gives review-guided overall `4` versus context-control
  overall `3`;
- citation-frontier probe retrieves a thin later citation graph with terms
  around `chatbot`, `moral`, `refusal`, `LLM`, `user`, and `regulation`;
- frontier score pattern is `short_term_positive_long_term_negative`:
  short-term review-guided minus paper-only is `+1`, but later-frontier
  review-guided minus paper-only is `-0.04`;
- winner under the current lexical future-frontier score is
  `shuffled_review_control`, not review-guided.

Interpretation:

This is not a delayed-value success case. It is a useful mixed case. The human
reviews help the regenerated artifact specify the refusal-training objective
and broaden the evaluation plan, but the current citation-frontier metric points
to a later literature about refusal as moral/social regulation in chatbots,
which the review-guided artifact does not capture. A deeper replay should ask
whether the review's benchmark criticism could have pushed the automatic
researcher from arithmetic refusal toward broader refusal-policy, user-facing
calibration, and safety-evaluation work.

Required deep rerun:

- reconstruct the original RLKF-style experiment at small scale;
- compare three automatic-research conditions: paper-only, review-guided, and
  shuffled-review-control;
- require the generated follow-up to add at least one non-arithmetic refusal
  benchmark and one user-facing reliability or safety metric;
- report accuracy, rejection precision, rejection recall, calibration, and
  over-refusal rate;
- compare the generated evaluation framing with later refusal and safety
  evaluation papers.

## Case 2: Conditional Graph Generation And Molecular Design

- Paper ID: `openreview_sample_2`
- Title: `Forked Diffusion for Conditional Graph Generation`
- Source artifacts:
  - `experiments/openreview_guided_regeneration_probe_20260602_073500/selected_papers.json`
  - `experiments/openreview_guided_regeneration_probe_20260602_073500/regenerated_artifacts.json`
  - `experiments/openreview_equal_context_ablation_20260602_142000/summary.json`
  - `experiments/retrospective_frontier_citation_probe_20260602_213000/summary.json`

Concrete review guidance used in the pilot:

- reviewers describe the method as a parent diffusion process over structure
  plus child diffusion processes over dependent properties;
- reviewers criticize unclear motivation, assumptions, and comparison against
  related conditional-generation methods;
- reviewers highlight the intended application to conditional graph generation
  and inverse molecular design.

Regenerated artifact behavior:

- review-guided regeneration is preferred by the equal-context model reviewer;
- GPT-style review gives review-guided overall `4` versus context-control
  overall `3`;
- the review-guided artifact improves framing around conditional information
  flow and multi-task graph-generation evaluation.

Observed pilot data:

- the current citation-frontier probe cannot score this case because it finds
  no reliable future-frontier terms after filtering;
- temporal diagnostic is `mixed_or_tie` with short-term review-guided minus
  paper-only `+1` and long-term frontier difference `0.0`;
- no delayed-value or future-alignment claim is supported for this case yet.

Interpretation:

This is a useful deep-replay candidate because it exposes a limitation in the
current frontier-reconstruction pipeline. The paper is scientifically relevant
to molecular design, but the current citation/metadata probe is too weak to
trace the later route. A deeper case should use domain-specific later-frontier
descriptors: conditional molecule generation, property-guided diffusion,
multi-objective inverse design, validity/novelty/uniqueness, and docking or
property predictors where available.

Required deep rerun:

- choose a low-cost molecular graph benchmark with public data and evaluators;
- generate follow-up methods under paper-only, review-guided, and control
  conditions;
- force review-guided plans to answer the reviewers' criticism: why forked
  diffusion is needed, what baseline it beats, and which assumptions are tested;
- report validity, uniqueness, novelty, property satisfaction, and baseline
  comparisons;
- compare the resulting method framing against later conditional molecule
  generation and inverse-design work.

## Case 3: Knowledge Unlearning And Privacy Risk

- Paper ID: `openreview_sample_17`
- Title: `Knowledge Unlearning for Mitigating Privacy Risks in Language Models`
- Source artifacts:
  - `experiments/openreview_guided_regeneration_probe_20260602_073500/selected_papers.json`
  - `experiments/openreview_guided_regeneration_probe_20260602_073500/regenerated_artifacts.json`
  - `experiments/openreview_equal_context_ablation_20260602_142000/summary.json`
  - `experiments/retrospective_frontier_citation_probe_20260602_213000/summary.json`
  - `experiments/semantic_frontier_judge_probe_20260602_223000/summary.json`

Concrete review guidance used in the pilot:

- reviewers recognize the privacy and right-to-be-forgotten motivation;
- reviewers ask for stronger baselines and metrics;
- the decision text raises a precise scale question: when does the simple
  gradient-ascent unlearning method reach a breaking point as the amount of
  unlearned data increases?

Regenerated artifact behavior:

- review-guided regeneration is preferred in the short-term model-review
  setting;
- GPT-style equal-context review gives review-guided overall `4` versus
  context-control overall `3`;
- review-guided artifact includes baseline, robustness, and privacy terms that
  are missing or weaker in the baseline mini-paper.

Observed pilot data:

- citation-frontier terms include `unlearning`, `data`, `privacy`, `LLMs`,
  `machine`, `user`, `forget`, `forgetting`, `dataset`, and `request`;
- paper-only score is `0.39`, review-guided score is `0.32`, and
  shuffled-review-control score is `0.29`;
- temporal diagnostic is `short_term_positive_long_term_negative`: short-term
  review-guided minus paper-only is `+1`, but later-frontier review-guided
  minus paper-only is `-0.07`;
- semantic frontier judge identifies this as the only case where the
  review-guided artifact wins semantically, but it is short-term-positive and
  semantic-positive rather than a strict delayed-value case.

Interpretation:

This is the strongest deep-replay candidate in the current package. It contains
a concrete human-insight question that can be turned into an experiment:
identify the breaking point of simple unlearning under increasing deletion
scope, stronger baselines, and privacy/utility tradeoff metrics. The later
field did indeed develop around LLM unlearning, privacy requests, benchmarked
forgetting, and utility preservation. The current lexical score still favors
paper-only because the original paper already contains the core future terms,
but the review guidance adds an experimentally meaningful next step.

Required deep rerun:

- reproduce a small unlearning setup with a lightweight language model or
  classification proxy;
- compare paper-only automatic follow-up against review-guided follow-up;
- require the review-guided condition to test increasing unlearning-set sizes,
  multiple baselines, privacy leakage, forget quality, and retained utility;
- report the actual breaking-point curve rather than only a regenerated
  manuscript;
- compare the resulting experiment design with later machine-unlearning and LLM
  unlearning benchmarks.

## What Counts As A Strong Deep Case

A deep case should not be counted as positive merely because a model reviewer
prefers the regenerated text. It should satisfy at least one of these stronger
patterns:

- `local_improvement`: review-guided replay improves short-term paper quality
  and produces better experiment data than paper-only and control;
- `delayed_value`: review-guided replay is worse on short-term score but more
  aligned with later mainstream or SOTA field developments;
- `frontier_route`: review-guided replay identifies a concrete experiment,
  benchmark, failure mode, or mechanism that became important later, even if
  the small rerun cannot reproduce the full later result;
- `negative_boundary`: review-guided replay fails, and the failure reveals what
  kinds of human comments should be downweighted by IGRE.

The current three candidate cases include local short-term improvements and
one strong frontier-route candidate, but no validated delayed-value positive
case. This boundary should remain visible in the manuscript.

## Minimum Future Deep-Case Artifact

For each selected paper, add a folder:

```text
experiments/deep_regeneration_case_<paper_id>/
  original_paper.md
  human_reviews.md
  review_signal_map.json
  paper_only_plan.md
  review_guided_plan.md
  shuffled_control_plan.md
  experiment_code/
  experiment_results.json
  regenerated_paper.md
  future_frontier_evidence.md
  case_analysis.md
```

This is the right scale for the current project: three carefully documented
cases can support a serious pilot paper and justify a later large-scale study,
whereas hundreds of shallow replays would be expensive and less interpretable.
