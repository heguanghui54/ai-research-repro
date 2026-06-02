# Co-Pilot AI Scientist v3: Insight-Gated Research Evolution for Collaborative Automated Science

## Abstract

Automated research agents can now propose hypotheses, run experiments, write manuscripts, and optimize code, but they still lack a principled way to use human scientific taste: the non-metric judgement that some problems, failures, mechanisms, or claim boundaries are more worth pursuing than others. Generic co-pilot workflows usually treat humans as approvers or editors, while fully autonomous systems remove the very judgement that often determines whether a research direction is important. We introduce Insight-Gated Research Evolution (IGRE), a workflow architecture that converts human taste and expert-review insight into explicit control signals inside AI Scientist-v2-style research loops. IGRE uses six gates: scientific-taste prior, evaluator stress test, frontier steering, verifiable micro-evolution, structured feedback, and claim calibration. We further introduce Temporal Frontier Replay (TFR), an offline replay protocol that asks whether historical peer reviews would have moved an automated researcher toward later field trajectories. Together, IGRE and TFR make human participation measurable rather than assumed beneficial: gates are logged with evidence, attention cost, and claim boundaries, while historical review signals are replayed against future-frontier evidence. We evaluate the package with FML-bench style runs, OpenEvolve-style micro-evolution probes, OpenReview-derived expert-review signals, paired manuscript probes, TFR audits, and clean-clone reproducibility checks. The current evidence supports a conservative claim: expert review text can be mapped into actionable workflow gates, review-guided regeneration improves some research artifacts under cross-model review, TFR is operationalized but currently negative for delayed-value evidence, and short-budget human-gated FML runs are mixed or negative rather than automatically superior. This is therefore not a proof that humans always improve automated science. It is a reproducible method for designing, comparing, and auditing the modes by which human insight can alter scientific search.

## 1. Introduction

The recent wave of AI research agents has made a strong case for automation. Systems such as AI Scientist-v2 can generate ideas, run experiments, and produce papers. AI Co-Scientist-style systems organize hypotheses through generate, debate, and evolve loops. AlphaEvolve demonstrates that language models can drive evolutionary code search when candidate programs can be evaluated automatically. These systems expose a tempting conclusion: if the benchmark and evaluator are clear, the human can be removed from the loop.

Scientific research, however, is not only a process of optimizing a visible metric. Researchers also decide which questions are deep, which failure is informative, which mechanism is worth isolating, and which result is too weak to claim. These judgements are often called taste or insight. They are not fully captured by benchmark scores, but they are not mystical either: they appear concretely in paper reviews, rebuttals, lab discussions, claim audits, and decisions to abandon or reframe a direction.

This paper asks a narrower and more useful question than whether human participation is always better than full automation. The question is: which forms of human participation can be turned into workflow-control signals that improve the search process or the accountability of automated research? This framing matters because human involvement is high-variance. A human gate may steer the system toward a rare high-value idea, but it may also slow the run, inject bias, overfit to taste, or choose a worse branch than the autonomous policy. A credible co-pilot method must therefore measure both positive and negative effects.

We propose Insight-Gated Research Evolution (IGRE), the core algorithmic pattern of Co-Pilot AI Scientist v3. IGRE is inspired by prior automated-research systems, but it is not a direct collage of them. The method adapts their ideas around a different object: not autonomous discovery alone, but the insertion of human scientific taste into the parts of the loop where non-metric judgement is useful and dangerous. IGRE treats human insight as a logged search operator. It can modify the prior over research directions, stress the evaluator, steer the hypothesis frontier, trigger small verifiable program searches, structure manuscript feedback, or calibrate manuscript claims.

The primary claim of this paper is therefore deliberately narrow: expert review and human scientific judgement can be operationalized as auditable workflow-control signals, and the usefulness of those signals can be compared experimentally. We do not claim that the current co-pilot system outperforms autonomous AI Scientist-v2. The current paper makes four contributions. First, it defines IGRE as a six-gate architecture for human-guided automated science. Second, it releases a reproducible evidence package with an English manuscript, scripts, logs, gate schemas, audits, and a reusable Codex skill. Third, it introduces Temporal Frontier Replay (TFR), an offline protocol for using historical peer reviews to test whether human insight would have steered automated research toward later field trajectories. Fourth, it reports mixed and negative short-budget results alongside positive workflow probes, keeping the claim boundary explicit: IGRE currently supports workflow design and measurement readiness, not a top-conference-level proof of co-pilot superiority.

![Figure 1. Co-Pilot AI Scientist v3 combines AI Co-Scientist-style hypothesis frontiers, AI Scientist-v2-style experiment and paper production, OpenEvolve-style micro-search, and six human insight gates. The lower panel shows why frontier-aware evaluation uses vector movement and metric disagreement rather than a single short-term score.](figures/igre_frontier_main_figure.png)

## 2. Related Work

End-to-end automated scientists. The AI Scientist introduced an automated machine-learning research loop that proposes ideas, writes code, runs experiments, produces figures and manuscripts, and applies an automated reviewer. AI Scientist-v2 extends this line with progressive agentic tree search, broader ML domains, and workshop-level autonomous paper generation. AI Co-Scientist systems instead emphasize multi-agent hypothesis generation, debate, ranking, and evolution over biomedical research goals. These systems motivate IGRE's end-to-end setting, but they do not make human scientific taste a first-class control variable. IGRE asks where a human or review-derived signal should enter the loop, how much attention it costs, and whether it changes the downstream search trajectory.

Scientific discovery agents beyond ML. Coscientist and ChemCrow show that LLM agents can connect literature reasoning, tool use, and chemistry workflows; related systems in materials science and scientific hypothesis generation explore domain-specific agent scaffolds. These works strengthen the case that automated discovery is not only an ML-paper-writing problem. IGRE is complementary: it does not propose a new wet-lab or domain-tool stack, but a participation-mode layer for deciding when expert insight should reshape the problem, evaluator, frontier, or claim boundary.

Program search and algorithm discovery. AlphaTensor, AlphaDev, FunSearch, and AlphaEvolve demonstrate that learned search, LLM-guided program evolution, or evolutionary coding agents can discover algorithms and optimize real computational infrastructure when candidates can be evaluated automatically. OpenEvolve provides an open implementation inspired by AlphaEvolve-style evolutionary coding. IGRE uses this family selectively through the verifiable micro-evolution gate. It treats program evolution as an escalation operator for machine-gradeable subproblems, not as the universal form of scientific reasoning.

Self-referential program search before LLMs. A longer lineage of AI self-improvement predates current LLM agents. Schmidhuber's 1987 work on evolutionary principles in self-referential learning treated learning-how-to-learn as a setting in which learning procedures can inspect and modify their own machinery. His later Optimal Ordered Problem Solver (OOPS) organized incremental universal search over programs and search procedures; the Gödel Machine formalized fully self-referential problem solvers that rewrite their own software after proving an expected improvement; and POWERPLAY continually searched for new tasks together with solver modifications that preserve all previously solved tasks. These works matter for IGRE because they frame self-improvement as a problem of ordered search, verification, and preservation of previous competence, not merely as repeated prompting. Recent Darwin Gödel Machine and Huxley-Gödel Machine work revisits this tradition with coding agents that modify agent codebases and select self-modification branches using benchmark, archive, or metaproductivity signals. IGRE is not itself a self-modifying agent architecture, but its verifiable micro-evolution gate borrows the same discipline: branch changes should be evaluated, archived, and claim-bounded rather than treated as free-form creativity. The difference is central: IGRE evolves research trajectories and bounded subproblem code under human-insight gates, rather than directly optimizing an autonomous agent's own source code.

LLM-guided evolution and reflective improvement. PromptBreeder, EvoPrompting, Evolution of Heuristics, ReEvo, multi-objective heuristic evolution, LLM-as-evolution-strategy work, and recent algorithm-discovery systems combining evolutionary search with reinforcement learning all show that LLMs can serve as mutation operators, reflective evaluators, heuristic generators, or learned search policies. Self-Refine, Reflexion, Voyager, and AutoGen demonstrate related feedback, reflection, skill-library, and multi-agent conversation patterns. IGRE differs from these self-evolution lines by keeping the object of evolution outside the model itself: the research trajectory is evolved under explicit human gates and evidence audits.

Benchmarks for research agents. MLAgentBench, MLE-bench, and FML-bench provide complementary ways to evaluate agents that perform machine-learning experimentation, engineering, or research-strategy search. Newer paper-scale and lifecycle benchmarks such as PaperBench, AIRS-Bench, RExBench, ReplicationBench, and SciVisAgentBench sharpen this point: realistic scientific agents must replicate papers, implement research extensions, analyze experiments, and handle domain-specific scientific workflows, not merely produce plausible manuscripts. They are essential because co-pilot claims should not rest only on polished manuscripts or model-judge preferences. IGRE therefore reports matched autonomous and human-gated probes, including negative short-budget results, and uses benchmark disagreement as evidence about when human taste should or should not override metric-driven search.

Human feedback, peer review, and scientific taste. Generic co-pilot systems often treat humans as approvers, prompt writers, preference labelers, or editors. IGRE makes a different algorithmic claim: human input should be classified as a search-control signal, logged with rationale and attention cost, and tested against downstream outcomes. OpenReview-style peer-review data is useful here because real reviews contain judgements about novelty, evaluation, correctness, clarity, impact, and claim boundaries. Such data is noisy and retrospective, but it is one of the few public traces of expert scientific taste. IGRE uses it as an offline testbed for participation-mode design rather than as a substitute for future live human co-pilot traces.

## 3. Method: Insight-Gated Research Evolution

IGRE models a research run as a sequence of machine actions interrupted by explicit gates. Each gate can alter the next action, but it must record the reason, evidence, cost, and claim boundary. This makes human involvement auditable and comparable to autonomous baselines.

The first gate is the scientific-taste prior. It selects or reweights research directions before expensive experimentation. A useful taste prior is not a vague preference. It should explain why a direction has depth, novelty potential, mechanistic value, failure informativeness, benchmark fit, or asymmetric upside. In the current package, OpenReview novelty and impact comments are used as an offline proxy for this gate.

The second gate is the evaluator stress test. It asks whether the metric is too easy, too narrow, or gameable. In automated science this is crucial because an agent can optimize the evaluator while missing the scientific target. Review comments about missing baselines, weak metrics, leakage, poor ablations, or invalid comparisons are routed here.

The third gate is frontier steering. It operates over a portfolio of hypotheses or implementation branches. Rather than approving one output at the end, the human or review-derived signal chooses which part of the search frontier should receive more budget. This gate is useful when the best direction is not simply the one with the best early score.

The fourth gate is verifiable micro-evolution. It applies OpenEvolve-style program search to narrow machine-gradeable subproblems such as heuristic design, vectorization, tabular modeling, or small combinatorial objectives. IGRE treats this as an escalation operator. Direct editing remains preferable when the task is simple, when evaluation is expensive, or when search adds little beyond a strong baseline.

The fifth gate is structured feedback. It converts human or review-derived comments about clarity, reproducibility, missing definitions, organization, and reader burden into an explicit revision plan. This gate matters because many valuable reviews do not change the algorithm or benchmark, but change whether the resulting research artifact is understandable, reproducible, and comparable.

The sixth gate is claim calibration. It edits the manuscript-level interpretation of evidence. This gate is not cosmetic. It decides whether a result supports superiority, feasibility, measurement readiness, a negative result, or only a future-work claim. Many expert reviews are useful precisely because they force this boundary.

The gates form the following algorithmic loop. The system proposes a research frontier, evaluates early artifacts, maps human or review-derived signals into gate actions, updates the frontier or evaluator, optionally performs micro-evolution, and finally writes a claim-audited manuscript. Every gate has a structured record containing the gate type, artifact reviewed, options considered, decision, rationale, expected upside, possible harm, attention cost, and downstream evidence. This structure is what distinguishes IGRE from informal co-pilot interaction.

IGRE also defines a cross-gate meta-policy, the Long-Horizon Taste Gate (LHTG).
LHTG is the part of the method that operationalizes the paper's central
intuition: a human review may make the next artifact worse under short-term
quality scores, yet still move the research trajectory toward a future
mainstream or SOTA direction. LHTG searches for delayed-value review signals
(DVRS), meaning review or human-gate interventions that combine short-term
friction with long-horizon directionality. A DVRS is not treated as automatically
correct. It is routed into the appropriate IGRE gate, queued for TFR replay, and
audited against both immediate artifact quality and later frontier alignment.
This makes the paper's method distinct from generic co-pilot assistance:
scientific taste is modeled as a selective, risky, testable search override
rather than as approval, preference labeling, or extra context.

IGRE also includes an offline learning and evaluation mode, Temporal Frontier Replay (TFR). TFR is the mechanism that turns retrospective peer-review data into a test of scientific taste rather than merely another paper-quality rubric. Given a historical paper at time `t`, its reviews, and later field evidence at `t + delta`, TFR constructs three replay conditions: paper-only, review-guided, and shuffled-review-control. It then asks whether the review-guided replay improves only local artifact quality, or whether it also moves the generated research plan toward later mainstream or SOTA directions. A delayed-value signal is the temporally asymmetric case: review guidance may make the immediate artifact worse under short-term scores, but better aligned with later field evolution. This is the specific kind of human taste that IGRE is designed to preserve.

TFR is not an extra borrowed benchmark. It is an adaptation required by the co-pilot question. Standard benchmark comparison measures whether a branch wins now. TFR measures whether a human comment changes what the agent should search for later. In the current package, TFR is implemented through a deterministic smoke, a citation-backed frontier probe, direct review-frontier signal mining, and a semantic frontier judge. These probes are still small and currently negative for delayed-value evidence, but they make the high-tail hypothesis falsifiable: useful human insight must be routed, replayed, and tested against a future frontier, not assumed valuable because it came from a human reviewer.

## 4. Experiments

The experiments are designed around participation-mode selection, not around proving that humans always beat automation. The evidence package asks four questions.

The main quantitative evidence is summarized below. The table intentionally mixes positive, mixed, and negative results because IGRE is evaluated as a gate-selection framework, not as a guaranteed performance booster.

| Probe | Co-pilot or review-guided result | Baseline or autonomous result | Delta or win count | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Review utility map | 398 actionable snippets | 64 noisy snippets | 473 snippets total | Expert reviews contain routeable taste/insight signals. |
| Gate-structure ablation | full IGRE utility capture 1.000 | best single gate 0.369; random gate mean 0.199; no-gate 0.000 | full vs. best single +2359 utility units | Multi-gate routing is needed because review insight is heterogeneous; this is routing evidence, not downstream quality proof. |
| Held-out review-gate validation | full selected policy utility capture 1.000 | best single gate 0.374; random category mean 0.706; no-gate 0.000 | 94 held-out reviews from 32 papers | Paper-level train/held-out split reduces sample-reuse bias for review-to-gate routing; not independent human labels. |
| Gate-outcome attribution | full IGRE aligned score 75.17 | best single gate 37.25; random gate mean 15.26 | full vs. best single +37.92 | Post-hoc downstream attribution over six OpenReview pairs; not causal proof. |
| Single-gate artifact ablation | best single gate mean 3.6667 | full review-guided 3.5; baseline 2.9166 | best single vs. baseline +0.7501 | Causal-style mini-artifact ablation; targeted evaluator-stress can beat full review guidance in this small proxy. |
| OpenReview regeneration, same scorer | 5 review-guided wins | 1 baseline win | mean overall +0.8333 | Positive but vulnerable to same-model and extra-context bias. |
| OpenReview regeneration, Claude cross-review | 3 review-guided wins | 1 baseline win, 2 ties | mean overall +0.1667 | Modest positive signal; not automatic improvement. |
| OpenReview equal-context ablation | 8 review-guided votes | 1 context-control vote, 3 ties | mean delta across models +0.5 | Paper-specific reviews beat matched unrelated review context, but Claude shows the effect is modest. |
| Deep-case internal six-gate review | six-gate hybrid wins 3/3 | raw review-guided wins 0/3 | mean internal delta +1.133 | Closes the current reproducible internal review loop for the three concrete cases; deterministic rubric proxy, not human expert evidence. |
| Frontier-alignment taxonomy | six-gate hybrid wins 3/3 | raw review-guided wins 0/3 | mean lexical frontier-alignment delta +3.467 | Uses ICLR/ICML/ACL 2025 official award-paper seeds to compare regenerated artifacts with current frontier themes, rather than judging them only by local experiment scores. |
| Frontier vector graph | mean six-gate projection gain +0.1668 | mean six-gate cosine gain -0.0641 | 2 positive projection cases, 1 negative | Represents original papers, regenerated artifacts, and the current frontier centroid as six-dimensional vectors; shows that lexical frontier gain can still include directional drift. |
| Frontier metric disagreement | internal and lexical metrics favor six-gate 3/3 | vector projection favors six-gate 2/3; cosine favors six-gate 1/3 | disagreement rate 0.6667 | Confirms that short-term review wins, lexical frontier coverage, and vector movement measure different things. |
| Preregistered blind expert-review packet | 6 anonymized A/B pairs prepared | 0 completed human rows | planned 3-5 raters | Evaluation readiness only; no human evidence is claimed yet. |
| Live skill invocation smoke | 3 candidate directions and an archived first-version IGRE gate plan generated | template-only skill smoke | 2 live model calls, audit recommendation pass | Shows the Codex skill can be reused on a fresh task; not benchmark evidence. |
| Metric-gaming evaluator-stress smoke | evaluator-stress gate selects `guardrailed_utility_model` | primary-only fairness metric selects `metric_gaming_all_negative` | 1 synthetic metric-gaming incident reduced | Links the live skill task to an actual evaluator; controlled toy evidence, not FML-bench. |
| FML Fairness evaluator-stress replay | gate rejects metric-gaming and aborts no-valid continuation | primary-only FML metric selects `metric_gaming_all_negative` | 1 archived FML metric-gaming incident reduced | Real FML-Bench artifact replay; supports gate design, not Fairness improvement. |
| Retrospective frontier-alignment smoke | review-guided wins 1 | shuffled-control wins 5 | mean delta vs. control -0.0855; 0 delayed-value cases; 3 short-term-positive/long-term-negative cases | Future-frontier alignment is harder than local paper improvement; heuristic descriptors only. |
| Citation-backed frontier pilot | review-guided wins 1 | paper-only wins 3; shuffled-control wins 1; 1 case not scored | 6 papers, 80 relevance-filtered later citations, mean delta vs. paper-only -0.02 | Relevance filtering and match-drift guards are implemented; no delayed-value cases are found, and 3 cases are short-term-positive/long-term-negative. |
| Review-frontier signal mining | best review snippets scored 0.1431 mean | paper context 0.2369; review-guided artifact 0.1906 | 0 review-beats-paper cases; 0 latent delayed-value candidates | Historical reviews contain routeable gates, but this lexical future-frontier test finds that the original paper context carries more citation-frontier terms than the review snippets. |
| Semantic frontier judge | review-guided artifact wins 1 | paper context wins 4 | 5 model-judged cases; 0 delayed-value candidates | A model judge using citation metadata also favors original paper context; one review-guided artifact is short-and-semantic positive, not delayed-value. |
| Delayed-value candidate mining | 120 replay candidates | 90 short-term repair signals; 176 generic/unrouted | 473 reviews screened; candidate rate 0.2537 | A pre-replay screen finds comments worth expensive TFR validation, but these are candidates, not positive delayed-value evidence. |
| Candidate-frontier validation | delayed candidates mean 0.24 | controls mean 0.176 | 13 scored of 16 attempted; delayed-control +0.064 | Weak OpenAlex lexical evidence that the replay queue is better than arbitrary controls; not a delayed-value proof. |
| Prospective matched packages | 1 co-pilot or human-selected win | 3 autonomous/tie/invalid outcomes | 4 packages | Short-budget average benchmark superiority is not supported. |
| Same-run online FML smokes | 0 co-pilot benchmark wins | 1 autonomous win, 1 tie, 1 unknown | 3 paired smokes | Current valid benchmark evidence leans autonomous or tie. |
| End-to-end paired trajectory manuscript | co-pilot manuscript internal score 4.64; model reviewers prefer co-pilot 2/2 | autonomous manuscript internal score 3.48; autonomous benchmark metric wins 0.640451 vs. 0.862015 | one same-run smoke pair | Demonstrates continuous trajectory-to-manuscript comparison readiness and metric/quality disagreement, not co-pilot superiority. |
| MLAgentBench vectorization | correct search in 8/8 seeds, median 0.024581 s | starter 3.261186 s; direct rewrite failed correctness | large runtime gain | Micro-evolution helps on a correctness-gated code subproblem. |
| Sklearn diabetes tabular probe | OpenEvolve median RMSE 55.895460 | direct rewrite RMSE 55.895460 | no search advantage | Direct editing can be enough on simple modeling tasks. |

The resulting claim-to-evidence map is deliberately conservative.

| Paper claim | Evidence status | Claim boundary |
| --- | --- | --- |
| IGRE is this paper's six-gate method for treating human taste as a logged research-control signal. | Supported as a method and artifact contribution. | Not a claim that every human intervention improves outcomes. |
| OpenReview-style expert reviews can proxy human taste/insight for offline workflow design. | Supported for routeability: 398 actionable snippets and strong multi-gate utility capture. | Offline peer review is not the same as live co-pilot data. |
| Targeted gate routing can be more useful than giving the agent all human context. | Supported narrowly by the single-gate artifact ablation. | Model-reviewed mini-artifacts only; needs human expert validation. |
| TFR can test whether past reviews would have moved automated science toward later frontiers. | Supported as an operationalized replay protocol; candidate mining screens 120 comments and a small OpenAlex validation gives delayed candidates a +0.064 lexical frontier advantage over controls. | Current validated probes find 0 delayed-value cases, so the long-horizon hypothesis remains unproven. |
| Human-gated short-budget FML runs outperform autonomous runs. | Not supported. | Current evidence is mixed or negative and should be treated as a failure-mode lesson. |
| OpenEvolve-style micro-evolution improves some machine-gradeable subproblems. | Supported narrowly. | Trigger selectively; direct editing is competitive on simple tasks. |

### 4.1 Can expert review text be mapped into useful workflow gates?

We use the Hugging Face `nhop/OpenReview` dataset through streaming access, avoiding a full local download. The probe verifies 34,638 dataset rows and samples 160 rows. From these rows, a deterministic review-utility map extracts 473 review snippets. It marks 398 snippets as actionable and 64 as noisy or low-actionability.

The most common actionable route is evaluator stress testing, with 245 triggers. Structured feedback receives 210 triggers, claim calibration receives 140, and scientific-taste prior receives 111. At the category level, evaluation and metric issues appear 205 times, limitations and claim-boundary issues 140 times, novelty and positioning 111 times, reproducibility 79 times, and method-correctness 71 times.

We then run a gate-structure ablation on the same review-utility map. A no-gate policy captures no actionable routed utility. The best single-gate policy, evaluator stress testing, captures 0.369 of available utility; structured feedback captures 0.295; claim calibration captures 0.187; scientific-taste prior captures 0.148. A random-gate baseline averaged across 128 seeds captures 0.199. Full IGRE captures 1.000 by preserving all six explicit gates. This ablation does not prove better final papers, but it does establish a structural reason for IGRE: human review insight is not one generic approval signal, so compressing it into a single gate systematically drops useful scientific taste and evaluator-design information.

To reduce sample-reuse bias, we also run a paper-level held-out validation. We
select actionable categories on 379 train reviews and evaluate the resulting
gate policy on 94 held-out reviews from 32 papers. The full selected policy
captures 1.000 of held-out deterministic utility and routes 0.798 of reviews
with zero noisy-only routes. The best single-gate policy, evaluator stress
testing, captures 0.374 utility; a 512-seed random category baseline averages
0.706. This is still an offline rule-based proxy rather than independent human
labels, but it shows that the review-to-gate mapping is not only a same-sample
artifact.

Finally, we run a downstream gate-outcome attribution probe using the six equal-context OpenReview regeneration pairs. The probe links each paper's review-derived gate utility to the observed review-guided minus context-control score deltas from GPT and Claude reviewers. Full IGRE obtains aligned-outcome score 75.17, while the best single gate, evaluator stress testing, obtains 37.25 and a 512-seed random single-gate baseline averages 15.26. The strongest observed downstream alignment comes from evaluator stress testing, structured feedback, and scientific-taste prior. Frontier steering and claim calibration have no nonzero signal in this six-paper subset, so this is a post-hoc attribution signal rather than a causal six-gate downstream proof.

We then run a causal-style single-gate artifact ablation. For each selected paper, we generate new mini-paper artifacts from title/abstract plus only one gate-specific subset of reviews, and compare them with title/abstract baseline and full review-guided artifacts under GPT and Claude reviewers. The best single-gate condition is evaluator stress testing, with mean overall score 3.6667. Full review-guided obtains 3.5, and baseline obtains 2.9166. Winner votes are split across baseline (3), full review-guided (2), evaluator stress testing (6), and structured feedback (1). This result is important because it is not simply pro-human. It suggests that targeted evaluator-stress review can be more useful than feeding all review text, while baseline remains competitive for some information-rich abstracts. IGRE therefore needs gate selection, not maximal human context.

This supports the paper's central premise: human review is a concrete trace of scientific taste and insight. But the useful signal is not all review text. It is the subset that can alter evaluator design, search direction, manuscript structure, or claim boundaries.

### 4.2 Does review-guided regeneration improve research artifacts?

We select six ML/AI OpenReview papers and generate paired mini-paper artifacts. The baseline condition uses only title and abstract. The review-guided condition also uses real review snippets and decision text. An initial scorer prefers review-guided artifacts in 5 of 6 pairs, increasing mean overall score from 3.0 to 3.8333.

To reduce same-model scoring bias, we rescore the same six pairs with a stricter cross-model review route. Under this review, review-guided artifacts win 3 of 6 pairs, the baseline wins 1 pair, and 2 pairs tie, with a smaller mean delta of +0.1667. The conservative conclusion is that review text is useful when it adds concrete method detail, experiment specificity, limitation awareness, or claim calibration. It is not automatically helpful when the feedback is generic or causes the regeneration to lose the original technical framing.

This probe has an important confound. The review-guided condition receives more information than the title/abstract baseline. We therefore run an equal-context ablation using matched-length unrelated OpenReview snippets as a context-control condition. Across two reviewer models and six papers, review-guided artifacts receive 8 winning votes, context-control receives 1, and 3 comparisons tie, with mean delta across models +0.5. The stricter Claude review gives 3 review-guided wins, 0 context-control wins, and 3 ties, with mean delta +0.1667. This supports a more precise conclusion: paper-specific reviews can add value beyond generic reviewer pressure, but mostly when they contain concrete method details or explicit claim-calibration warnings.

### 4.3 Do regenerated artifacts move toward current research frontiers?

Local paper-quality scores are not enough for the central claim of this paper.
A human review may lower short-term benchmark or writing scores while still
moving a research trajectory toward a later important direction. Conversely, a
review may improve reviewer satisfaction while moving the artifact away from
the field's current frontier. To make this distinction measurable, we add
Frontier Alignment Vector Graph (FAVG), a frontier-vector graph protocol for
comparing trajectory movement rather than only artifact scores.

We seed a small current-frontier taxonomy from official ICLR, ICML, and ACL
2025 award-paper pages, then define a six-dimensional frontier space:
alignment/safety/reliability, mechanistic/theoretical insight,
efficient systems/inference, adaptive long-horizon search,
evaluation/benchmark shift, and deployment/social value. Each original paper,
raw review-guided artifact, six-gate hybrid artifact, and frontier seed is
mapped to a nonnegative vector in this space. Let `o` be the original paper
vector, `a` be a regenerated artifact vector, and `f` be the centroid of the
current frontier seeds. We report three complementary quantities:

1. `cos(a, f) - cos(o, f)`, the change in direct similarity to the current
   frontier centroid.
2. `dot(a - o, f - o) / ||f - o||`, the projection of the regeneration movement
   onto the original-to-frontier direction.
3. the norm of the component of `a - o` orthogonal to `f - o`, which measures
   sideways novelty rather than direct frontier convergence.

FAVG makes the evaluation less brittle than a single scalar. In the
three deep cases, the lexical frontier-alignment score favors six-gate hybrid
artifacts in all three cases, with mean delta +3.467. The vector graph is more
diagnostic: mean six-gate projection gain is +0.1668, but mean cosine gain is
-0.0641; two cases move more strongly along the original-to-frontier direction,
while one case moves away. This mixed signal is exactly why IGRE needs
frontier-aware gates. A useful human insight is not merely a comment that makes
the next artifact score higher. It is a comment that changes the search vector
in a direction worth pursuing, or deliberately creates orthogonal novelty whose
value should be tested by later evidence.

We therefore add a disagreement matrix across the three deep cases. Internal
review and lexical frontier metrics favor six-gate hybrid artifacts in all
three cases, but vector projection favors six-gate in only two cases and
frontier cosine favors it in only one. The disagreement rate is 0.6667. This is
not a failure of the vector graph; it is the measurement point. It prevents the
paper from collapsing scientific taste into a single score and makes visible
when a human-guided artifact improves local quality while changing the research
direction in a more ambiguous way. FAVG is therefore not a reward model; it is
a diagnostic layer for deciding which human-guided directions deserve deeper
replay, expert review, or prospective matched-budget runs.

### 4.4 Do short-budget human gates beat autonomous baselines?

The prospective FML-bench-style matched packages are intentionally reported as mixed or negative. Across the current passing packages, there is one controlled Max-Cut micro-task where a human-selected branch is useful, and three FML-bench cases where the co-pilot branch loses, ties, aborts, or fails to produce a valid continuation. In repeated online paired smokes, valid Causality runs produce 0 co-pilot benchmark wins, 1 autonomous win, and 1 tie; the Fairness run is a no-valid-branch failure case.

This result is important. It prevents the paper from claiming that human participation improves average benchmark performance under tiny budgets. Instead, it motivates the core design problem: human gates must be specific, budget-aware, and routed to the parts of the workflow where taste and insight actually matter.

We also generate a same-run end-to-end manuscript pair from one online full-gate trajectory. The co-pilot side exercises idea selection, evaluator approval, branch selection, program-search escalation, and claim audit, then renders a trace-bound manuscript. The autonomous side uses the same online run's autonomous baseline summary and the same evidence-bound manuscript template family. This pair is deliberately mixed: the co-pilot manuscript has a higher internal structure and claim-calibration score (4.64 versus 3.48), and two model reviewers prefer it under an anonymized A/B prompt; meanwhile, the autonomous baseline wins the benchmark metric (0.640451 versus 0.862015, lower is better). This supports workflow completion and comparison readiness, not a claim that co-pilot automation is already better. It also motivates why IGRE evaluates benchmark score, manuscript quality, claim calibration, and human attention cost separately.

### 4.5 When should verifiable micro-evolution be triggered?

OpenEvolve-style search is valuable on some machine-gradeable subproblems, but not all. On a vectorization task, direct rewrite fails correctness while short OpenEvolve-style search retains correct programs and finds large runtime improvements. On Max-Cut, direct editing improves the starter, while OpenEvolve-style search gives a small additional gain. On a simple sklearn diabetes regression probe, direct editing matches the median OpenEvolve result. This boundary condition is central to IGRE: program search should be triggered by evaluator readiness and expected marginal value, not by methodological fashion.

## 5. Discussion

IGRE reframes human participation as a high-variance search operator. This is a better fit for science than the claim that human involvement is always positive. Human judgement can increase the chance of rare, high-value trajectories by noticing problem depth, mechanism, novelty, or claim risk that a metric misses. But it can also reduce average score under short budgets.

The OpenReview experiments suggest a practical way forward. Real review comments can be mined to discover what types of human insight are useful. Comments about weak evaluation should trigger evaluator stress tests. Comments about novelty should reshape the taste prior. Comments about missing limitations should trigger claim calibration. Comments about unclear presentation should become structured feedback. Vague praise or generic criticism should have low routing weight.

The retrospective nature of peer review can also be used as a measurement
advantage. For historical papers, later field evolution provides a post-hoc
frontier target. IGRE can therefore run a retrospective frontier-alignment
experiment: take a paper and its reviews at time `t`, regenerate follow-up
research artifacts with paper-only, review-guided, and shuffled-review-control
conditions, and judge which artifacts better align with the field's later
mainstream or SOTA trajectory. A good review is then not merely a review that
scores a paper harshly or positively. It is a review whose actionable comments
would have moved the automated research workflow toward a future-relevant
problem framing, method, evaluation norm, failure mode, or claim boundary.

A first deterministic smoke of this protocol is intentionally sobering. Using
manual, non-citation-backed future-frontier descriptors on the same six
OpenReview cases, the review-guided artifacts win only 1 of 6 comparisons under
a keyword/actionability score, while shuffled-review-control artifacts win 5 of
6 and the review-guided mean score is below the shuffled control by 0.0855. This
does not invalidate the protocol, because the descriptors and score are only a
pipeline smoke. It does show that future-frontier alignment is a stricter target
than local paper-quality improvement, and that "good review" must be defined by
future-relevant directionality rather than by generic reviewer pressure.

The most important case is temporally asymmetric. A review-guided rerun may
produce a paper that is worse than the original paper under immediate quality
or benchmark criteria, but better aligned with later field evolution. Such a
case would be a delayed-value review signal: the human comment is not valuable
because it improves the next artifact, but because it changes the search
trajectory toward a future-relevant direction. If a corpus of these comments can
be identified, IGRE can learn where human taste should override short-term
automation pressure.

This is the practical role of LHTG. It is a selection rule for human
participation modes: retain comments that name future-relevant mechanisms,
evaluation norms, problem reframings, or failure modes even when they are
associated with low ratings or weak immediate evidence; downweight comments that
only increase local reviewer satisfaction without improving future-frontier
alignment; and mark harmful comments when they improve neither. The current
experiments do not yet prove that LHTG finds positive DVRS cases, but they make
the distinction measurable and therefore learnable from historical review data.

The current smoke does not yet find this delayed-value pattern. It finds the
opposite diagnostic in three cases: review guidance improves the short-term
model-scored artifact, but decreases heuristic future-frontier alignment. This
negative result is useful because it separates local reviewer satisfaction from
long-horizon scientific directionality, which is exactly the distinction a
co-pilot scientist must learn.

A citation-backed version of the probe now runs on six OpenReview samples with
OpenAlex fallback, lexical relevance filtering, and a title-overlap guard
against match drift. It retrieves usable future-frontier terms for 5 of 6
papers and 80 relevance-filtered later citations. The result is again
sobering: review-guided regeneration wins only 1 case, paper-only wins 3,
shuffled-review control wins 1, and one case is not scored because the metadata
match drifts. The mean review-guided citation-frontier score is 0.21, below
paper-only 0.23 and shuffled-control 0.248. The probe finds 0 delayed-value
cases and 3 short-term-positive/long-term-negative cases. This is not evidence
against the delayed-value hypothesis; it shows that the current lexical
frontier metric can reward original paper terminology more than review-derived
direction changes, and that future-frontier measurement must solve citation
coverage, topical relevance, metadata match-drift, and semantic rather than
lexical alignment.

We therefore add a stricter review-frontier signal probe that scores the
historical review snippets themselves against citation-derived frontier terms.
Across 16 review snippets from the six papers, the best review snippets have
mean future-frontier score 0.1431, while the original paper context scores
0.2369 and the review-guided artifact scores 0.1906. No review snippet beats
the paper context or the generated artifact, and no latent delayed-value
candidate is found. This negative result is useful. It prevents the paper from
treating OpenReview as a magic source of human taste. The actionable conclusion
is narrower: peer review is a scalable offline proxy for testing participation
modes, but useful taste/insight signals must be filtered, routed, and validated
against stronger semantic and human-judged future-frontier measures.

To check whether this negative result is merely an artifact of lexical overlap,
we run a small semantic judge probe using a Monica-routed `gpt-4o-mini` judge.
The judge sees the original paper context, the best historical review snippet,
the review-guided regenerated artifact, and metadata from later citing papers.
Across the five cases with future-frontier terms, paper context wins 4 times
and review-guided artifact wins once. Mean semantic-frontier scores are 4.2 for
paper context, 3.4 for review-guided artifact, and 3.0 for the best review
snippet. The single review-guided win is a knowledge-unlearning case where the
artifact is both short-term and semantic positive. The semantic probe therefore
still finds 0 delayed-value candidates. This narrows the claim further: the
delayed-value design is conceptually important and now measurable, but the
current small OpenReview sample does not yet provide positive evidence for it.

Because expensive replay should not be run on arbitrary reviews, we add a
delayed-value candidate-mining screen over the larger review-utility map. The
screen separates comments into delayed-value replay candidates, long-horizon
positive candidates, short-term repair signals, generic/unrouted comments, and
low-routeability noise. It looks for the temporal asymmetry that matters here:
long-horizon directionality, such as mechanism, theory, generalization,
scaling, novelty repositioning, or future impact, combined with short-term
friction such as low scores, rejection, missing evaluation, unclear claims, or
weak immediate evidence. Over 473 OpenReview snippets from 160 papers, the
screen finds 120 delayed-value replay candidates, 84 long-horizon positive
candidates, and 90 short-term repair signals. This does not overturn the
negative TFR result. It instead creates a reproducible replay queue: future TFR
experiments should validate these candidates against paper-only and
shuffled-review controls using later frontier evidence.

We then run a small OpenAlex validation of this queue. For four examples from
each label class, the probe retrieves later citing works, extracts
citation-frontier terms, applies a title-overlap guard against metadata drift,
and scores the review excerpt against those later terms. Thirteen of sixteen
attempted reviews pass the match-drift guard. Delayed-value replay candidates
obtain mean review signal 0.24, compared with 0.176 for the combined controls,
a weak positive difference of +0.064. Long-horizon positive candidates score
0.28, short-term repair signals score 0.09, and generic/unrouted comments
score 0.1867. This suggests that the queue is not arbitrary, while also showing
that the strongest lexical future-frontier class is broader than strict
delayed-value candidates. The result supports replay prioritization, not a
claim that delayed-value evidence has been found.

This makes the paper's application value concrete. The goal is not merely to prove that humans improve paper quality. The goal is to design the best modes of human participation, compare them empirically, and build a workflow in which human taste is used where it has the highest chance of changing the research trajectory.

We therefore add a high-tail power-analysis artifact rather than treating the
breakthrough hypothesis as rhetoric. A high-tail success is preregistered as an
artifact that passes a blinded or fixed external quality threshold, survives
claim calibration, avoids evaluator-stress metric gaming, and, for TFR, aligns
better with later frontier evidence than both paper-only and shuffled-review
controls. Under a one-sided Fisher exact test, a Monte Carlo analysis shows why
the present six-paper probes cannot support rare-breakthrough claims: if the
autonomous high-tail rate is 5% and human-gated participation raises it to 10%,
roughly 500 matched runs per arm are needed for about 80% power; even a larger
increase from 5% to 15% needs roughly 150 runs per arm. This turns the high-tail
claim into a concrete future experiment and explains why the present paper
reports protocol readiness rather than breakthrough-probability evidence.

## 6. Limitations

The current evidence is a pilot package. It does not include independent human expert review of the final IGRE paper or of the paired regenerated artifacts. The live co-pilot trace is a single-author derived metadata corpus, not a population-level dataset of many scientists using the system. OpenReview is offline asynchronous review data, not real-time human intervention inside an AI Scientist-v2 run. The matched-budget FML evidence is underpowered and currently negative or mixed for benchmark performance. The equal-context OpenReview ablation reduces, but does not eliminate, concerns about context confounds because it still relies on model-routed scoring and regenerated mini-artifacts rather than blind expert review. The delayed-value candidate-mining screen and OpenAlex validation prioritize future replay cases, but they are heuristic and lexical; they do not replace full TFR replay or human future-frontier judgement. The high-tail hypothesis is now statistically operationalized as a power-analysis protocol, but no high-tail or delayed-value positive case has been demonstrated in the current evidence package.

These limitations are also future research directions. To make the next step concrete, the repository includes a prepared and preregistered blind-review packet for the six OpenReview regeneration pairs: reviewers see anonymized A/B artifacts, a fixed rubric, and a score-sheet template, while the condition key and analysis plan are held by the coordinator until ratings are complete. The plan defines useful human taste and insight as review signals that can change research-control decisions, not as generic approval. This packet is not evidence yet because no independent human ratings have been collected. A stronger study would deploy a reusable co-pilot scientist skill to many researchers, collect privacy-preserving gate metadata with consent, run matched autonomous and human-gated trajectories across tasks, and submit paired outputs to blind expert review. At present, such live multi-researcher data is more feasible for major agent or model companies than for a small independent project. IGRE therefore uses OpenReview as a scalable offline proxy and clearly marks the gap.

## 7. Conclusion

Co-Pilot AI Scientist v3 proposes IGRE, a six-gate architecture for inserting human scientific taste and expert-review insight into automated research loops. The evidence does not show that human participation automatically improves automated science. It shows something more specific and more useful: expert review contains actionable signals, these signals can be routed into workflow gates, review guidance can improve some regenerated artifacts, and short-budget human gates must be audited because they can fail. IGRE turns this into a reproducible method for designing and comparing human-AI scientific collaboration.

## References

- Chris Lu, Cong Lu, Robert Tjarko Lange, Jakob Foerster, Jeff Clune, and David Ha. *The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery*. arXiv:2408.06292, 2024.
- Yutaro Yamada, Robert Tjarko Lange, Cong Lu, Shengran Hu, Chris Lu, Jakob Foerster, Jeff Clune, and David Ha. *The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search*. arXiv:2504.08066, 2025.
- Juraj Gottweis, Wei-Hung Weng, Alexander Daryin, and others. *Towards an AI Co-Scientist*. arXiv:2502.18864, 2025.
- Daniil A. Boiko, Robert MacKnight, Ben Kline, and Gabe Gomes. *Autonomous Chemical Research with Large Language Models*. Nature, 2023.
- Andres M. Bran, Sam Cox, Oliver Schilter, Carlo Baldassari, Andrew D. White, and Philippe Schwaller. *Augmenting Large Language Models with Chemistry Tools*. Nature Machine Intelligence, 2024.
- Seongok Miret and N. M. Anoop Krishnan. *Are LLMs Ready for Real-World Materials Discovery?* arXiv:2402.05200, 2024.
- Shuyi Jia, Chao Zhang, and Victor Fung. *LLMatDesign: Autonomous Materials Discovery with Large Language Models*. arXiv:2406.13163, 2024.
- Alhussein Fawzi, Matej Balog, Aja Huang, Thomas Hubert, Bernardino Romera-Paredes, and others. *Discovering Faster Matrix Multiplication Algorithms with Reinforcement Learning*. Nature, 2022.
- Daniel J. Mankowitz, Andrea Michi, Anton Zhernov, Michael Gelmi, Mark Selvi, and others. *Faster Sorting Algorithms Discovered Using Deep Reinforcement Learning*. Nature, 2023.
- Bernardino Romera-Paredes, Mohammadamin Barekatain, Alexander Novikov, and others. *Mathematical Discoveries from Program Search with Large Language Models*. Nature, 2023.
- Alexander Novikov, Ngan Vu, Marvin Eisenberger, and others. *AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery*. arXiv:2506.13131, 2025.
- Asankhaya Sharma. *OpenEvolve: An Open-Source Evolutionary Coding Agent*. GitHub software repository, 2025.
- Jürgen Schmidhuber. *Optimal Ordered Problem Solver*. Machine Learning, 2004.
- Jürgen Schmidhuber. *Gödel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements*. arXiv:cs/0309048, 2003.
- Jürgen Schmidhuber. *POWERPLAY: Training an Increasingly General Problem Solver by Continually Searching for the Simplest Still Unsolvable Problem*. arXiv:1112.5309, 2011.
- Jenny Zhang, Shengran Hu, Cong Lu, Robert Tjarko Lange, and Jeff Clune. *Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents*. arXiv:2505.22954, 2025.
- Wenyi Wang, Piotr Piękos, Li Nanbo, Firas Laakom, Yimeng Chen, Mateusz Ostaszewski, Mingchen Zhuge, and Jürgen Schmidhuber. *Huxley-Gödel Machine: Human-Level Coding Agent Development by an Approximation of the Optimal Self-Improving Machine*. arXiv:2510.21614, 2025.
- Fernando et al. *PromptBreeder: Self-Referential Self-Improvement via Prompt Evolution*. arXiv:2309.16797, 2023.
- Angelica Chen, David Dohan, and David So. *EvoPrompting: Language Models for Code-Level Neural Architecture Search*. NeurIPS, 2023.
- Robert Tjarko Lange, Yujin Tang, and David Ha. *Large Language Models as Evolution Strategies*. GECCO Companion, 2024.
- Fei Liu, Xialiang Tong, Mingxuan Yuan, Xi Lin, Fu Luo, Zhenkun Wang, and Qingfu Zhang. *Evolution of Heuristics: Towards Efficient Automatic Algorithm Design Using Large Language Model*. arXiv:2401.02051, 2024.
- Haoran Ye, Jiarui Wang, Zhiguang Cao, Federico Berto, Chuanbo Hua, and others. *ReEvo: Large Language Models as Hyper-Heuristics with Reflective Evolution*. NeurIPS, 2024.
- Sheng Yao, Fei Liu, Xi Lin, Zhenkun Wang, and Qingfu Zhang. *Multi-Objective Evolution of Heuristic Using Large Language Model*. AAAI, 2025.
- Surina et al. *Algorithm Discovery with LLMs: Evolutionary Search Meets Reinforcement Learning*. arXiv:2504.05108, 2025.
- Noah Shinn, Federico Cassano, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao. *Reflexion: Language Agents with Verbal Reinforcement Learning*. NeurIPS, 2023.
- Madaan et al. *Self-Refine: Iterative Refinement with Self-Feedback*. NeurIPS, 2023.
- Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, and Anima Anandkumar. *Voyager: An Open-Ended Embodied Agent with Large Language Models*. arXiv:2305.16291, 2023.
- Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li, and others. *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation*. arXiv:2308.08155, 2023.
- Qian Liu, Yihong Chen, Bingheng Li, et al. *MLAgentBench: Evaluating Language Agents on Machine Learning Experimentation*. ICML, 2024.
- Jun Shern Chan, Neil Chowdhury, Oliver Jaffe, James Aung, Dane Sherburn, Evan Mays, Giulio Starace, and others. *MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering*. arXiv:2410.07095, 2024.
- *FML-bench: A Controlled Study of AI Research Agent Strategies from the Perspective of Search Dynamics*. arXiv:2605.17373, 2026.
- Giulio Starace, Oliver Jaffe, Dane Sherburn, James Aung, Jun Shern Chan, and others. *PaperBench: Evaluating AI's Ability to Replicate AI Research*. arXiv:2504.01848, 2025.
- Alisia Lupidi, Bhavul Gauri, Thomas Simon Foster, Bassel Al Omari, Despoina Magka, and others. *AIRS-Bench: a Suite of Tasks for Frontier AI Research Science Agents*. arXiv:2602.06855, 2026.
- Nicholas Edwards, Yukyung Lee, Yujun Mao, Yulu Qin, Sebastian Schuster, and Najoung Kim. *RExBench: Can coding agents autonomously implement AI research extensions?* arXiv:2506.22598, 2025.
- Christine Ye, Sihan Yuan, Suchetha Cooray, Steven Dillmann, Ian L. V. Roque, and others. *ReplicationBench: Can AI Agents Replicate Astrophysics Research Papers?* arXiv:2510.24591, 2025.
- Kuangshi Ai, Haichao Miao, Kaiyuan Tang, Nathaniel Gorski, Jianxin Sun, and others. *SciVisAgentBench: A Benchmark for Evaluating Scientific Data Analysis and Visualization Agents*. arXiv:2603.29139, 2026.
- `nhop/OpenReview`. *OpenReview Dataset*. Hugging Face Datasets, accessed 2026-06-02.
