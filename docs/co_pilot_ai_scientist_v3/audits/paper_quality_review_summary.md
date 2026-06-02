# Paper Quality Review Summary

Review date: 2026-06-02

Reviewer routes:

- Monica OpenAI-compatible `gpt-4o-mini`
- Monica OpenAI-compatible `claude-3-7-sonnet-latest`

## Review Context

This review pass was run after adding the prospective matched-budget package
summary. The reviewers therefore saw the mixed prospective evidence: one
controlled Max-Cut micro-task favors the human-selected branch, while the
stronger FML-bench Causality prospective package favors the autonomous baseline.

## Aggregate Verdict

The two model reviewers agree on the main diagnosis: the IGRE architecture and
reproducibility package are promising, but the current paper remains a pilot
systems/reproducibility package rather than a top-conference empirical result.
`gpt-4o-mini` gives a generous `Weak accept`, mainly crediting novelty,
structured human intervention, and reproducibility. `claude-3-7-sonnet-latest`
gives `Reject` for a strong ML/NLP systems venue because the central
human-gating and paper-quality claims remain unsupported, the strongest
FML-bench prospective package is negative for co-pilot performance, and no
single end-to-end paper-generating trajectory has been demonstrated.

## Rubric Snapshot

| Reviewer | Recommendation | Novelty | Rigor | Clarity | Evidence | Reproducibility | Significance |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | Weak accept | 4 | 3 | 4 | 3 | 4 | 3 |
| `claude-3-7-sonnet-latest` | Reject | 3 | 1 | 2 | 1 | 3 | 2 |

## Shared Required Revisions

- Run matched-budget comparisons between autonomous AI Scientist-v2 and
  human-gated variants across more tasks, seeds, and budgets. Current
  prospective evidence is mixed and underpowered.
- Demonstrate at least one complete end-to-end trajectory from new hypothesis
  generation to experiments, claim audit, and final manuscript, plus a matched
  autonomous manuscript baseline.
- Add statistical or uncertainty analysis across tasks and seeds.
- Populate `attention_cost` and `taste_insight` fields in future prospective
  human gates, then test whether those gates change downstream outcomes.
- Add at least one scored official non-FML benchmark with a complete matched
  comparison when data access permits.
- Rewrite the main paper into a more focused conference structure, moving
  progress logs and setup failures into appendices or repository artifacts.
- Keep AlphaEvolve wording as `OpenEvolve-based` or `AlphaEvolve-style` unless
  official AlphaEvolve code becomes available.

## Mini-Manuscript Probe

After the review pass, we added a narrow matched mini-manuscript scoring probe
for `prospective_matched_fml_causality_20260602_000001`. The probe generates an
autonomous baseline mini-manuscript from the same package evidence and asks
Monica-routed `gpt-4o-mini` and `claude-3-7-sonnet-latest` to score anonymized
manuscripts A/B. Both reviewers prefer the co-pilot package mini-manuscript,
with overall scores `4` versus `3`. This is a useful measurement-readiness
signal, but it should not be read as evidence that the full co-pilot system
writes better papers: it covers one short package manuscript, not a complete
end-to-end manuscript generated under matched conditions.

## Full-Manuscript Generation Probe

We also added deterministic matched full-manuscript generation probes for the
prospective FML packages. They render the archived co-pilot evidence and matched
autonomous baselines into complete paper-shaped manuscripts with the same major
sections, then score them with an internal rubric for section completeness,
evidence grounding, claim calibration, method distinctness, and metric result
strength. The latest Fairness_fairlearn probe scores the co-pilot manuscript
`4.18` overall and the autonomous manuscript `4.11`, but the autonomous
manuscript is the only variant with a valid scalar FML test result. This
narrows the manuscript-generation gap but does not satisfy the reviewer request
for a fresh end-to-end paper-generating trajectory or independent expert
paper-quality scoring.

## Online Trajectory Manuscript Probe

We then repeated the same-continuous-trajectory online full-gate manuscript
probe three times. Each trajectory generates a complete co-pilot manuscript and
a same-run autonomous AI Scientist-v2 manuscript comparator from the same
orchestrator invocation. Two Causality trajectories have valid scalar test
metrics: the repeated-smoke summary reports `0` co-pilot benchmark wins, `1`
autonomous benchmark win, and `1` tie, with mean co-pilot test MAE `0.754120`
and mean autonomous test MAE `0.643337`. The third trajectory uses
`Fairness_fairlearn` and is a no-valid-branch failure-mode case, so it is
counted as unknown/no-valid rather than as a win for either side.

We also ran Monica-routed model-review A/B probes on all three paired
manuscript sets. All six reviewer calls prefer the co-pilot manuscript (`6/6`
wins), with rationales emphasizing methodological completeness, claim
calibration, and limitation honesty. This is useful measurement-readiness
evidence, but it is still model review over three smoke trajectories, not human
expert peer review or top-conference empirical support.

## Human Co-Pilot Trace Dataset

The paper now includes `human_copilot_trace_dataset.md/json`, a derived metadata
protocol for using the author's real Codex sessions as a single-author
longitudinal co-pilot trace corpus. Public human-AI interaction datasets are
useful adjacent evidence, but they do not directly provide human scientist
interventions inside AI Scientist-v2-style hypothesis-experiment-paper loops.
The derived trace currently indexes 52 gate records, 35 records with
attention-cost fields, 10 records with taste/insight fields, 4 prospective
matched packages, and 58 relevant commits. The stricter gate audits find 1
complete attention-cost record and 2 complete taste/insight records, so this
improves ecological validity and process evidence; it does not establish
population-level human benefit or human attention efficiency.

## Hypothesis Frontier Front End

The package now includes
`experiments/hypothesis_frontier_smoke_20260602_021500/`, a live
Monica-routed AI Co-Scientist-style front-end smoke. Two `gpt-4o-mini` calls
generate four candidate research frontiers and critique/rank them, selecting
`frontier_004` for possible next-budget evaluation. This improves the upstream
hypothesis-organization evidence, but it is still front-end orchestration only:
by itself it does not connect the selected hypothesis to a prospective
experiment, claim-audited manuscript, or autonomous hypothesis-front-end
baseline.

## Participation-Mode Design Reframing

The paper should now be read primarily as a workflow-design study for
human-guided automated science. The central target is not a binary proof that
human participation improves paper quality in all settings. The target is to
design and compare participation modes that make scientific taste and insight
usable inside an AI Scientist-v2-style loop: upstream taste-prior selection,
evaluator stress testing, frontier steering, selective program-search
escalation, structured manuscript feedback, and claim calibration. Negative
short-budget results are still useful because they identify where a proposed
human gate is not worth its cost or where autonomous search should dominate.

## Autonomous Hypothesis Front-End Baseline

The package now includes
`experiments/hypothesis_frontend_baseline_20260602_030500/`, a same-model
front-end comparison. The probe reuses the archived IGRE frontier portfolio,
generates an autonomous AI Scientist-v2-style portfolio with `gpt-4o-mini`, and
scores both portfolios with a fixed rubric. The scorer prefers IGRE (`overall
4` vs. autonomous `3`) because the IGRE portfolio has stronger evidence gain,
benchmark fit, claim calibration, and human-taste visibility. This is useful
participation-pattern evidence, but it is still front-end planning evidence
only.

## Expert-Review Taste Prior

The package also includes
`experiments/expert_review_taste_prior_probe_20260602_031800/`, which uses
Hugging Face streaming access over `nhop/OpenReview`. The Dataset Viewer
statistics report 34,638 rows, and the probe samples 160 rows without
downloading the full dataset. It verifies enough expert-review fields to build
a limited offline scientific-taste prior, while the sampled rows lack usable
`mean_reproducibility` values. The right use of this data is to compare
participation modes under a shared offline expert-review proxy: no human gate,
taste-prior gate, evaluator-stress gate, structured-feedback gate, and
claim-calibration gate can each generate artifacts that are scored against
OpenReview-derived novelty, correctness, clarity, impact, and confidence
signals. This does not replace live multi-researcher co-pilot interaction data,
but it can support data-driven workflow selection before such data exists.

## Participation-Mode Selection Probe

The package now includes
`experiments/participation_mode_selection_probe_20260602_060500/`. This probe
generates matched artifacts for five workflow modes and scores them with an
OpenReview-conditioned model-routed rubric. The no-gate artifact scores `2`
overall, taste-prior `3`, evaluator-stress `4`, structured-feedback `5`, and
claim-calibration `5`. The scorer's explicit `best_mode` field and ranking
order differ between the two tied top modes, so the conservative interpretation
is that structured feedback and claim calibration form the current top pair,
not that one mode has been uniquely proven best.

## OpenReview-Guided Regeneration Probe

The package now includes
`experiments/openreview_guided_regeneration_probe_20260602_073500/`, an
expanded version of the earlier three-paper probe. It selects six ML/AI papers
from the OpenReview sample and generates two mini-paper artifacts for each:
one from title/abstract only and one from title/abstract plus real review
snippets and decision text. The initial three-paper run had review-guided
artifacts win `3/3` comparisons. The expanded six-paper run has review-guided
artifacts win `5/6`, with one baseline win where the review text did not
materially improve the artifact. Mean overall score increases from `3.0` to
`3.8333`. This is the strongest current evidence that human review text can be
operationalized as scientific taste/insight for artifact improvement, and the
single baseline win is useful evidence that review guidance is not
automatically beneficial. The probe still does not rerun the original
experiments or constitute independent expert re-review.

## Review Insight Taxonomy

The package now includes
`experiments/review_insight_taxonomy_probe_20260602_064500/`. It mines 32
OpenReview review cases and maps actionable review patterns to IGRE gates:
novelty concerns to `scientific_taste_prior`, limitations and weaknesses to
`claim_calibration`, clarity issues to `structured_feedback`, and
metric/evaluation issues to `evaluator_stress_test`. This taxonomy is useful
because it separates review comments that can control automated research from
generic praise or vague reactions.

## Review Utility Map

The package now includes
`experiments/review_utility_map_probe_20260602_071500/`, a deterministic
large-sample complement to the model-routed taxonomy. It analyzes 473 review
snippets from the 160-paper OpenReview sample and classifies whether each
snippet can be routed to a concrete IGRE gate. The map finds 398 snippets with
actionable gate signals and 64 with noisy low-actionability signals. The
strongest gate pressure is evaluator stress testing (245 actionable triggers),
structured feedback (210), claim calibration (140), and scientific taste prior
(111). Category counts show that evaluation/metric concerns (205 snippets),
limitations and claim-boundary issues (140), novelty/positioning issues (111),
actionable suggestions (111), reproducibility details (79), method-correctness
issues (71), and clarity/presentation issues (86) are the review patterns most
directly useful for workflow control. This makes the taste/insight claim more
specific: useful human review is not all human opinion, but review text that
can change the agent's search direction, evaluator design, manuscript
structure, or claim boundary.

## Structured Feedback Probe

The selected `frontier_004` has now been connected to a small downstream
measurement probe in
`experiments/structured_feedback_probe_20260602_022900/`. Starting from the
same archived co-pilot manuscript, five Monica-routed `gpt-4o-mini` calls
generate informal feedback, IGRE-structured feedback, one revision under each
feedback mode, and a fixed-rubric model score. The scorer prefers the
structured revision (`overall 5` vs. `4`) and assigns higher scores on clarity,
reproducibility, claim calibration, evidence grounding, method distinctness,
limitation honesty, and novelty preservation.

This is useful evidence that the feedback protocol is operational and can
produce a measurable manuscript-revision difference. It is not independent
human expert review. The score output also contains an internally awkward note
that structured feedback "hurt" limitation honesty despite assigning a higher
limitation-honesty score to the structured revision, so the result should be
treated as a measurement-readiness probe rather than a stable quality finding.

## Second Prospective FML Package

A second prospective two-step FML package was run after the previous review. It
again uses `Causality_causalml`, DeepSeek, complete attention/taste logging, and
a matched autonomous baseline. The result is more negative for short-budget
co-pilot performance: co-pilot test MAE is `0.646224`, while the autonomous
baseline reaches `0.296399`. The FML summary now reports two prospective
two-step packages, both won by autonomous baselines.

## Paper Treatment

The manuscript should present Co-Pilot AI Scientist v3 as an architecture,
logging schema, and reproducibility package with pilot evidence. It should
report the prospective matched-budget package summary as mixed evidence, not as
support for human-gate superiority. It should not claim top-conference
readiness, paper-quality improvement, attention efficiency, or full-system
superiority until broader matched-budget evaluation and independent paper
quality scoring are complete.
