# Co-Pilot AI Scientist v3: Insight-Gated Research Evolution for Collaborative Automated Science

## Abstract

Automated research agents can now propose hypotheses, run experiments, write manuscripts, and optimize code, but they still lack a principled way to use human scientific taste: the non-metric judgement that some problems, failures, mechanisms, or claim boundaries are more worth pursuing than others. Generic co-pilot workflows usually treat humans as approvers or editors, while fully autonomous systems remove the very judgement that often determines whether a research direction is important. We introduce Insight-Gated Research Evolution (IGRE), a workflow architecture that converts human taste and expert-review insight into explicit control signals inside AI Scientist-v2-style research loops. IGRE uses five gates: scientific-taste prior, evaluator stress test, frontier steering, verifiable micro-evolution, and claim calibration. These gates are logged with evidence, attention cost, and claim boundaries, so human participation can be measured rather than assumed beneficial. We evaluate IGRE with an evidence package built from FML-bench style runs, OpenEvolve-style micro-evolution probes, OpenReview-derived expert-review signals, paired manuscript probes, and reproducibility audits. The current evidence supports a conservative claim: expert review text can be mapped into actionable workflow gates, review-guided regeneration improves some research artifacts under cross-model review, and short-budget human-gated FML runs are mixed or negative rather than automatically superior. IGRE is therefore not a proof that humans always improve automated science. It is a reproducible method for designing, comparing, and auditing the modes by which human insight can alter scientific search.

## 1. Introduction

The recent wave of AI research agents has made a strong case for automation. Systems such as AI Scientist-v2 can generate ideas, run experiments, and produce papers. AI Co-Scientist-style systems organize hypotheses through generate, debate, and evolve loops. AlphaEvolve demonstrates that language models can drive evolutionary code search when candidate programs can be evaluated automatically. These systems expose a tempting conclusion: if the benchmark and evaluator are clear, the human can be removed from the loop.

Scientific research, however, is not only a process of optimizing a visible metric. Researchers also decide which questions are deep, which failure is informative, which mechanism is worth isolating, and which result is too weak to claim. These judgements are often called taste or insight. They are not fully captured by benchmark scores, but they are not mystical either: they appear concretely in paper reviews, rebuttals, lab discussions, claim audits, and decisions to abandon or reframe a direction.

This paper asks a narrower and more useful question than whether human participation is always better than full automation. The question is: which forms of human participation can be turned into workflow-control signals that improve the search process or the accountability of automated research? This framing matters because human involvement is high-variance. A human gate may steer the system toward a rare high-value idea, but it may also slow the run, inject bias, overfit to taste, or choose a worse branch than the autonomous policy. A credible co-pilot method must therefore measure both positive and negative effects.

We propose Insight-Gated Research Evolution (IGRE), the core algorithmic pattern of Co-Pilot AI Scientist v3. IGRE is inspired by prior automated-research systems, but it is not a direct collage of them. The method adapts their ideas around a different object: not autonomous discovery alone, but the insertion of human scientific taste into the parts of the loop where non-metric judgement is useful and dangerous. IGRE treats human insight as a logged search operator. It can modify the prior over research directions, stress the evaluator, steer the hypothesis frontier, trigger small verifiable program searches, or calibrate manuscript claims.

The primary claim of this paper is therefore deliberately narrow: expert review and human scientific judgement can be operationalized as auditable workflow-control signals, and the usefulness of those signals can be compared experimentally. We do not claim that the current co-pilot system outperforms autonomous AI Scientist-v2. The current paper makes four contributions. First, it defines IGRE as a five-gate architecture for human-guided automated science. Second, it releases a reproducible evidence package with bilingual manuscripts, scripts, logs, gate schemas, audits, and a reusable Codex skill. Third, it uses OpenReview data as an offline proxy for expert scientific taste, showing how review comments can be mapped into actionable workflow gates. Fourth, it reports mixed and negative short-budget results alongside positive workflow probes, keeping the claim boundary explicit: IGRE currently supports workflow design and measurement readiness, not a top-conference-level proof of co-pilot superiority.

## 2. Related Work

AI Scientist-v2 represents the autonomous research-agent line: generate ideas, execute experiments, write papers, and evaluate outputs. Its strength is end-to-end automation, but this also means that human scientific taste is not a first-class object in the algorithm. AI Co-Scientist-style work emphasizes hypothesis generation, critique, ranking, and evolution. It is close to IGRE in its view of scientific search as a frontier, but IGRE adds explicit human gates, attention-cost logging, and claim calibration.

AlphaEvolve and OpenEvolve motivate IGRE's verifiable micro-evolution gate. They show that language-model-generated code changes can be evolved through automatic evaluation. IGRE uses this idea selectively: micro-evolution is triggered when the target is machine-gradeable and the cost is justified, rather than being treated as a universal replacement for direct editing.

Human-AI co-pilot systems usually provide assistance, editing, or approval. IGRE differs by making the human role algorithmic. A human intervention must be classified, logged, connected to evidence, and audited against downstream outcomes. The point is not that every human comment is useful. The point is to identify which comments are actionable as scientific search controls.

Peer-review datasets such as OpenReview provide a useful proxy for this problem. Real reviews contain human judgements about novelty, evaluation, correctness, clarity, impact, and claim boundaries. They are imperfect, noisy, and retrospective, but they are one of the few large public traces of expert scientific taste. IGRE uses them not as a replacement for live human co-pilot data, but as a scalable offline testbed for participation-mode design.

## 3. Method: Insight-Gated Research Evolution

IGRE models a research run as a sequence of machine actions interrupted by explicit gates. Each gate can alter the next action, but it must record the reason, evidence, cost, and claim boundary. This makes human involvement auditable and comparable to autonomous baselines.

The first gate is the scientific-taste prior. It selects or reweights research directions before expensive experimentation. A useful taste prior is not a vague preference. It should explain why a direction has depth, novelty potential, mechanistic value, failure informativeness, benchmark fit, or asymmetric upside. In the current package, OpenReview novelty and impact comments are used as an offline proxy for this gate.

The second gate is the evaluator stress test. It asks whether the metric is too easy, too narrow, or gameable. In automated science this is crucial because an agent can optimize the evaluator while missing the scientific target. Review comments about missing baselines, weak metrics, leakage, poor ablations, or invalid comparisons are routed here.

The third gate is frontier steering. It operates over a portfolio of hypotheses or implementation branches. Rather than approving one output at the end, the human or review-derived signal chooses which part of the search frontier should receive more budget. This gate is useful when the best direction is not simply the one with the best early score.

The fourth gate is verifiable micro-evolution. It applies OpenEvolve-style program search to narrow machine-gradeable subproblems such as heuristic design, vectorization, tabular modeling, or small combinatorial objectives. IGRE treats this as an escalation operator. Direct editing remains preferable when the task is simple, when evaluation is expensive, or when search adds little beyond a strong baseline.

The fifth gate is claim calibration. It edits the manuscript-level interpretation of evidence. This gate is not cosmetic. It decides whether a result supports superiority, feasibility, measurement readiness, a negative result, or only a future-work claim. Many expert reviews are useful precisely because they force this boundary.

The gates form the following algorithmic loop. The system proposes a research frontier, evaluates early artifacts, maps human or review-derived signals into gate actions, updates the frontier or evaluator, optionally performs micro-evolution, and finally writes a claim-audited manuscript. Every gate has a structured record containing the gate type, artifact reviewed, options considered, decision, rationale, expected upside, possible harm, attention cost, and downstream evidence. This structure is what distinguishes IGRE from informal co-pilot interaction.

## 4. Experiments

The experiments are designed around participation-mode selection, not around proving that humans always beat automation. The evidence package asks four questions.

The main quantitative evidence is summarized below. The table intentionally mixes positive, mixed, and negative results because IGRE is evaluated as a gate-selection framework, not as a guaranteed performance booster.

| Probe | Co-pilot or review-guided result | Baseline or autonomous result | Delta or win count | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Review utility map | 398 actionable snippets | 64 noisy snippets | 473 snippets total | Expert reviews contain routeable taste/insight signals. |
| OpenReview regeneration, same scorer | 5 review-guided wins | 1 baseline win | mean overall +0.8333 | Positive but vulnerable to same-model and extra-context bias. |
| OpenReview regeneration, Claude cross-review | 3 review-guided wins | 1 baseline win, 2 ties | mean overall +0.1667 | Modest positive signal; not automatic improvement. |
| OpenReview equal-context ablation | 8 review-guided votes | 1 context-control vote, 3 ties | mean delta across models +0.5 | Paper-specific reviews beat matched unrelated review context, but Claude shows the effect is modest. |
| Prospective matched packages | 1 co-pilot or human-selected win | 3 autonomous/tie/invalid outcomes | 4 packages | Short-budget average benchmark superiority is not supported. |
| Same-run online FML smokes | 0 co-pilot benchmark wins | 1 autonomous win, 1 tie, 1 unknown | 3 paired smokes | Current valid benchmark evidence leans autonomous or tie. |
| MLAgentBench vectorization | correct search in 8/8 seeds, median 0.024581 s | starter 3.261186 s; direct rewrite failed correctness | large runtime gain | Micro-evolution helps on a correctness-gated code subproblem. |
| Sklearn diabetes tabular probe | OpenEvolve median RMSE 55.895460 | direct rewrite RMSE 55.895460 | no search advantage | Direct editing can be enough on simple modeling tasks. |

### 4.1 Can expert review text be mapped into useful workflow gates?

We use the Hugging Face `nhop/OpenReview` dataset through streaming access, avoiding a full local download. The probe verifies 34,638 dataset rows and samples 160 rows. From these rows, a deterministic review-utility map extracts 473 review snippets. It marks 398 snippets as actionable and 64 as noisy or low-actionability.

The most common actionable route is evaluator stress testing, with 245 triggers. Structured feedback receives 210 triggers, claim calibration receives 140, and scientific-taste prior receives 111. At the category level, evaluation and metric issues appear 205 times, limitations and claim-boundary issues 140 times, novelty and positioning 111 times, reproducibility 79 times, and method-correctness 71 times.

This supports the user's central intuition: human review is a concrete trace of scientific taste and insight. But the useful signal is not all review text. It is the subset that can alter evaluator design, search direction, manuscript structure, or claim boundaries.

### 4.2 Does review-guided regeneration improve research artifacts?

We select six ML/AI OpenReview papers and generate paired mini-paper artifacts. The baseline condition uses only title and abstract. The review-guided condition also uses real review snippets and decision text. An initial scorer prefers review-guided artifacts in 5 of 6 pairs, increasing mean overall score from 3.0 to 3.8333.

To reduce same-model scoring bias, we rescore the same six pairs with a stricter cross-model review route. Under this review, review-guided artifacts win 3 of 6 pairs, the baseline wins 1 pair, and 2 pairs tie, with a smaller mean delta of +0.1667. The conservative conclusion is that review text is useful when it adds concrete method detail, experiment specificity, limitation awareness, or claim calibration. It is not automatically helpful when the feedback is generic or causes the regeneration to lose the original technical framing.

This probe has an important confound. The review-guided condition receives more information than the title/abstract baseline. We therefore run an equal-context ablation using matched-length unrelated OpenReview snippets as a context-control condition. Across two reviewer models and six papers, review-guided artifacts receive 8 winning votes, context-control receives 1, and 3 comparisons tie, with mean delta across models +0.5. The stricter Claude review gives 3 review-guided wins, 0 context-control wins, and 3 ties, with mean delta +0.1667. This supports a more precise conclusion: paper-specific reviews can add value beyond generic reviewer pressure, but mostly when they contain concrete method details or explicit claim-calibration warnings.

### 4.3 Do short-budget human gates beat autonomous baselines?

The prospective FML-bench-style matched packages are intentionally reported as mixed or negative. Across the current passing packages, there is one controlled Max-Cut micro-task where a human-selected branch is useful, and three FML-bench cases where the co-pilot branch loses, ties, aborts, or fails to produce a valid continuation. In repeated online paired smokes, valid Causality runs produce 0 co-pilot benchmark wins, 1 autonomous win, and 1 tie; the Fairness run is a no-valid-branch failure case.

This result is important. It prevents the paper from claiming that human participation improves average benchmark performance under tiny budgets. Instead, it motivates the core design problem: human gates must be specific, budget-aware, and routed to the parts of the workflow where taste and insight actually matter.

### 4.4 When should verifiable micro-evolution be triggered?

OpenEvolve-style search is valuable on some machine-gradeable subproblems, but not all. On a vectorization task, direct rewrite fails correctness while short OpenEvolve-style search retains correct programs and finds large runtime improvements. On Max-Cut, direct editing improves the starter, while OpenEvolve-style search gives a small additional gain. On a simple sklearn diabetes regression probe, direct editing matches the median OpenEvolve result. This boundary condition is central to IGRE: program search should be triggered by evaluator readiness and expected marginal value, not by methodological fashion.

## 5. Discussion

IGRE reframes human participation as a high-variance search operator. This is a better fit for science than the claim that human involvement is always positive. Human judgement can increase the chance of rare, high-value trajectories by noticing problem depth, mechanism, novelty, or claim risk that a metric misses. But it can also reduce average score under short budgets.

The OpenReview experiments suggest a practical way forward. Real review comments can be mined to discover what types of human insight are useful. Comments about weak evaluation should trigger evaluator stress tests. Comments about novelty should reshape the taste prior. Comments about missing limitations should trigger claim calibration. Comments about unclear presentation should become structured feedback. Vague praise or generic criticism should have low routing weight.

This makes the paper's application value concrete. The goal is not merely to prove that humans improve paper quality. The goal is to design the best modes of human participation, compare them empirically, and build a workflow in which human taste is used where it has the highest chance of changing the research trajectory.

## 6. Limitations

The current evidence is a pilot package. It does not include independent human expert review of the final IGRE paper or of the paired regenerated artifacts. The live co-pilot trace is a single-author derived metadata corpus, not a population-level dataset of many scientists using the system. OpenReview is offline asynchronous review data, not real-time human intervention inside an AI Scientist-v2 run. The matched-budget FML evidence is underpowered and currently negative or mixed for benchmark performance. The equal-context OpenReview ablation reduces, but does not eliminate, concerns about context confounds because it still relies on model-routed scoring and regenerated mini-artifacts rather than blind expert review. The high-tail hypothesis, that human taste may increase rare breakthrough probability even if average score falls, is conceptually important but not yet statistically operationalized.

These limitations are also future research directions. To make the next step concrete, the repository includes a prepared blind-review packet for the six OpenReview regeneration pairs: reviewers see anonymized A/B artifacts, a fixed rubric, and a score-sheet template, while the condition key is hidden. This packet is not evidence yet because no independent human ratings have been collected. A stronger study would deploy a reusable co-pilot scientist skill to many researchers, collect privacy-preserving gate metadata with consent, run matched autonomous and human-gated trajectories across tasks, and submit paired outputs to blind expert review. At present, such live multi-researcher data is more feasible for major agent or model companies than for a small independent project. IGRE therefore uses OpenReview as a scalable offline proxy and clearly marks the gap.

## 7. Conclusion

Co-Pilot AI Scientist v3 proposes IGRE, a five-gate architecture for inserting human scientific taste and expert-review insight into automated research loops. The evidence does not show that human participation automatically improves automated science. It shows something more specific and more useful: expert review contains actionable signals, these signals can be routed into workflow gates, review guidance can improve some regenerated artifacts, and short-budget human gates must be audited because they can fail. IGRE turns this into a reproducible method for designing and comparing human-AI scientific collaboration.
