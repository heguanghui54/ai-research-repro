# Co-Pilot AI Scientist v3: Insight-Gated Research Evolution for Collaborative Automated Science

**Author:** He Shi, School of Computing, National University of Singapore

## Abstract

Autonomous research agents have begun to connect idea generation, experiment
execution, benchmark evaluation, and paper writing. Yet fully autonomous
pipelines still struggle at the creative and strategic decisions where human
scientists contribute taste, field knowledge, and responsibility for claims.
We propose Co-Pilot AI Scientist v3 and its underlying method, Insight-Gated
Research Evolution (IGRE). IGRE is not a direct composition of prior research
agents. It reorganizes their useful lessons into a tail-seeking research
process: automated systems maintain broad executable frontiers, while humans
inject scientific taste, risk tolerance, and claim responsibility at explicit
decision gates. The primary goal is not to prove a binary claim that "human
participation improves paper quality." It is to design, compare, and refine
human-participation modes that better translate hard-to-quantify scientific
taste and insight into automated research workflows. We define a reproducible
evaluation protocol that compares autonomous, partially gated, and fully
collaborative variants on small automated-research tasks. The central
hypothesis is intentionally asymmetric: human input may reduce average
short-budget benchmark performance, but a well-designed participation workflow
can raise the probability of rare, high-novelty, high-impact research outcomes
that matter most for scientific discovery.

## 1. Introduction

The next useful version of automated research is unlikely to be a scientist-free
paper factory. Scientific work is not only a sequence of executable steps; it is
also a process of choosing valuable questions, recognizing weak evidence,
reframing failures, and deciding which claims deserve to be made. Prior systems
offer useful ingredients: hypothesis debate, executable experiment search, and
automatic-evaluator code evolution. This paper uses those ingredients as
inspiration, but the method is defined around a different objective. Scientific
co-piloting should not only maximize the mean score of short benchmark runs. It
should also increase the chance that a run crosses into a qualitatively better
research direction: a sharper question, a more revealing evaluator, a surprising
failure interpretation, or a claim that opens a new line of work.

This paper proposes Co-Pilot AI Scientist v3 and formalizes it as Insight-Gated
Research Evolution (IGRE). The goal is not to slow an autonomous pipeline with
arbitrary approvals. IGRE treats human intervention as a scarce, high-variance
operator that should be invoked only where scientific judgment can change the
shape of the search frontier. The proposed gates are: scientific taste prior,
evaluator stress test, frontier steering, verifiable micro-evolution, and claim
calibration.

The practical question is therefore a design question: which human
participation pattern best converts scientific taste into useful search
pressure? IGRE evaluates several modes rather than assuming a single human role:
upstream taste-prior selection, evaluator stress testing, mid-run frontier
steering, selective program-search escalation, structured feedback on
manuscript evidence, and claim calibration. The experiments in this version are
used to shape that workflow and identify boundary conditions, including
negative cases where autonomous search is stronger under short budgets. This
makes the paper an applied collaboration-design study for automated science,
not merely a test of whether humans are globally "better" or "worse" than
automation.

## 2. Related Work

AI Co-Scientist frames scientific discovery as hypothesis generation,
discussion, and evolution. Its strength is upstream research imagination and
evidence organization. AI Scientist-v2 focuses on turning candidate ideas into
runnable experiments and papers through agentic tree search. AlphaEvolve focuses
on code evolution driven by automatic evaluation. FunSearch provides an earlier
example of LLM-guided program search for mathematical discovery. Coscientist
shows how LLM agents can connect to chemistry tools and laboratory automation.

IGRE borrows design pressure from these systems, not their control logic. From
hypothesis agents it takes the need for diverse conjectures, but replaces
free-form debate with a logged scientific-taste prior. From automated paper
agents it takes executable experiment search, but inserts frontier steering and
claim calibration where benchmark score is not enough. From program evolution it
takes deep search on machine-gradeable subproblems, but exposes that search only
through a selective escalation gate. The result is a co-pilot pattern whose
unit of optimization is not a single task metric, but an evidence-aligned
research trajectory with higher upside.

### 2.1 Distinction from Generic Research Co-Pilots

Many co-pilot systems treat humans as approvers, prompt writers, preference
labelers, or emergency supervisors. IGRE makes a different algorithmic claim:
the most important human contribution to automated science is often a
non-metric prior over what is scientifically tasteful. This prior is difficult
to reduce to a scalar reward. It includes judgments such as whether a question
has depth, whether a negative result is revealing, whether a benchmark is too
easy to game, whether a surprising branch is worth preserving, and whether a
claim would still matter if the primary metric improved only slightly.

IGRE therefore separates three concepts that are often conflated in
human-in-the-loop agents. **Preference** means choosing what looks better among
finished options. **Oversight** means preventing invalid or unsafe actions.
**Scientific taste** means changing what the system searches for before the
outcome is known. The last role is the distinctive one. In IGRE, taste is not
forced into a complete reward model; it is captured as a structured,
auditable-but-partly-qualitative gate record that changes the search frontier.
This lets the system evaluate human input honestly: it may hurt the mean score,
but it should be judged by whether it increases the chance of rare,
field-opening trajectories.

## 3. Method

Co-Pilot AI Scientist v3 implements Insight-Gated Research Evolution. IGRE has
four machine loops and five human-facing operators. The machine loops preserve
the scalability of automated research: hypothesis expansion, experiment
construction, executable frontier search, and verifiable micro-evolution. The
human-facing operators are designed for places where scientific taste can alter
which frontier is worth expanding.

Figure 1 gives the operational data flow. A research goal enters the hypothesis
loop, passes through experiment construction and executable frontier search,
optionally delegates machine-gradeable subproblems to OpenEvolve-based
micro-evolution, and finally reaches manuscript generation and claim
calibration. Each gate consumes a structured frontier and produces a logged
decision artifact.

```text
Research goal -> hypothesis loop -> experiment loop -> search loop
          |             |                 |               |
   taste prior  evaluator stress  frontier gate   micro-evolution gate
                                                        |
                                                        v
                                      Verifiable micro-evolution
                                                        |
                                                        v
                                   draft manuscript -> claim-calibration gate
                                                        |
                                                        v
                                          evidence-aligned paper package
```

First, the scientific-taste prior asks the human scientist to select, merge, or
rewrite candidate directions using criteria that are not fully captured by
early metrics: conceptual freshness, field relevance, asymmetry of upside, and
whether a failure would still teach something.

Second, the evaluator stress-test gate converts selected hypotheses into
benchmark tasks, baselines, ablations, executable scripts, and rejection
conditions. The gate asks not only whether the metric is convenient, but whether
it can be gamed, whether it misses utility, and whether it would support the
paper claim if the result were positive.

Third, the frontier-steering gate runs over executable experiment branches. At
predefined checkpoints, the system summarizes metrics, code snapshots, errors,
and novelty notes. The human scientist may allocate budget to a branch that is
not currently best on the primary metric if it has higher scientific upside or
reveals a more important failure mode.

Fourth, the verifiable micro-evolution gate sends only machine-gradeable
subproblems to a code-evolution engine. Since AlphaEvolve itself is not open
sourced, our reproducible implementation uses OpenEvolve as the practical
substrate for this operator. OpenEvolve provides an evolutionary coding loop
with custom evaluators, OpenAI-compatible model routing, MAP-Elites
quality-diversity search, island-based populations, and reproducible seeds. The
operator evolves code, stores candidate programs, and returns verified
improvements to the main research pipeline.

Fifth, the claim-calibration gate audits the final paper draft against the
evidence record. It weakens, removes, or reframes claims that are not supported,
and it records which stronger claims remain hypotheses for the next benchmark
stage.

```text
Algorithm 1: Insight-Gated Research Evolution (IGRE)
Input: research goal g, benchmark budget B, human attention budget H
1. Generate a diverse hypothesis frontier F_h from g.
2. Apply scientific_taste_prior(F_h, H) to select or rewrite high-upside
   hypotheses, including branches whose value is not yet metric-visible.
3. Convert selected hypotheses into evaluators, baselines, and failure tests.
4. Apply evaluator_stress_test to reject metrics that are non-executable,
   easily gamed, or too weak to support the intended claim.
5. Run executable frontier search under budget B and log branch states.
6. At checkpoints, apply frontier_steering to allocate budget using both
   metrics and qualitative upside/failure value.
7. For machine-gradeable subproblems, apply verifiable_micro_evolution only
   when direct editing is insufficient and the evaluator is reliable.
8. Draft the paper from logs, then apply claim_calibration to align claims with
   evidence and demote unsupported conclusions to future hypotheses.
Output: evidence-aligned paper package plus auditable gate trajectory.
```

Each human intervention is recorded as structured data: decision type, options,
free-text rationale, affected artifacts, and downstream consequences. This makes
human participation part of the reproducibility record rather than an invisible
side channel.

The current artifact package contains a retrospective full-gate trajectory
covering all proposed gate types. It links an idea gate selecting the narrow
human-gated tree-search contribution, an evaluator gate rejecting a fairness
metric-gaming branch, a live branch gate selecting among two Causality drafts, a
program-search gate escalating to OpenEvolve, and a claim gate demoting
unsupported superiority claims to future work. This trajectory demonstrates the
log format and evidence chain, but it is not yet a single online end-to-end run.

We also provide a rerunnable full-gate trace script. Given the archived
experiment summaries, the script recomputes a continuous sequence of idea,
evaluator, branch, program-search, and claim gates and writes both JSON and
Markdown artifacts. This verifies that the gate policy can be executed over the
current evidence package. It is deliberately labeled as an executable artifact
replay rather than a fresh online training run.

After that replay artifact, we ran a first fresh online full-gate smoke
trajectory on `ubuntu-heshi`. The orchestrator generated an idea gate, approved
a low-cost evaluator bundle, launched a new two-draft FML-bench Causality
frontier, selected the lower-validation-MAE branch, continued the selected
snapshot for one AI Scientist-v2 step, ran a one-iteration OpenEvolve knapsack
search, and wrote a claim-audit gate. The branch frontier selected step 2
(`0.627837` validation MAE) over step 1 (`0.677448`). The one-step continuation
then reached test MAE `0.862015`, worse than the selected frontier's test MAE
`0.646224`; the simultaneous knapsack OpenEvolve smoke reached best score
`1.000000`. This is the first online orchestration evidence for all five gate
types, but it is a smoke test and a negative continuation outcome, not evidence
of co-pilot superiority.

We then ran a same-FML-step autonomous baseline for the online smoke. The
baseline used the same Causality task and DeepSeek model for three AI
Scientist-v2 steps, but without a human branch gate. It reached validation MAE
`0.354147` and held-out test MAE `0.428516`, substantially outperforming the
human-gated smoke continuation's test MAE `0.862015`. This paired smoke result
is negative for performance improvement, while still supporting the narrower
claim that online co-pilot orchestration is executable.

We subsequently repeated the stronger same-continuous-trajectory paired online
smoke pattern three times. Each run generated complete co-pilot and autonomous
manuscript artifacts from the same orchestrator invocation. Two Causality runs
have valid scalar test metrics: the co-pilot continuation has mean test MAE
`0.754120` and the same-run autonomous baseline has mean test MAE `0.643337`;
lower is better, so the valid-metric aggregate is `0` co-pilot wins, `1`
autonomous win, and `1` tie. The third run switches to `Fairness_fairlearn` and
is archived as a no-valid-branch failure-mode trajectory; neither side obtains
a valid scalar test metric. Monica-routed A/B model-review probes prefer the
co-pilot manuscript in all six reviewer calls across the three runs. This is
stronger than a single archived matched-budget comparator because the
manuscripts come from repeated same-run online smokes, including a cross-task
failure case. It still does not prove co-pilot superiority: the valid benchmark
aggregate favors autonomous or tie, the budgets are tiny, and model review is
not independent expert paper-quality review.

We now also include a live AI Co-Scientist-style hypothesis-frontier smoke. A
Monica-routed `gpt-4o-mini` front end made two live model calls: one to generate
four candidate research frontiers for the next IGRE evidence milestone, and one
to critique and rank them under conservative AI Scientist-v2 evidence
discipline. The selected next-budget candidate is `frontier_004`, a structured
human-feedback mechanism intended to compare rubric-guided feedback against
informal feedback for reproducibility and clarity. This closes a narrow
orchestration gap in the AI Co-Scientist portion of the architecture: the
package now has a logged generate-critique-rank hypothesis front end. It does
not show that the selected candidate improves downstream benchmarks or paper
quality, and it is not a human-selection result.

We then added an autonomous hypothesis-front-end baseline. The script
`run_hypothesis_frontend_baseline.py` reuses the archived IGRE candidate
portfolio, asks the same model to generate an autonomous AI Scientist-v2-style
portfolio without explicit human-taste gates or structured human feedback, and
uses a fixed-rubric comparison call to score both portfolios. The scorer
prefers IGRE (`overall 4` versus `3`) because the IGRE portfolio has higher
evidence gain, benchmark fit, claim calibration, and human-taste visibility.
The autonomous portfolio is not useless: the audit marks it as stronger for
exploring fully autonomous process variants. This probe only compares
direction-finding portfolios; it does not evaluate downstream benchmark
performance, paper quality, or human expert judgment.

We therefore ran a small downstream structured-feedback probe for
`frontier_004`. Starting from the same archived co-pilot manuscript, the script
`run_structured_feedback_probe.py` made five Monica-routed `gpt-4o-mini` calls:
free-form informal feedback, IGRE-structured feedback, one revision conditioned
on each feedback mode, and a fixed-rubric model score over the two revisions.
The scorer preferred the structured-feedback revision (`overall 5` versus `4`),
with higher scores for clarity, reproducibility, claim calibration, evidence
grounding, method distinctness, limitation honesty, and novelty preservation.
This result should be read narrowly. It shows that the IGRE feedback format can
be operationalized and can induce a measurable revision difference under a
model-routed evaluator. It is not independent human peer review, not a
multi-task result, and not evidence that human feedback improves benchmark
performance.

To test whether public expert-review data can serve as an offline proxy for
scientific taste, we added an expert-review taste-prior probe over
`nhop/OpenReview`. The script `run_expert_review_taste_prior_probe.py` first
checks Hugging Face Dataset Viewer availability, then uses streaming access so
the experiment does not need to download the full dataset. In the current run,
the dataset statistics report 34,638 rows and the streaming sample contains 160
papers. The required fields are available, including titles, abstracts,
reviews, decisions, mean overall score, novelty, clarity, impact, and
reproducibility fields. Within the 160-row sample, `mean_score` is available
for all 160 rows with mean 0.5349, `mean_novelty` for 27 rows with mean 0.6284,
`mean_correctness` for 106 rows with mean 0.6267, `mean_clarity` for 71 rows
with mean 0.5968, `mean_impact` for 73 rows with mean 0.5459, and
`mean_confidence` for 158 rows with mean 0.6373. No sampled row has a usable
`mean_reproducibility` value, which is an important caveat for any
reproducibility-aware taste model. This probe supports only a limited offline
taste-prior construction: it can help rank or diagnose generated hypotheses and
manuscript revisions against expert-review signals, but it is not live human
co-pilot interaction data and does not show that such a prior improves
AI Scientist-v2 outputs.

This placement makes the OpenReview data useful for the paper's main design
question. Rather than treating the dataset as evidence that online human
co-piloting has already occurred, we use it as a participation-mode selection
benchmark: different workflow variants can generate hypotheses, experiment
plans, evidence summaries, or manuscript revisions, and an OpenReview-derived
rubric can score whether those artifacts resemble higher-rated expert-reviewed
papers in novelty, correctness, clarity, impact, and reviewer confidence. This
lets the paper compare participation patterns such as no human gate, upstream
taste-prior gate, evaluator-stress gate, structured-feedback gate, and claim
calibration gate under a common offline expert-review proxy. The result would
not prove real-world peer-review acceptance, but it can provide data-driven
support for choosing a better human-in-the-loop workflow before larger online
studies exist.

We then ran this participation-mode selection experiment. The script
`run_participation_mode_selection_probe.py` asks the same model to generate
matched artifacts for five modes: no human gate, taste-prior gate,
evaluator-stress gate, structured-feedback gate, and claim-calibration gate.
The scoring call is conditioned on compact high- and low-scoring OpenReview
examples from the expert-review probe. In this run, the no-gate artifact scores
`2` overall, taste-prior scores `3`, evaluator-stress scores `4`, and both
structured-feedback and claim-calibration score `5`. The scorer ranks
claim-calibration and structured-feedback as the top two modes, with a minor
internal inconsistency between the explicit `best_mode` field and the ranking
order; we therefore treat the result as evidence for a top pair rather than a
single winner. The design lesson is still useful: reviewer-like signals appear
most immediately valuable when they improve manuscript structure and weaken
unsupported claims, while upstream taste-prior selection remains promising but
less directly evidenced in this artifact-level probe.

To make the expert-review signal less abstract, we also ran an
OpenReview-guided regeneration probe. The initial probe selected three ML/AI
papers from the sample: an LLM refusal/RLKF paper, an in-context learning
paper, and a semi-supervised/robust learning by mixup paper. For each paper,
`run_openreview_guided_regeneration_probe.py` generates a baseline mini-paper
artifact from title and abstract only, and a review-guided artifact from title,
abstract, and the real review snippets/decision text. A fixed model-routed
scorer preferred the review-guided artifact in all three initial pairs. We then
expanded the probe to six papers spanning accepted and rejected OpenReview
examples in LLM reliability, graph generation, unlearning/privacy, in-context
learning, semi-supervised robustness, and safety-critical causal generation.
In the expanded run, review-guided artifacts win `5/6` pairs, with one
baseline win where the review text did not improve the generated artifact.
Mean overall score increases from `3.0` to `3.8333`, giving a mean delta of
`+0.8333`. This is a stronger empirical use of OpenReview than the availability
probe: real review comments often act as human scientific taste/insight that
improves paper-shaped regenerations, but not always. The claim remains bounded
because the experiment does not rerun the original methods or obtain
independent expert review.

To reduce same-model scoring bias, we then reran the six generated pairs
through `run_openreview_regeneration_cross_model_review.py`, using
`claude-3-7-sonnet-latest` as an independent Monica-routed reviewer. The
stricter cross-model review gives review-guided artifacts `3/6` wins, baseline
`1/6` win, and `2` ties, with a smaller mean overall delta of `+0.1667`. The
per-paper rationales are informative: review text helps when it adds concrete
method details, experimental specificity, or limitation/claim calibration; it
does not help when it merely restates generic concerns or causes the artifact
to lose the original technical framing. We therefore interpret the regeneration
results as evidence for workflow selection and review-signal utility, not as a
stable proof that adding review text always improves generated papers.

Finally, `run_review_insight_taxonomy_probe.py` mines 32 OpenReview review
cases to identify which kinds of review comments are most useful as automated
research control signals. The model-routed taxonomy marks novelty concerns and
limitations/weaknesses as highly actionable (`5/5`), mapped primarily to the
scientific-taste-prior and claim-calibration gates. Clarity issues are also
actionable (`4/5`) and map to structured feedback, while metric/evaluation
issues (`4/5`) map to evaluator stress testing. This taxonomy gives IGRE a
more concrete rule: human review text is most useful when it changes what the
agent should pursue, what evidence it must gather, what claims it may safely
make, or how clearly the manuscript communicates the result.

To move from a small taxonomy to a larger reproducible signal map, we then ran
`run_review_utility_map_probe.py` over the 160-paper OpenReview sample. This
deterministic probe extracts 473 review snippets and classifies review patterns
by whether they can be routed to a concrete IGRE gate. It finds 398 snippets
with at least one actionable signal and 64 snippets with noisy low-actionability
signals. The strongest gate pressure is not generic approval: 245 snippets
trigger evaluator-stress testing, 210 trigger structured feedback, 140 trigger
claim calibration, and 111 trigger scientific-taste priors. The highest-utility
categories are evaluation/metric concerns (205 snippets), limitations and claim
boundary issues (140), novelty/positioning issues (111), actionable suggestions
(111), reproducibility details (79), method-correctness issues (71), and
clarity/presentation issues (86). This gives a more data-grounded version of
the paper's central workflow claim: useful human taste and insight are not all
human comments, but the subset of review signals that can change search
direction, evaluator design, manuscript structure, or claim boundaries. Generic
praise and vague reactions are useful only after decomposition into one of
these actionable control signals.

## 4. Benchmark Selection and Evaluation Plan

We evaluate six variants: autonomous baseline, idea gate only, branch gate only,
evaluator gate only, claim gate only, and full co-pilot v3. Candidate tasks
should be selected by claim type rather than by a single favorite benchmark.
For AI Scientist-v2-style experiment search, FML-bench is a useful near-term
benchmark because it is already runnable in our Ubuntu environment and exposes
branch-level logs. For machine-gradeable algorithmic subproblems, we use
OpenEvolve-controlled tasks such as function minimization, knapsack heuristic
search, and weighted Max-Cut. For broader evidence beyond FML-bench, we include an initial
MLAgentBench vectorization probe for end-to-end ML experimentation and track
setup probes for additional MLAgentBench and ScienceAgentBench tasks. The
current evidence still does not include a second scored official non-FML
benchmark: the MLAgentBench CIFAR10/debug run was blocked by slow dataset
download, the MLAgentBench IMDB probe repaired the missing `datasets`
dependency but could not reach HuggingFace from the Ubuntu host, and
ScienceAgentBench metadata/artifacts were not reachable. Higher-cost stretch benchmarks include
MLE-bench Lite for Kaggle-style ML engineering, PaperBench for paper-to-code
replication and hierarchical rubric grading, and AIRS-Bench for full ML research
lifecycle evaluation.

Metrics include task score, paper quality, claim support, search efficiency,
human attention cost, and hypothesis diversity. For the programmatic-search
module, the key ablation is OpenEvolve versus repeated direct LLM edits under
the same evaluator and iteration budget. FML-bench should therefore be read as
one current evidence source, not as the complete benchmark definition for the
project.

Because IGRE's key contribution is scientific taste rather than generic
approval, we add a taste/insight rubric to the evaluation package. The rubric
scores problem depth, novelty potential, mechanistic value, failure
informativeness, benchmark taste, claim significance, and risk asymmetry from 1
to 5, with short rationales. This is deliberately not a reward model. It is a
structured record of the non-metric prior that caused a human to preserve,
rewrite, or prune a branch. Future evaluations should report both mean task
performance and high-tail signals: whether a human-selected branch that an
autonomous policy would have pruned later produces a stronger claim, better
evaluator, or more informative negative result.

We also add a taste/insight coverage audit over 39 gate records. It finds 2
complete `taste_insight` records: one scientific-taste prior encoding the
author's decision to move from an FML-centric benchmark story to a
claim-matched benchmark portfolio and high-tail evaluation, and one
operator-recorded priority gate choosing to measure attention/taste before
making stronger human-efficiency or taste-effect claims. The other 37 records
lack complete taste/insight fields. This is not a performance result. It does,
however, make the paper's distinctive human-taste claim operational:
prospective matched-budget runs must fill both `taste_insight` and
`attention_cost` before IGRE can test its high-tail hypothesis.

Because the central claim concerns human scientific taste in a co-pilot
research loop, the paper also needs human co-pilot usage data. We therefore add
a derived Human Co-Pilot Trace Dataset protocol. A survey of public interaction
datasets finds useful adjacent resources, including CoAuthor for collaborative
writing, CUPID for contextual preference interactions,
`neulab/agent-data-collection` for broad agent trajectories, and WebChain for
human-annotated web trajectories. None of these directly contains human
scientist interventions inside an AI Scientist-v2-style loop with linked
hypotheses, benchmark runs, code artifacts, claim audits, and manuscripts. The
primary dataset for this paper is therefore a single-author longitudinal Codex
co-pilot trace corpus derived from this project: gate records, artifact paths,
commit IDs, benchmark metrics, manuscript revisions, and claim-audit outcomes,
without releasing raw chat logs or credentials. The current derived snapshot
indexes 52 gate records, 35 records with attention-cost fields, 10 records with
taste/insight fields, 4 prospective matched packages, and 58 relevant commits.
This supports ecological and process claims, but not population-level claims
about all scientists.

We add a release-readiness audit for this dataset. The audit verifies required
top-level fields, gate schema coverage, explicit claim boundaries, and scans for
secret-like strings and raw-log markers. The current audit passes with 4
public-dataset survey entries, 52 gate records, 4 prospective packages, 58
commit-index entries, 0 secret-pattern hits, and 0 raw-log marker hits. This
permits release as a derived metadata case-study artifact, not as raw chat logs
or human-subject population data.

Following the latest paper-quality review, we made attention cost an explicit
auditable artifact rather than an informal metric. The human-gate schema now
contains an optional `attention_cost` object with active review minutes,
wall-clock latency, number of options reviewed, artifacts reviewed, and decision
count. We also added a strict coverage audit over 39 gate records: 9 standalone
human-gate logs and 30 embedded gates across 6 trajectory artifacts. The audit
finds 1 complete attention-cost record: an operator-recorded
measurement-readiness gate with 8.5 active review minutes, 9.67 wall-clock
minutes, 3 options reviewed, 4 artifacts reviewed, and 1 decision. The other 38
records still lack one or more required fields. This is an important
measurement-readiness result: the archived gates show decision provenance and
the logging path now works, but the package still cannot support any efficiency
claim about human attention. Future prospective matched runs must fill this
field before comparing co-pilot and autonomous variants.

We further add a prospective matched-budget package audit. This audit is a hard
evidence-shape gate rather than a result. A package passes only if it contains a
prospective co-pilot trajectory, a matched autonomous baseline on the same
task/model/tool budget, complete `attention_cost` and `taste_insight` records
for every human gate, a final claim audit, and a manuscript generated from the
same run. The repository now includes one passing controlled micro-pilot
package on a weighted Max-Cut task. This proves that the package shape can be
generated and audited on a real remote computation, but it is not
top-conference performance evidence: it does not use AI Scientist-v2 tree
search and does not evaluate paper quality.

We then upgraded this evidence shape to an AI Scientist-v2-style FML-bench
pilot. The new package runs fresh `Causality_causalml` co-pilot and autonomous
baselines under the same DeepSeek model and two-step budget, records complete
attention/taste fields for the human frontier gate, and writes a claim audit
plus mini-manuscript. The result is negative for co-pilot performance in this
small run: co-pilot test MAE is `0.646224`, while the matched autonomous run
reaches `0.624703` (lower is better). This is valuable because it verifies the
prospective evidence package on an AI Scientist-v2-style task while reinforcing
that superiority remains unproven.

We additionally report a metric-level prospective package summary rather than
only a pass/fail artifact audit. It currently contains three passing packages:
one controlled Max-Cut micro-task in which the human-selected branch wins on
mean normalized score (`0.984419` versus `0.596214`), and two FML-bench
Causality packages in which the autonomous run wins on test MAE (`0.624703`
versus `0.646224`, and `0.296399` versus `0.646224`). All three human gates have
complete attention-cost and taste/insight records. This summary is central to
the IGRE framing: human scientific taste is a logged, high-variance intervention
whose value must be tested across a distribution of research trajectories, not
assumed from a single favorable case.

Finally, we add a first matched mini-manuscript quality probe for the FML-bench
prospective package. The probe generates an autonomous mini-manuscript from the
same baseline evidence, anonymizes the co-pilot package manuscript as A and the
autonomous manuscript as B, and asks Monica-routed `gpt-4o-mini` and
`claude-3-7-sonnet-latest` to score claim calibration, evidence use,
methodological completeness, limitation honesty, clarity, and overall quality.
Both reviewers prefer A, with overall scores `4` versus `3`. The rationales
credit the co-pilot manuscript for stronger claim calibration and more explicit
limitations despite its worse benchmark score. This is only a
measurement-readiness result: the artifacts are short package manuscripts from
one FML task, not complete end-to-end generated papers.

To make this principle operational, we maintain a benchmark-to-claim matrix.
FML-bench Causality supports the branch-gate feasibility claim but does not yet
show general human-gate superiority. FML-bench Fairness supports the need for
evaluator gates because executable repairs and degenerate predictors reveal
metric-gaming risk. OpenEvolve function minimization, knapsack, Max-Cut,
MLAgentBench vectorization, and sklearn diabetes probes test the program-search
escalation policy under different subproblem types. ScienceAgentBench, MLE-bench Lite,
PaperBench, and AIRS-Bench remain expansion targets rather than current scored
claims. Future runs should therefore be chosen by the weakest unsupported claim,
not by convenience.

### 4.1 Preliminary Programmatic-Search Smoke Test

As an initial feasibility check, we ran OpenEvolve 0.2.27 on the SSH-controlled
Ubuntu host using DeepSeek through an OpenAI-compatible API. The task was a
small function-minimization evaluator with a random-search baseline. In one
OpenEvolve iteration, the system improved the evaluator score from 0.0345 to
0.0378 and saved a simulated-annealing-style evolved program. This result is
only a smoke test: it verifies the remote OpenEvolve path, evaluator loading,
model routing, checkpointing, and artifact capture. It does not yet establish
the paper-level claim that human-gated research improves final manuscript
quality.

We also ran a direct one-shot LLM-edit baseline with the same DeepSeek model,
initial program, and evaluator. The direct edit reached a score of 0.038021,
slightly above both the one-iteration OpenEvolve score of 0.037816 and a
five-iteration OpenEvolve score of 0.038007. This boundary result supports a
central design choice of Co-Pilot AI Scientist v3: programmatic search should be
controlled by an explicit escalation gate. For small budgets or simple local
rewrites, direct editing may be sufficient; for richer search spaces and larger
budgets, OpenEvolve-style population search can become the appropriate tool.

To test that latter case, we added a richer 0/1 knapsack heuristic task. The
initial value/weight greedy program reached an average optimality ratio of
0.991519 across 18 deterministic instances. A direct LLM rewrite improved this
to 0.995270. A five-iteration OpenEvolve run improved it further to 0.999439,
with no invalid instances. The evolved program introduced local improvement via
one-item and two-item removals followed by greedy refill. This provides a
positive example for the escalation gate: OpenEvolve-style search can be useful
when the subproblem has a richer combinatorial structure and an automatic
evaluator.

We then added a second controlled combinatorial task, weighted Max-Cut, to
avoid relying on one hand-built knapsack result. The starter program alternates
node labels and reaches normalized score 0.734680 against a deterministic
multi-start local-search reference over 16 graph instances. A direct DeepSeek
rewrite improves the score to 0.962237. A five-iteration OpenEvolve run with
the same model and evaluator reaches 0.970833, improving over the direct rewrite
by 0.008596 with no invalid instances. The margin is small and from one seed,
but it is a second positive algorithmic subproblem result. Combined with the
negative function-minimization boundary case, it supports the selective
program-search gate rather than an unconditional OpenEvolve policy.

### 4.2 Retrospective AI Scientist-v2 Branch-Gate Replay

We also replayed two existing AI Scientist-v2 FML-bench smoke runs. In the
Causality_causalml run, the first draft achieved the best validation MAE
observed in the four-step run (0.598943 versus a baseline of 1.296259), while
the second draft and later refinements failed to improve it. A branch gate after
two drafts would have kept the first branch and avoided at least one low-value
follow-up. In the Fairness_fairlearn run, the first draft worsened the baseline
fairness metric (0.316467 versus baseline 0.186632), the second attempt failed
with a Fairlearn compatibility issue, and later attempts were either worse or
buggy. A human branch gate would have paused the branch and routed the system to
an evaluator or algorithm reset. This replay evidence is not a substitute for an
online human-gated benchmark, but it shows that the logged AI Scientist-v2
trajectory contains actionable checkpoints for human co-pilot intervention.

### 4.3 Live AI Scientist-v2 Branch-Gate Probe

To move beyond retrospective replay, we ran a new live FML-bench probe on the
Ubuntu host. We configured AI Scientist-v2 on Causality_causalml with a
two-step budget, two draft ideas, two simulated parallel workers, and a temporary
stage-budget schedule that assigns all budget to the first stage. This produced
a real two-branch frontier before a branch gate. The first draft obtained
validation MAE 1.149610, while the second draft obtained validation MAE
0.621262; lower is better. The structured branch gate therefore selected the
second draft and pruned the first. The benchmark's automatic final test on the
selected validation branch reported test MAE 0.640451.

This live probe demonstrates that the proposed branch gate can be inserted at a
real AI Scientist-v2 decision frontier and can make a clear budget-allocation
decision from logged metrics and code snapshots. It does not yet prove that
human gating outperforms autonomous AI Scientist-v2, but it gives a concrete
frontier on which such a comparison can be built.

We then implemented a minimal selected-branch continuation runner. The runner
temporarily applies the human-selected code snapshot to the official FML-bench
task template, launches a short AI Scientist-v2 continuation run, and restores
the template afterward. Starting from the selected second draft, a two-step
continuation reached validation MAE 0.401240 and test MAE 0.402170. This is
better than the live two-draft gate run's test MAE of 0.640451 and also better
than the earlier four-step autonomous smoke run's test MAE of 0.617719. The
comparison is still preliminary because continuation is implemented by snapshot
seeding rather than by preserving the original in-memory tree object, and it
uses only a single small task and seed. Nevertheless, it demonstrates an
executable path from branch gate, to selected snapshot, to additional
AI Scientist-v2 search budget.

Following the paper-quality review, we added closer matched-budget autonomous
baselines. The first matched run used the same Causality_causalml task, the same
DeepSeek model, two initial ideas, two parallel branches, and four total AI
Scientist-v2 steps, but no human branch selection. It reached validation MAE
0.389451 and test MAE 0.421474. In this pair, the human-gated path remained
slightly better on held-out test MAE (0.402170 versus 0.421474), while the
autonomous baseline was slightly better on validation MAE.

We then ran a second matched Causality replicate. The human-gated two-draft
frontier selected a branch with validation MAE 0.605881 and test MAE 0.646224.
The snapshot-seeded continuation did not improve the held-out test score,
ending with validation MAE 0.627837 and test MAE 0.646224. The matched
autonomous four-step baseline reached validation MAE 0.537972 and test MAE
0.595685. In this second pair, the autonomous path was better on both
validation and held-out test metrics.

Across the two matched pairs, one pair favors human-gated continuation and one
favors the autonomous baseline on held-out test MAE. Mean human-gated test MAE
is 0.524197, while mean autonomous test MAE is 0.508579. Since lower is better,
the two-pair mean slightly favors the autonomous baseline. The evidence
therefore removes one compute-budget confound but remains mixed; it supports
feasibility of branch-gate insertion and continuation, not general human-gate
superiority.

We now also generate this FML matched-comparison aggregate with a script rather
than relying only on the hand-written table. The generated audit reports one
human-gated win and one autonomous/tie win across the two formal pairs, mean
autonomous-minus-human delta `-0.015618`, delta SEM `0.034921`, and statistical
claim `not_supported_n_too_small`. The separate online-smoke comparison is also
negative for co-pilot performance (`0.862015` versus `0.428516` test MAE). This
scripted summary is the current authoritative FML performance evidence.

After this audit, we ran a second prospective two-step FML package with the
same task, model, tool access, and budget shape as the first prospective
package. The co-pilot branch again reached test MAE `0.646224`, while the
matched autonomous baseline reached `0.296399`. Across the two prospective
two-step FML packages, the autonomous baseline wins both comparisons; mean
autonomous-minus-human delta is `-0.185672` with SEM `0.164152`. This result
strengthens the negative average-performance evidence while leaving the
high-tail taste/insight hypothesis open for future larger-budget studies.

We then extended the prospective package runner beyond the repeated Causality
workspace to the other FML-bench workspace available on `ubuntu-heshi`,
`Fairness_fairlearn`. This package is also negative for the co-pilot path, but
for a different reason: both co-pilot branch candidates failed validation, so
the logged frontier gate selected `abort_no_valid_branch` rather than forcing a
continuation. The matched autonomous run completed with test primary metric
`0.172152` (`abs_demographic_parity_diff_mean`, lower is better). The generated
package audit now finds four passing prospective packages, all with complete
attention-cost and taste/insight gate records: one controlled micro-task win,
two negative Causality FML packages, and one Fairness FML invalid-continuation
case. This broadens the benchmark shape but makes the average-performance
story more conservative, not stronger.

### 4.4 Non-FML Benchmark and Program-Search Probe

Following the benchmark-selection principle above, we also used MLAgentBench as
a non-FML evaluation source. We cloned MLAgentBench on the Ubuntu host and first
ran its lightweight `vectorization` task with the built-in `Agent` baseline,
which simply executes the starter `train.py` and submits the result. The
official baseline completed with final score 3.172504 seconds and total
benchmark time 3.365531 seconds, with no reported error flags.

We then wrapped the same task in a stricter local evaluator: before accepting a
runtime, the evaluator compares the candidate `Conv2DLayer.forward` output
against a nested-loop reference on a deterministic small input. Under this
controlled evaluator, the starter program had median runtime 3.261186 seconds.
A direct DeepSeek `deepseek-chat` rewrite produced plausible vectorized code but
failed the correctness gate due to a numerical mismatch. In contrast, a
three-iteration OpenEvolve-style run using the same DeepSeek model found a
correct candidate at iteration 1 with median runtime 0.051882 seconds, a 62.86x
speedup over the controlled starter program. This result supports the narrower
claim that the program-search-escalation node can be valuable on
machine-gradeable subproblems beyond FML-bench. It does not yet prove that the
full co-pilot architecture improves whole-paper quality.

To test robustness, we repeated the same three-iteration OpenEvolve setup with
additional random seeds. Across seeds 0, 1, 2, 3, 4, 7, 42, and 123, all eight
runs retained a correct best program and improved over the controlled starter.
The median best runtime was 0.024581 seconds, corresponding to a median speedup
of about 132.67x over the starter runtime. Six of eight seeds found a
sub-0.1-second program. The result is still not deterministic under tiny
budgets: seed 7 only achieved a weak 1.09x speedup and seed 1 achieved a 15.57x
speedup. This strengthens the evidence that the program-search module can find
useful code transformations, while preserving the important caveat that search
quality varies substantially by seed and budget.

To avoid making the non-FML evidence only about low-level runtime optimization,
we added a second controlled probe using the built-in sklearn diabetes tabular
regression dataset. This probe does not require Kaggle credentials and should
not be reported as an official MLAgentBench score. It starts from a deliberately
rudimentary mean predictor with mean RMSE 78.572189 across five deterministic
splits. A direct DeepSeek rewrite recovered a standard Ridge-style baseline with
mean RMSE 55.895460. Three 3-iteration OpenEvolve seeds also improved strongly
over the mean predictor, with best RMSEs 55.895460, 55.946535, and 55.895460.
The median OpenEvolve RMSE was 55.895460, matching the direct rewrite. This
result broadens the benchmark coverage to a tabular modeling subproblem, but it
also gives an important boundary condition: when the improvement is a standard
small modeling change, direct editing can be as effective as program search.
Thus the program-search gate should be selective, not automatic.

We also attempted three benchmark-expansion probes. First, we tried to add a
second official MLAgentBench `debug` task, which maps to CIFAR10. The setup
probe repaired a missing `torchvision` dependency by installing the matching
CPU wheel for the local `torch` version, but the run stopped during dataset
preparation because the 170 MB CIFAR10 archive was downloading too slowly for
the interactive budget. Second, we probed ScienceAgentBench. The repository was
present on the Ubuntu host, and its README points to the April 2026 verified
split and `benchmark_verified.zip`, but the local benchmark directory did not
contain the verified artifacts and the HuggingFace metadata request failed with
`[Errno 101] Network is unreachable`. Third, we probed the official
MLAgentBench `imdb` folder. After installing the missing `datasets` dependency
required by its official `eval.py`, even a five-example dataset load failed
with the same HuggingFace network error. We therefore report these as setup
artifacts and not as benchmark scores. The next official non-FML score requires
pre-cached data or a different network path, not a convenient retreat back to
FML-bench alone.

### 4.5 Claim Audit

We ran a claim-evidence audit after the pilot experiments. A Monica-routed
`gpt-4o-mini` review classified the core architecture contribution as
reasonable but warned that the empirical evidence does not yet support broad
claims that human gates improve paper quality or that the full co-pilot system
outperforms autonomous AI Scientist-v2. We therefore treat those as hypotheses
for the evaluation protocol rather than as conclusions. The audit supports only
the narrower empirical claims reported above: OpenEvolve-style search can help
on some machine-gradeable subproblems but is seed-sensitive under tiny budgets,
direct editing can match OpenEvolve on a simple tabular modeling probe,
branch-gate insertion is feasible in AI Scientist-v2-style logs, evaluator
gates must reject non-executable and metric-gaming branches before
continuation, and the first two matched Causality pairs give mixed evidence
rather than a reliable human-gating advantage. A first attempt to extend online
branch gating to `Fairness_fairlearn` produced two validation failures rather
than a score, so we archive it as failure-mode evidence rather than
matched-budget performance evidence. A follow-up evaluator-gate repair probe
made the lesson sharper: an API-repaired fairness candidate was executable but
worse on demographic parity difference (test 0.317603 versus the baseline
0.173030), while a degenerate all-negative predictor achieved a perfect target
metric of 0.000000 but collapsed balanced accuracy to 0.500000. For fairness
tasks, the gate therefore needs both an execution check and a utility floor
before accepting a branch.

We also ran a refreshed paper-quality review through two Monica-routed reviewer
models after adding the prospective matched-budget metric summary. `gpt-4o-mini`
gave a weak-accept recommendation with scores of 4/5 for novelty and
reproducibility but 3/5 for rigor and evidence. `claude-3-7-sonnet-latest` was
stricter and gave a reject recommendation for a strong ML/NLP systems venue,
mainly because the central human-gating and paper-quality claims remain
unsupported, the strongest FML-bench prospective package is negative for
co-pilot performance, and the system still lacks a paper-generating end-to-end
comparison. Both reviewers converged on the same required next step: run
autonomous AI Scientist-v2 and human-gated variants under equal budgets across
more tasks and seeds, measure human attention cost, and separate completed
system evidence from future plans more sharply.

## 5. Current Contributions and Unproven Claims

The current contributions are:

1. A modular architecture for collaborative automated research.
2. A formal schema for human intervention nodes in research agents.
3. A live Monica-routed hypothesis-frontier smoke that generates four new
   research-frontier candidates, critiques/ranks them, and selects
   `frontier_004` for possible next-budget evaluation.
4. A same-model autonomous hypothesis-front-end baseline probe that compares
   the archived IGRE frontier portfolio with an autonomous AI Scientist-v2-style
   portfolio and scores IGRE `4` vs. autonomous `3` as front-end planning
   evidence only.
5. An offline expert-review taste-prior data probe over Hugging Face
   `nhop/OpenReview`, using streaming access to sample 160 rows from a 34,638-row
   expert-review corpus and verifying that it can support limited scientific
   taste-prior experiments.
6. A participation-mode selection probe that uses OpenReview-conditioned
   scoring to compare no-gate, taste-prior, evaluator-stress,
   structured-feedback, and claim-calibration modes, finding
   structured-feedback and claim-calibration as the current top pair.
7. An OpenReview-guided regeneration probe whose initial three-paper run gives
   `3/3` review-guided wins and whose expanded six-paper run gives `5/6`
   review-guided wins under the generating model's scorer, with a stricter
   Claude cross-model review giving `3/6` review-guided wins, `1/6` baseline
   win, and `2` ties.
8. A review-insight taxonomy probe over 32 OpenReview review cases and a
   deterministic review-utility map over 473 review snippets from 160 sampled
   papers; together they map novelty, evaluation, claim-boundary, clarity,
   reproducibility, and correctness signals to IGRE gates while separating
   actionable review insight from generic praise or vague reactions.
9. A same-manuscript structured-feedback probe that operationalizes
   `frontier_004` and compares informal feedback with IGRE-structured feedback
   through two revisions and a fixed-rubric model score.
10. A retrospective full-gate trajectory showing idea, evaluator, branch,
   program-search, and claim-audit gates serialized under the shared schema.
11. A rerunnable full-gate trace script that recomputes the gate chain from
   archived experiment summaries while marking the output as artifact replay.
12. A first online full-gate smoke trajectory that exercises idea, evaluator,
   branch, program-search, and claim gates in one remote run, while producing a
   negative continuation outcome.
13. An evaluation protocol for measuring both mean benchmark performance and
   high-tail scientific upside under human intervention.
14. Initial remote OpenEvolve and FML-bench probes showing that the
   verifiable micro-evolution and frontier-steering operators can run on the
   Ubuntu host.
15. Two matched-budget FML-bench Causality comparisons between a human-gated
   branch continuation and a four-step autonomous AI Scientist-v2 baseline,
   with mixed outcomes.
16. A same-FML-step autonomous baseline for the first online full-gate smoke,
   showing a negative performance result for the human-gated continuation.
17. Non-FML program-search probes for runtime optimization and tabular
   regression, broadening benchmark coverage beyond FML-bench.
18. A reusable Codex skill for running the workflow.
19. Bilingual paper, usage artifacts, and claim-audit artifacts for
   reproducibility.
20. A Monica-routed paper-quality review artifact that records external model
   criticism before the next revision.
21. A human-gate attention-cost audit over 39 gates showing 1 complete
   operator-recorded attention-cost event and 38 incomplete records; future
   prospective experiment gates must record these fields before making
   attention-efficiency claims.
22. A taste/insight coverage audit showing 2 complete scientific-taste prior
   records and 37 gates that still lack complete taste/insight fields.
23. A prospective matched-budget package validator that defines the minimum
   non-synthetic evidence shape required before claiming paper-quality gains,
   human-attention efficiency, or superiority over autonomous AI Scientist-v2.
24. A controlled prospective Max-Cut micro-pilot package that passes this
   validator, with complete attention/taste logging, matched baseline metrics,
   claim audit, and same-run manuscript artifact.
25. Two prospective FML-bench Causality packages with complete attention/taste
   logging and matched autonomous baselines, both yielding negative co-pilot
   performance results in the small two-step setting.
26. A prospective package metric summary that separates passing audit packages
   by task, metric direction, co-pilot score, autonomous score, and claim
   implication; the current result is one positive controlled micro-task, two
   negative Causality FML-bench packages, and one Fairness_fairlearn invalid
   continuation package.
27. A matched mini-manuscript quality probe for the FML package, where
   Monica-routed `gpt-4o-mini` and `claude-3-7-sonnet-latest` both prefer the
   co-pilot package mini-manuscript over a generated autonomous
   mini-manuscript, with overall scores of 4 versus 3.
28. A matched full-manuscript generation probe that renders the same archived
   FML evidence into two complete paper-shaped manuscripts and scores them
   with a deterministic internal rubric; the co-pilot manuscript scores 4.18
   overall for structure, grounding, calibration, and method distinctness,
   while the autonomous manuscript scores 4.11 and is the only variant with a
   valid scalar FML test metric in the Fairness package.
29. A repeated same-continuous-trajectory paired online full-gate
   manuscript-production summary over three smoke runs, including one
   `Fairness_fairlearn` no-valid-branch failure trajectory; the valid
   Causality benchmark aggregate has `0` co-pilot wins, `1` autonomous win,
   and `1` tie, while Monica-routed model-review probes prefer the co-pilot
   manuscript in `6/6` reviewer calls.
30. A derived Human Co-Pilot Trace Dataset protocol that positions the author's
   real Codex sessions as a single-author longitudinal process corpus after
   privacy-preserving metadata extraction.

The current evidence does not yet prove that human gates improve paper quality
or that the full co-pilot system outperforms autonomous AI Scientist-v2. The
structured-feedback probe is a measurement artifact for one manuscript, not a
replacement for independent expert review. Those stronger claims remain targets
for the next benchmark stage.

## 6. Limitations

This proposal does not assume that human involvement always helps. Human gates
can introduce bias, slow search, reduce exploration, and in short-budget
benchmarks they may underperform a fully autonomous search policy. That is not
a side note; it is part of the method's intended evaluation. IGRE treats human
scientists as high-variance search operators whose value may appear in the
upper tail rather than the mean: better problem taste, a more revealing
evaluator, a sharper interpretation of failure, or a willingness to pursue a
riskier but more original direction. Programmatic search can likewise optimize
local metrics without improving scientific contribution, and under tiny budgets
it may not outperform direct LLM editing. Expert paper ratings are costly and
may vary across reviewers. The first version should make narrow claims and
report negative results when gates fail to improve outcomes. The current
selected-branch continuation evidence is mixed across two matched pairs and is
not yet a statistically controlled benchmark. The retrospective full-gate
trajectory and executable artifact replay show the schema, decision chain, and
reproducible traversal logic. The online smoke trajectory does exercise all five
gates in one remote run, but it uses a tiny budget, mixes an FML branch task
with a knapsack program-search subproblem, and produced a worse continuation
test score. A same-FML-step autonomous baseline also outperformed the
human-gated continuation. Stronger claims require more tasks, more seeds,
richer budget schedules, larger online trajectories, independent paper-quality
review, and metrics that capture rare high-quality research outcomes rather
than only average task score.

The current human-gate logs also lack measured attention cost. We can count
decision artifacts, but cannot yet compute active review minutes or
wall-clock latency. This prevents any claim that the proposed gates improve the
ratio of research quality to human effort. The next matched-budget experiments
must record attention cost prospectively.

The new prospective matched-budget package audit now passes on one controlled
micro-pilot, two FML-bench Causality pilots, and one FML-bench Fairness pilot.
This is progress in evidence shape, not in final empirical strength. The FML
packages are negative or invalid-continuation cases for co-pilot average
performance at this budget, and the packages do not provide independent expert
evaluation of full paper quality. The paper therefore remains at pilot-system
evidence until larger prospective experiments exist.

The derived Human Co-Pilot Trace Dataset improves ecological validity because it
comes from the author's real Codex workflow, but it is still a single-author
longitudinal process corpus. It can support process and case-study claims; it
cannot by itself support population-level claims about scientists in general.
The release audit reduces privacy and leakage risk by checking for secret-like
strings and raw-log marker fields, but it is not a substitute for institutional
human-subject review if the dataset is later expanded to multiple researchers.
The OpenReview/Hugging Face expert-review evidence is therefore a legitimate
source of human scientific taste and insight, but it is an offline and
asynchronous source rather than a live co-pilot trajectory. It can guide
artifact regeneration, participation-mode selection, review-insight taxonomy
construction, and deterministic review-utility mapping, as shown by the four
OpenReview probes above. What it does not contain is real-time human decisions
inside a co-pilot
automated-research loop. A true online human-guided
automated-science dataset would require a broadly deployed skill or research
assistant used by many scientists, with consent, de-identification, artifact
linking, and prospective logging of interventions, attention cost, and
downstream outcomes. At present, this is more likely to be feasible for major
agent or foundation-model platforms than for a single-author pilot project, so
we treat it as a central future-work direction rather than as evidence already
available in this paper.

The full-manuscript probe reduces one specific gap but does not close the
top-conference evidence gap. It shows that archived FML packages contain enough
structured evidence to generate two complete, claim-calibrated manuscripts
under a matched prompt-free template. The latest Fairness probe scores the
co-pilot manuscript 4.18 and the autonomous manuscript 4.11 on the internal
rubric, but the autonomous manuscript is the only variant with a valid scalar
FML test result. The repeated same-continuous online smoke summary now shows
that fresh online co-pilot trajectories can produce complete manuscript-shaped
artifacts and same-run autonomous manuscript comparators. Across the two valid
Causality paired smokes, benchmark outcomes are `0` co-pilot wins, `1`
autonomous win, and `1` tie, with mean test MAE `0.754120` for co-pilot and
`0.643337` for autonomous. The third `Fairness_fairlearn` paired smoke is a
no-valid-branch failure trajectory rather than a scored performance comparison.
Monica-routed model reviewers prefer the co-pilot manuscripts in `6/6` calls,
but this is a measurement-readiness signal rather than expert review. This is
exactly why the co-pilot claim must remain about method distinctness,
scientific taste logging, and high-tail research search rather than average
short-budget benchmark superiority.

The taste/insight evidence is also only at the logging-readiness stage. The
archive now contains two complete scientific-taste prior records: one grounded
in the author's instruction to broaden benchmarks and foreground high-tail
research taste, and one operator-recorded decision to prioritize attention/taste
measurement over more weak benchmark runs. Neither record shows that the
decision improved downstream research outcomes. Future runs must log taste
rationales prospectively rather than reconstructing them from successful
outcomes.

The current implementation now has smoke-level repeated same-continuous-
trajectory paper-generating comparisons, but it is still too small for a
systems-paper claim. The next systems-paper draft must report larger matched
trajectory pairs across tasks and seeds, from hypothesis generation to final
claim-audited manuscripts.

## 7. Conclusion

Co-Pilot AI Scientist v3 reframes automated scientific discovery as
insight-gated research evolution. The system preserves the strengths of
autonomous agents while giving human scientists explicit, logged, and
experimentally testable points of influence. Its strongest claim is not that
humans always improve average benchmark performance. The deeper claim is that
human scientific taste and insight can reshape the search distribution toward
rarer, more original, and potentially field-opening outcomes. If future matched
benchmarks support this high-tail hypothesis, co-pilot research systems may
produce better papers not by removing humans from science, but by using human
attention where it can change what kind of science is attempted. The present
paper should be read as a reproducible system proposal with pilot evidence, not
as a final proof of superiority.
