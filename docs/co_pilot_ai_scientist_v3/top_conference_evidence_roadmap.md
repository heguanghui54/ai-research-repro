# Top-Conference Evidence Roadmap

This roadmap translates the current evidence gaps into concrete experiments.
It is deliberately stricter than the present pilot package: passing the package
audits means the artifacts are reproducible, not that the paper has reached a
top-conference empirical bar.

## Current Position

Co-Pilot AI Scientist v3 is strongest as a workflow-design contribution. The
current artifacts support the claim that human scientific taste and insight can
be operationalized as auditable gates inside AI Scientist-v2-style research
loops. They do not yet prove that human-gated automation beats autonomous AI
Scientist-v2 on average, improves final paper quality under independent human
review, or increases high-tail scientific breakthroughs.

Boundary phrase for audits: not empirical superiority over autonomous AI Scientist-v2.

The next version should move from "mode design and pilot evidence" to
"matched empirical evidence." Every experiment below should be preregistered
before the generated manuscripts are scored.

The engineering release track is related but separate. It can demonstrate that
IGRE is usable as public research infrastructure, but it should not be counted
as empirical proof that co-pilot science outperforms autonomous science.

## Milestone 1: Blind Human Expert Review

- Claim tested: review-derived and IGRE-gated feedback improves research
  artifacts in ways recognized by qualified human reviewers.
- Required data: the prepared blind A/B packet in
  `experiments/human_expert_blind_review_packet_20260602_143000/`.
- Minimum design: 3-5 qualified reviewers with ML/AI expertise; the preferred first cohort is
  NUS-affiliated or school-affiliated faculty, postdocs, PhD students, or
  advanced research students. All reviewers score the same six anonymized pairs
  when feasible.
- Ethics and recruitment boundary: because the scores would be used for a
  research paper, recruitment should proceed only after institutional ethics
  review, departmental review, or exemption determination. Generic Prolific or
  crowd-worker evaluation can be used only as supplementary researcher-level
  evidence unless participants' ML/AI expertise is verified.
- Metrics: condition win rate, mean delta on novelty, rigor, clarity,
  significance, evidence grounding, and useful taste/insight comments.
- Required analysis: exact binomial win test excluding ties, bootstrap
  confidence intervals for mean deltas, inter-rater agreement when enough
  overlapping ratings exist, and qualitative coding of comments that would
  change a research-control decision.
- Upgrade condition: review-guided or gate-routed artifacts win a majority of
  non-tied comparisons with positive mean deltas on novelty or rigor.
- If it fails: keep the claim at "offline review signals are routeable," and
  remove any statement implying human-reviewed paper-quality improvement.

## Milestone 2: Matched Autonomous Versus Human-Gated Runs

- Claim tested: Co-Pilot AI Scientist v3 improves the distribution of outcomes
  relative to an autonomous AI Scientist-v2 baseline under the same budget.
- Required tasks: at least 3 tasks spanning FML-Bench or AI Scientist-v2-style
  ML tasks, one MLAgentBench-style implementation task, and one automatically
  scored program-search subproblem.
- Minimum design: at least 5 matched pairs per task; same model family, same
  tool access, same step budget, same task, and preregistered stopping rules.
- Metrics: task score, valid-run rate, evaluator-gaming failures, paper-quality
  proxy score, and claim-calibration violations.
- Current micro-pilot progress: the SSH Ubuntu package
  `prospective_matched_micro_pilot_20260603_ssh_maxcut` now supplies one
  controlled matched-budget run on weighted Max-Cut. On 12 deterministic
  machine-gradeable instances, the autonomous alternating baseline scores
  `0.596214` mean normalized score and the co-pilot-selected local-search
  branch scores `0.984419` (`+0.388205`). This validates the prospective
  package shape and a machine-gradeable frontier-steering gate, but it is still
  a small controlled subproblem rather than an AI Scientist-v2 research-task
  benchmark.
- Upgrade condition: the human-gated condition should improve either valid
  high-quality manuscript rate or evaluator-robustness rate without a large
  average task-score regression.
- If it fails: frame IGRE as a safety and workflow-control architecture rather
  than a performance-improving system.

## Milestone 3: Long-Horizon Taste Gate / DVRS Replay

- Claim tested: some human review comments that are not immediately helpful can
  nevertheless guide past research toward later frontier developments.
- Required data: delayed-value candidate queue from
  `experiments/delayed_value_review_candidate_mining_20260603_001500/`,
  plus the OpenAlex/Semantic Scholar future-frontier reconstruction pipeline.
- Minimum design: replay at least 30 delayed-value candidates and 30 matched
  controls after title-overlap and field-match drift guards.
- Metrics: immediate artifact quality, later-frontier alignment, delayed-value
  indicator, and reviewer-comment category.
- Upgrade condition: at least one clear delayed-value positive case, plus an
  aggregate advantage over matched controls under semantic or expert frontier
  judging.
- Delayed-value success case: a replay may be counted as theoretically
  positive even when the regenerated artifact has lower immediate paper-quality
  or original-task score, if the review-guided trajectory is clearly more
  aligned with later mainstream or SOTA field developments than both paper-only
  and shuffled-review controls.
- If it fails: keep LHTG/DVRS as a falsifiable measurement protocol and report
  negative evidence, not as a proven source of breakthrough guidance.

## Milestone 4: Three Deep Regeneration Case Studies

- Claim tested: broad OpenReview screening can identify concrete historical
  paper-review pairs where human review guidance changes the automatic-research
  trajectory in an interpretable way.
- Required data: about three selected cases from `deep_regeneration_casebook.md`,
  each with original paper summary, human review excerpts, regenerated
  paper-only/review-guided/control artifacts, runnable experiment code or logs,
  short-term metrics, later-frontier evidence, and a case-level route analysis.
- Minimum design: at least one positive or frontier-route case, one mixed case,
  and one negative/boundary case; do not rely only on LLM reviewer win counts.
- Metrics: actual rerun metrics where possible, changed experiment design,
  frontier-alignment score, qualitative similarity to later mainstream results,
  and whether the review changed a decision that an automatic researcher would
  otherwise not make.
- Upgrade condition: the case studies reveal concrete, inspectable mechanisms
  by which review guidance changes benchmarks, methods, failure analysis, or
  claim boundaries; at least one case should show nontrivial similarity to a
  later mainstream research route.
- If it fails: keep the paper as a workflow/protocol proposal and use the case
  failures to define which human review comments should be downweighted.

## Milestone 5: Live Multi-Researcher Co-Pilot Trace Data

- Claim tested: the gate schema captures real human scientific taste and
  attention cost beyond a single-author Codex trace.
- Required data: consented, privacy-protected traces from multiple researchers
  using the reusable Codex skill or a derived co-pilot workflow.
- Minimum design: at least 20 prospective gates from at least 5 researchers,
  with both `attention_cost` and `taste_insight` fields complete.
- Metrics: gate type distribution, attention minutes, downstream decision
  changes, accepted/rejected branch quality, and qualitative non-metric factors.
- Upgrade condition: the dataset shows that humans intervene for reasons not
  reducible to scalar metric improvement, and those interventions can be linked
  to downstream search-control changes.
- If it fails: describe the schema as single-author prototype tooling and mark
  population-level claims as future work.

## Milestone 6: Non-FML Official Benchmark Check

- Claim tested: the workflow is not overfit to FML-Bench-style evidence.
- Required data: at least one scored official non-FML benchmark, preferably
  MLAgentBench, ScienceAgentBench, or another task where AI Scientist-v2-style
  agents can be compared under matched budgets.
- Minimum design: one scored matched package with complete autonomous and
  human-gated trajectories, plus an evaluator-stress gate.
- Metrics: official task score, validity, runtime or cost, evaluator-stress
  outcome, and manuscript/claim quality.
- Upgrade condition: at least one non-FML benchmark shows a clear workflow
  benefit or a concrete evaluator-safety benefit.
- If it fails: keep benchmark claims explicitly limited to the current pilot
  tasks and program-search subproblems.

## Milestone 7: Public Skill Engineering And Community Adoption

- Claim tested: IGRE is not only a paper idea; it can be packaged as a reusable
  research skill that other researchers can install, run, and adapt.
- Reference point: high-adoption academic skill repositories such as
  `academic-research-skills`, which packages paper-writing and research support
  workflows and cites PaperOrchestra as one source for multi-agent
  paper-writing design.
- Required data: standalone skill README, install instructions, quickstart,
  templates, validation script, example gate trajectory, isolated install
  smoke test, and a clear boundary separating engineering adoption from
  scientific performance claims.
- Minimum design: publish a clean GitHub skill package with the six IGRE gates,
  example task, gate-log template, claim-audit template, local validator, and
  at least one reproducible smoke test. The current package satisfies the
  internal install-smoke part by installing into an isolated `CODEX_SKILLS_DIR`
  and validating the installed copy; it still needs an external researcher or
  clean external environment to demonstrate community transfer.
- Metrics: install success, quickstart completion, external issue/PR activity,
  example reuse count, and eventually stars or forks.
- Upgrade condition: at least one external researcher or clean external
  environment successfully runs the skill on a new topic and produces a valid
  gate log.
- If it fails: keep the skill as an internal artifact and do not claim
  engineering transferability.

## Decision Rule For The Paper

The paper should be submitted as a strong pilot/system paper only after
Milestone 1 or Milestone 2 produces positive evidence. It should be submitted
as a top-conference empirical paper only after Milestone 1 and Milestone 2 both
pass, with Milestone 3 providing either positive delayed-value evidence or a
clear negative result that strengthens the measurement contribution.
Milestone 7 can strengthen the systems and engineering-impact story, but it
does not replace blind expert review or matched benchmark evidence.

Until then, the correct claim boundary is:

> IGRE, LHTG, TFR, and DVRS define an auditable human-participation workflow for
> automated science. The current package demonstrates reproducible
> operationalization and pilot signals, but not empirical superiority over
> autonomous AI Scientist-v2.
