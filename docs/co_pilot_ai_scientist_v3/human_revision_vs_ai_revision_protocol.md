# Human Revision vs AI Scientist Revision Protocol

## Purpose

This protocol turns OpenReview version metadata into a direct comparison
between human author revision and AI Scientist-style revision under the same
peer-review signal. The target question is not only whether review-guided
automation improves a paper. The sharper question is how human authors, a raw
AI Scientist revision loop, and an IGRE-gated revision loop transform the same
reviews into different scientific trajectories.

The protocol should be used only when the dataset exposes enough version-chain
evidence to separate the initial submission, the reviews, and a later revised
or camera-ready paper. Useful fields include `forum_id`, `note_id`, `cdate`,
`tcdate`, `ddate`, `invitation`, `revision`, PDF hashes, attachment URLs, and
multiple paper versions.

## Version Chain

For each selected OpenReview case, construct the following artifacts:

| Symbol | Artifact | Required condition |
| --- | --- | --- |
| `P0` | Initial submission | Created before the official review-release or decision period. |
| `R` | Human peer reviews and decision text | Released after `P0`; includes reviewer comments, scores, confidence, and decision metadata when available. |
| `PH` | Human-revised paper | A later author revision or camera-ready version after reviews, rebuttal, or decision. |
| `PAI` | AI Scientist revision | Generated from `P0 + R` under a fixed automatic-research skill budget. |
| `PAI-6G` | IGRE six-gate revision | Generated from `P0 + R` after routing review comments through the six IGRE gates. |
| `Pcontrol` | Control revision | Generated from `P0` with no review, or with shuffled/unrelated review text of comparable length. |

The main experiment is valid only if `P0`, `R`, and `PH` can be time-ordered
from metadata. If the dataset provides only a single paper text with no reliable
revision metadata, the case must be downgraded to review-signal taxonomy or
mini-artifact generation, not causal revision comparison.

## Metadata Requirements

The minimal machine-checkable metadata record should include:

| Field | Use |
| --- | --- |
| `forum_id` | Groups all notes, reviews, revisions, decisions, and comments for one submission. |
| `note_id` | Identifies the exact paper note or review note. |
| `cdate` | Establishes creation time for initial papers, reviews, revisions, and decisions. |
| `tcdate` | Tracks true creation time when OpenReview edits or imports alter visible timestamps. |
| `ddate` | Excludes deleted or superseded notes unless explicitly used for audit. |
| `invitation` | Distinguishes submission, official review, rebuttal, revision, decision, and camera-ready notes. |
| `revision` | Links later paper notes to earlier versions when available. |
| `content_hash` or `pdf_hash` | Prevents accidental comparison of the same PDF under two note IDs. |

When both `cdate` and `tcdate` exist, the stricter earlier timestamp should be
used to prevent leakage. A case is eligible for the main analysis only when
review text is later than `P0` and the human-revised `PH` is later than the
review or decision window.

## Generation Arms

All automatic arms must be preregistered before scoring.

1. `P0-only`: regenerate from the initial paper without review text.
2. `raw-review-guided`: run the AI Scientist-style skill on `P0 + R`.
3. `six-gate-guided`: first convert `R` into IGRE gate packets, then run the
   same AI Scientist-style skill on `P0` with those gate packets.
4. `shuffled-review-control`: use review text from another paper with matched
   length and venue when possible.
5. `human-author-revision`: use `PH` as the real human author revision path,
   not as generation context.

PH must never be visible to the generation prompts for `PAI`, `PAI-6G`, or
`Pcontrol`. If the generation is meant to simulate the past, the literature and
model-access policy should be time-capped to the `P0` date. If a modern
retrospective model is used, the result must be labeled as retrospective
replay, not as a historically faithful simulation.

## Metrics

The evaluation compares both immediate paper repair and longer-horizon
frontier alignment.

| Metric | Definition |
| --- | --- |
| `review_coverage` | Fraction of substantive review concerns addressed. |
| `revision_alignment` | Whether the artifact changes the same problem, method, experiment, or claim boundary targeted by reviews. |
| `scientific_delta` | Change in novelty, rigor, evidence grounding, clarity, and reproducibility relative to `P0`. |
| `human_unique_gain` | Improvements present in `PH` but absent from `PAI` and `PAI-6G`. |
| `ai_unique_gain` | Improvements present in `PAI` but absent from `PH`. |
| `six_gate_gain` | Improvements present in `PAI-6G` beyond both raw-review-guided and shuffled-control arms. |
| `frontier_alignment` | Semantic or expert-judged similarity to later mainstream or SOTA research directions. |
| `claim_calibration` | Whether claims are narrowed, strengthened, or overclaimed relative to evidence. |
| `leakage_flags` | Any timestamp, text, or citation evidence that later information entered generation. |

Short-term scoring may prefer `PH` or `PAI` when experiments improve. Long-term
analysis can count a review-guided path as scientifically valuable even when
its immediate score is lower, if it moves toward later frontier concepts more
clearly than both `P0-only` and shuffled controls.

## Analysis Plan

The primary comparison is triadic:

`PH` vs `PAI` vs `PAI-6G`

For every review comment, code whether it is ignored, superficially addressed,
or substantively converted into a research-control decision. Then compare which
agent type performs the conversion:

- Human authors may use tacit domain taste, private experiments, and strategic
  positioning not visible in the public review record.
- Raw AI Scientist revision may over-follow visible comments or produce
  plausible but weak paper edits.
- IGRE-gated revision should be better at filtering comments, routing useful
  insights, rejecting generic noise, and preserving claim boundaries.

The expected contribution is not that AI replaces human revision. The useful
outcome is a decomposition of what humans revise better, what AI revises better,
and where six-gate routing makes review text more useful than simply adding
more context.

## Relation To IGRE

This protocol directly tests the six-gate theory:

- `scientific_taste_prior`: whether review comments change the research
  direction rather than merely editing prose.
- `evaluator_stress_test`: whether weak evaluation comments trigger stronger
  tests or ablations.
- `frontier_direction_router`: whether comments push the work toward later
  field trajectories.
- `verifiable_micro_evolution`: whether method changes are implemented and
  checked instead of only described.
- `structured_feedback`: whether diffuse review text becomes a concrete
  revision plan.
- `claim_calibration`: whether limitations and scope are corrected.

The key ablation is `PAI` versus `PAI-6G`: if six-gate routing improves
review-coverage, claim calibration, or frontier alignment over raw review
guidance, then IGRE is doing method work rather than merely copying OpenReview
comments into the prompt.

## Limitations

This protocol depends on version metadata quality. Some OpenReview venues keep
only the final public PDF, hide intermediate revisions, or expose revisions
without enough timestamps to prove causal order. Author revisions can also
reflect private rebuttal, reviewer discussion, editor requests, new experiments,
or deadline constraints that are not visible in public review text. Modern LLMs
may know later research unless generation is time-capped and audited. Therefore
the protocol should report metadata coverage, leakage risk, and version-chain
eligibility before making any revision-quality claim.

## Minimum Report

Each deep case should publish:

- the `P0`, `R`, and `PH` metadata chain;
- the concrete human review excerpts used for generation;
- the `P0-only`, `PAI`, `PAI-6G`, and `Pcontrol` artifacts;
- a review-comment adoption table;
- immediate experiment or paper-quality metrics where available;
- later-frontier alignment evidence;
- leakage and match-drift flags;
- a case-level conclusion stating whether human revision, raw AI revision, or
  IGRE-gated revision produced the most scientifically useful trajectory.
