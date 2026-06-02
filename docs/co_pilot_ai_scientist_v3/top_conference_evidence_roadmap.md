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

## Cost-Aware Pilot Logic

The current paper should be evaluated as a cost-aware pilot and protocol paper,
not as a completed large-scale benchmark study. The empirical goal is to test
whether small, inspectable experiments can reveal a promising theory of human
participation before expensive scaling begins. This avoids a failure mode where
hundreds of historical paper replays are run blindly, only to discover that the
participation mode, frontier metric, or leakage guard was poorly specified.

The preferred sequence is therefore:

1. Use low-cost OpenReview probes to identify routeable human taste and insight
   signals.
2. Run small but concrete regeneration and version-chain cases with visible
   reviews, artifacts, metrics, and failure modes.
3. Use those cases to refine IGRE gates and frontier-alignment metrics.
4. Scale only the designs that show interpretable signal, or report negative
   pilot evidence if no design is promising enough to justify large-scale cost.

## Prioritized Next Evidence Queue

The next experiments should be selected by the weakest claim that can be
credibly improved under the available budget, not by the easiest script to run.
The current priority order is:

1. **Official non-FML benchmark scaling.**
   Proof target: move from one scored official MLAgentBench task to a more
   robust non-FML evidence slice. Current progress: MLAgentBench vectorization
   is scored, the open-data sklearn matched package provides official-like
   held-out trigger-policy evidence, and MLAgentBench CIFAR10/debug is now a
   scored official task after pre-caching the official CIFAR10 archive. The
   starter baseline scores `0.5103`, while the co-pilot-selected branch scores
   `0.7782`, `0.7709`, and `0.7738` across three seeds, with mean `0.7743`,
   minimum `0.7709`, sample std `0.003676`, and mean delta `+0.2640`. OGBN-arxiv
   now adds a second scored official-evaluator path: compatibility starter
   `0.02745`, co-pilot-selected normalized AdamW MLP scores `0.53999`,
   `0.54089`, and `0.54363` across three seeds, with mean `0.5415`,
   minimum `0.53999`, sample std `0.001896`, and mean delta `+0.5141`,
   with the boundary that the baseline is a compatibility
   translation rather than the unmodified NeighborLoader starter. Best near-term
   path: add another task or expand matched end-to-end trajectories. A 2026-06-03
   BabyLM feasibility probe shows that BabyLM data preparation is accessible
   from GitHub, and a cached tiny compatibility path now trains a two-layer
   from-scratch GPT-2 on 96 samples with train loss `10.5886` and reports a
   manual 64-chunk eval loss `10.6504` / perplexity `42208.44`. This remains a
   tiny compatibility score rather than a full BabyLM benchmark. Blocking condition:
   data access, CPU/GPU runtime, or external account consent prevents
   additional official scores. If blocked, report the current official CIFAR
   and OGBN results as two narrow official-evaluator paths only.

2. **Blind expert review packet collection.**
   Proof target: test whether qualified human reviewers prefer IGRE-gated or
   review-guided artifacts under anonymized scoring. Best near-term path:
   recruit NUS/school-affiliated ML/AI reviewers after ethics or departmental
   exemption review. Blocking condition: no qualified reviewers or no ethics
   clearance. If blocked, keep model-only dry runs as debugging evidence only.

3. **Matched multi-task autonomous versus human-gated runs.**
   Proof target: test whether co-pilot gates improve valid-run rate,
   evaluator robustness, or manuscript quality without unacceptable task-score
   regression. Best near-term path: extend the current prospective package
   format to at least three task families and five matched pairs per task.
   Blocking condition: API/compute budget or remote benchmark setup prevents
   enough paired runs.

4. **Deep TFR replay cases from the candidate queue.**
   Proof target: find at least one inspectable delayed-value or frontier-route
   case, or produce a stronger negative result about historical peer-review
   guidance. Best near-term path: choose cases from the delayed-value candidate
   queue using the OpenAlex validation score, then generate paper-only,
   review-guided, shuffled-control, and six-gate artifacts. Blocking condition:
   citation-frontier reconstruction is too thin or match-drift risk is too high.

5. **Human Revision vs AI Scientist Revision version-chain pilot.**
   Proof target: when OpenReview or Hugging Face metadata exposes `forum_id`,
   `note_id`, `cdate`, `tcdate`, `ddate`, `invitation`, `revision`, or multiple
   paper versions, compare the human author revision (`PH`) against raw AI
   Scientist revision (`PAI`) and IGRE six-gate revision (`PAI-6G`) under the
   same review signal. Best near-term path: run only a few eligible deep cases,
   showing the concrete reviews, generated artifacts, human-revised paper,
   leakage guards, and short-term/long-term metrics. Blocking condition:
   version-chain metadata is missing or cannot prove that `P0`, reviews, and
   `PH` are temporally ordered.

6. **External skill reuse beyond scripted clean environments.**
   Proof target: show that the release skill can be used by another researcher
   or independently prepared environment to produce a valid gate log. Best
   near-term path: invite one external tester after the release package is
   stable. Blocking condition: no external tester; do not substitute repository
   stars or scripted local reuse for independent adoption evidence.

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

## Milestone 4b: Human Revision vs AI Scientist Revision

- Claim tested: when version-chain metadata is available, the same historical
  peer-review signal can be used to compare human author revision against raw
  AI Scientist revision and IGRE six-gate revision.
- Required data: `P0` initial submission, `R` human peer reviews and decision
  text, `PH` human-revised or camera-ready paper, plus generated `PAI`,
  `PAI-6G`, and shuffled/no-review controls. Metadata should include
  `forum_id`, `note_id`, `cdate`, `tcdate`, `ddate`, `invitation`, `revision`,
  and PDF/content hashes when available.
- Minimum design: a small number of eligible deep cases is acceptable at the
  current budget stage, provided each case shows the exact review excerpts,
  generated artifacts, human-revised paper, version ordering, leakage guards,
  immediate metrics, and later-frontier alignment evidence.
- Metrics: review coverage, revision alignment, scientific delta,
  human-unique gain, AI-unique gain, six-gate gain, frontier alignment, claim
  calibration, and leakage flags.
- Upgrade condition: at least one case demonstrates an interpretable difference
  between human revision and AI/IGRE revision, such as humans adding tacit
  domain strategy, AI finding a different experiment path, or six-gate routing
  filtering useful review insight better than raw review prompting.
- If it fails: report it as a negative pilot showing that version-chain replay
  needs better metadata, stronger time-capping, or different frontier metrics
  before large-scale runs are justified.

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

- Claim tested: the workflow is not overfit to FML-Bench-style evidence and can
  be evaluated on official non-FML MLAgentBench tasks.
- Required data: the current three-seed scored official CIFAR10/debug run plus
  the three-seed scored OGBN-arxiv official-evaluator compatibility run, plus
  the BabyLM third-task feasibility audit showing setup success and a tiny
  cached compatibility score; then a full BabyLM run, another accessible
  official task, or more matched end-to-end trajectories when budget permits.
- Minimum design: at least one scored official non-FML MLAgentBench task with
  a documented baseline, co-pilot-selected branch, official evaluator output,
  multi-seed robustness when feasible, and a plan to scale beyond one task.
- Metrics: official task score, validity, runtime or cost, evaluator-stress
  outcome where applicable, and manuscript/claim quality.
- Upgrade condition: the official non-FML benchmark shows workflow benefit or
  evaluator-safety benefit and is not treated as broad coverage without scale.
- If it fails: keep official non-FML claims limited to the three-seed scored
  CIFAR10/debug task, the three-seed OGBN-arxiv compatibility path, and the
  narrow BabyLM tiny compatibility score; keep broader benchmark claims
  future-facing.

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
  and validating the installed copy; it also has a global-install reuse smoke
  and a clean external temporary reuse smoke that copies the release skill into
  `/tmp` and instantiates all six gates on a fresh scientific-visualization
  topic. It still needs an actual external researcher or community run to
  demonstrate social transfer beyond scripted clean-environment reuse.
- Metrics: install success, quickstart completion, external issue/PR activity,
  example reuse count, and eventually stars or forks.
- Upgrade condition: at least one external researcher or independently prepared
  external environment successfully runs the skill on a new topic and produces
  a valid gate log. The current scripted clean-environment smoke satisfies only
  the environment-transfer half of this condition.
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

The present low-budget version can still be useful if it clearly establishes
which participation patterns are worth scaling and which are not. It should
therefore emphasize pilot reliability, traceability, and decision value rather
than pretending that a small number of replays settles the general question of
human-AI scientific collaboration.

Until then, the correct claim boundary is:

> IGRE, LHTG, TFR, and DVRS define an auditable human-participation workflow for
> automated science. The current package demonstrates reproducible
> operationalization and pilot signals, but not empirical superiority over
> autonomous AI Scientist-v2.
