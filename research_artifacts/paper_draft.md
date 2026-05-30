# A Pilot Diagnostic Study of Structural and Judged Quality Signals in AI Research Workflows

## Abstract

We study a deliberately narrow instrumentation question for autonomous AI-research workflows: when does a structural artifact-completeness rubric disagree with independent judged artifact quality? The experiment has two layers. A five-task, seven-seed mechanism screen compares an author-curated deterministic reference, a deterministic fixed-template calibration baseline, fixed single-agent, reflective single-agent, budget-matched single-agent self-consistency, fixed multi-agent, append-only artifact evolution, and structured-memory artifact evolution. A separate 20-task, ten-seed DeepSeek repeated-seed experiment then compares only the three primary budget-control methods: `single_fixed`, budget-matched `single_self_consistency`, and `multi_fixed`; it does not evaluate the artifact-evolution methods. The design is motivated by AI Scientist and AI Scientist-v2 style research loops [@lu2024aiscientist; @yamada2025aiscientistv2], but it is not an evaluation of full scientific reliability, novelty, reproducibility, or cross-model generality. Under this author-created task suite and single primary generator, the 20-task structural run preserves a large raw-rubric advantage for `multi_fixed` over `single_fixed` (428.7 versus 336.0; paired delta 92.7 with descriptive bootstrap interval [84.5, 99.8]). The ten-seed `single_self_consistency` baseline improves structural coverage over `single_fixed` (359.9 versus 336.0) but remains well below `multi_fixed`. Yet the cross-model quality-primary analysis over all 640 artifacts from this 20-task comparison, using both DeepSeek and Monica/gpt-4o judges, favors `single_fixed`: `multi_fixed` averages 3.190 quality, and the budget-matched `single_self_consistency` baseline averages 3.108. Each judge separately ranks `single_fixed` above both extra-call baselines, and the two judges show moderate agreement on artifact quality (Pearson 0.578, Spearman 0.574). Thus the paper's contribution is not a claim that multi-agent orchestration produces better research artifacts. It is a well-logged observed divergence in this protocol: role-specialized orchestration and extra-call self-consistency receive higher structural artifact-coverage scores while receiving lower model-judged scientific quality scores. Append-only self-evolution and structured failure memory are negative results only in the five-task mechanism screen and only for the shallow mechanisms tested here. The author-curated reference calibrates the rubric upper end but is not an autonomous-agent or human-baseline result.

## 1. Introduction

AI Scientist-style systems aim to automate parts of the scientific loop: ideation, literature search, experiment design, implementation, analysis, visualization, writing, and review [@lu2024aiscientist; @yamada2025aiscientistv2]. Recent work has made this loop more open-ended through agentic tree search and multimodal figure critique. At the same time, benchmarks for scientific agents show that full-cycle research remains difficult: agents often fail to execute code, calibrate novelty, or ground claims in evidence [@chen2024scienceagentbench; @lupidi2026airsbench; @researchgym2026].

This paper does not try to measure whether an agent can do science end to end. It asks a smaller diagnostic question: what does a structural artifact-completeness rubric reward when applied to role decomposition and explicit artifact updates in a compact autonomous-research workflow benchmark, and does that signal agree with independent model judges? We treat artifact-centric self-evolution as a falsifiable design variant, not as an assumed contribution.

The success criterion is therefore diagnostic rather than competitive: the study is useful if it can observe and log a repeated-seed split between structural coverage and judged scientific quality under the tested conditions. It would fail if the structural and quality signals agreed trivially, if the split disappeared on the broader task surface used here, or if the artifacts were too poorly logged to inspect the disagreement. The main observation is that the split persists in the 20-task, ten-seed primary DeepSeek comparison, which reframes the work as a measurement and failure-analysis paper rather than a method-superiority or generalization paper.

## 2. Related Work

The AI Scientist introduced an end-to-end automated research pipeline and automated reviewing [@lu2024aiscientist]. AI Scientist-v2 extended this with template-free operation, progressive agentic tree search, and VLM-based figure feedback [@yamada2025aiscientistv2]. MultiAgentBench studies collaboration and competition among LLM agents, including topology effects [@zhu2025multiagentbench]. AIRS-Bench, ScienceAgentBench, ResearchGym, MLGym, and FIRE-Bench provide stronger evidence that scientific-agent evaluation should measure executable progress and evidence quality, not only fluent papers [@lupidi2026airsbench; @chen2024scienceagentbench; @researchgym2026; @mlgym2025; @firebench2026]. Self-evolving systems such as HexMachina suggest that executable artifacts can stabilize long-horizon learning [@belle2025agentsofchange].

## 3. Method

We compare eight workflows:

1. Author-Curated Reference: a deterministic non-LLM task-specific reference artifact that uses the task schema directly and calibrates the rubric upper end; it is not an autonomous-agent or human-baseline result.
2. Fixed Template: a deterministic non-LLM template that ignores task-specific evidence and calibrates the rubric floor.
3. Single-Agent Fixed: one fixed researcher role.
4. Single-Agent Reflection: the same role with post-task reflection.
5. Single-Agent Self-Consistency: the same researcher produces six independent attempts and one synthesis for each task, matching the seven-call-per-task budget of multi-agent workflows.
6. Multi-Agent Fixed: ideator, literature critic, experiment manager, coder, reviewer, and writer roles.
7. Multi-Agent Artifact Evolution: the same role set, plus an append-only policy update step that can only revise explicit strategy artifacts from observed failures.
8. Multi-Agent Structured Evolution: the same role set and call budget, but each completed task produces a structured failure-memory record containing missing evidence, missing artifacts, non-final claim statuses, risk language, and prevention rules; before each later task, the method retrieves the most relevant prior records and injects them as a checklist.

Each task requires a hypothesis, novelty check, experiment plan, claim-evidence table, limitations, and reproducibility commands. The real multi-agent condition uses an orchestrated role mode: ideator, literature critic, experiment manager, coder, reviewer, and writer produce an auditable role trace before a final synthesis step. The self-consistency baseline controls for call budget without role specialization. The append-only artifact-evolution method may update only its explicit strategy policy after each task, using the previous task result and score components as feedback. The structured-memory variant uses the same role calls but replaces free-form policy accumulation with explicit failure records and relevance-based retrieval. Neither evolution method can modify task definitions, prompts for other methods, analysis code, or scoring code. The exact role objectives, user prompt templates, policy-update field, structured-memory builder, and scoring function are implemented in `src/ai_research_repro/research_benchmark.py`; generated role traces are exported under `runs/research_pilot_deepseek_v3/role_traces/`.

## 4. Benchmark

The mechanism-screen benchmark contains five micro-tasks:

- novelty guard for generated research ideas,
- multi-agent topology evaluation,
- artifact-evolution measurement,
- VLM figure critic ablation,
- paper claim-grounding audit.

Metrics include evidence checklist coverage, expected-artifact coverage, experiment-plan presence, limitations, reproducibility commands, actionable command terms, claim-evidence table presence, final versus non-final claim rows, related-work-trap mentions, runtime, and output-size proxy. The exact rubric is additive: evidence hits receive 3 points each; expected artifacts receive 2 points each; experiment plan, reproducibility command, actionable command, claim table, and related-work-trap mention each receive 1-2 points; up to 3 limitations and up to 3 final claim rows are rewarded; up to 3 non-final claim rows and explicit fallback/simulated/placeholder terms are penalized. This rubric measures artifact completeness, not scientific truth. To test whether the five-task mechanism screen is misleading, we also define a 20-task diagnostic suite spanning novelty checks, benchmark conversion, reproducibility audits, evaluator integration, memory retrieval, role ablations, figure critique, policy updates, and claim grounding. The 20-task suite is the primary repeated-seed experiment for the `single_fixed` versus `multi_fixed` divergence claim. These metrics are intentionally modest, so we pair them with independent model judges and clearly separated external sanity checks: AIRS official-definition planning tasks and one task-local AIRS evaluator run on SVAMP.

The implementation also supports external task files through a JSON/JSONL schema. This allows AIRS-Bench, ResearchGym, FIRE-Bench, MLGym, or ScienceAgentBench subsets to be converted into the same evaluation interface while preserving source benchmark identifiers and expected artifacts [@lupidi2026airsbench; @researchgym2026; @firebench2026; @mlgym2025; @chen2024scienceagentbench].

For cost-normalized comparison, each run records LLM call count, estimated prompt/output characters, and provider token usage when returned by the API. This lets us test whether multi-agent gains remain after accounting for extra calls.

## 5. Experiments

Primary command:

```bash
bash scripts/run_ubuntu_pilot.sh
```

Primary pilot setting:

- Model: `deepseek-chat`
- Seeds: `0,1,2,3,4,5,6`
- Methods: all eight workflows
- Role mode: `orchestrated`
- Outputs: JSON logs, CSV table, Markdown summary
- Budget matching: `single_self_consistency`, `multi_fixed`, `multi_artifact_evolution`, and `multi_structured_evolution` each use seven LLM calls per task, or 35 calls per seed over five tasks. `single_fixed` and `single_reflection` use one call per task, or five calls per seed. `fixed_template` and `author_curated_reference` use zero LLM calls and are reported only as structural-rubric calibration baselines.

External benchmark and evaluator settings:

- Convert curated and AIRS official task definitions into the `research_artifacts/external_tasks_template.json` format.
- Run the same workflow families with `--task-file`, including 6-task and 12-task AIRS official-definition subsets.
- As a separate evaluator-connected sanity check, run `MathQuestionAnsweringSVAMPAccuracy` through its AIRS task-local `evaluate.py` by generating a DeepSeek `submission.csv`.
- Keep `repro_manifest.json` with each run for model, command, task-source, and git-state provenance.
- Export a submission package containing Markdown, LaTeX, figures, audit outputs, analysis outputs, role traces, bibliography, and a code snapshot (`src/`, `scripts/`, requirements, and project metadata).

We inspect whether the two tested shallow artifact-update mechanisms score higher than fixed orchestration, whether any observed difference persists under seed shuffling, whether fixed multi-agent orchestration scores above a budget-matched single-agent baseline, and whether its policies remain conservative. These checks are descriptive comparisons of concrete workflow variants rather than causal identification of role specialization or self-evolution in general.

The main repeated-seed experiment uses the 20-task suite with DeepSeek generation for seeds 0 through 9. It compares `single_fixed`, budget-matched `single_self_consistency`, and `multi_fixed` as the primary autonomous baselines while retaining deterministic `author_curated_reference` and `fixed_template` rows as seed-0 calibration anchors. This 20-task experiment is intentionally narrower than the five-task mechanism screen: it tests the single-agent versus multi-agent budget-control claim, not artifact evolution or structured memory. The self-consistency method uses the same seven-call-per-task budget as `multi_fixed`, so this test checks whether the structural gap remains under an extra-call single-agent control. For artifact quality, we judge the resulting 640 artifacts with both DeepSeek and Monica/gpt-4o using the same artifact-quality prompt, compare inter-judge agreement, average the two overall-quality scores, and compute paired deltas against `single_fixed` on matched seed/task artifacts. Both judges score all 640 artifacts; we report the averaged result and the per-judge method means to make same-generator judge bias inspectable. Descriptive intervals use percentile intervals from 5,000 paired bootstrap resamples; paired sign-flip p-values remain in supplemental files as stability diagnostics rather than confirmatory hypothesis tests. A separate 20-task Monica/gpt-4o generator check over seeds 0, 1, and 2 is reported only as external-generator context; it should not be confused with the Monica/gpt-4o judge, which covers all 640 artifacts in the 20-task DeepSeek-generator comparison. The seed-0 role ablation is exploratory triage for future role tests.

We interpret results in three stages. First, raw score deltas show whether a method improves the structural benchmark rubric. Second, cost-normalized metrics such as score per call and score per 1k tokens test whether the improvement remains after accounting for the extra inference budget used by multi-agent orchestration. Third, cross-model quality-primary analyses test whether structural gains correspond to judged artifact quality. The paper's main claim rests on the disagreement between these stages under this task suite, generator, rubric, and judge protocol, not on raw structural score alone.

Generated figures:

- mean benchmark score by method,
- score per LLM call by method,
- paired delta against the single-agent fixed baseline.

## 6. Results

Results are inserted automatically from the run artifacts by `ai_research_repro.cli write-paper-from-results`. The main run is `runs/research_pilot_deepseek_v3/research_benchmark_results.json`; supplemental evidence includes curated external tasks, AIRS official-definition subsets, a task-local evaluator smoke test, and a DeepSeek-generated SVAMP submission evaluated with AIRS `evaluate.py`.

## 7. Limitations

The mechanism-screen benchmark is small, author-created, and partly rubric-based. The 20-task diagnostic suite adds a ten-seed structural and model-judge quality check for `single_fixed`, budget-matched `single_self_consistency`, and `multi_fixed`, but it is still an author-created planning benchmark rather than a community leaderboard. Monica/gpt-4o generation broadens provider coverage only for three seeds, and role ablation remains seed-0 exploratory triage; neither replaces a statistically powered multi-model benchmark with human review. Heuristic scoring can overvalue polished text, and the automated claim audit still reports warnings where generated artifacts use planning language or non-final claim statuses. We therefore treat the warning audit and the weak rubric-versus-judge correlation as negative evidence about artifact reliability, not as a clean pass: those warnings motivate the paper's narrow conclusion and the need for human spot review. The cross-model quality-primary analysis is stronger than the raw rubric, and both DeepSeek and Monica/gpt-4o judges cover the full 20-task artifact set with moderate agreement, but it is still model-based rather than human expert review. Because DeepSeek is both the generator and one judge, same-family judge bias remains possible even though the Monica/gpt-4o judge independently preserves the same method ordering; the package includes a 40-artifact blinded human-evaluation packet, a local browser annotation app, and a scoring-analysis script so the next revision can directly calibrate the judge signal without changing the benchmark post hoc. Token and cost normalization depend on provider usage metadata. The SVAMP evaluator case study exercises a real task-local AIRS evaluator, but it is an appendix-only sanity check, not an official leaderboard submission, not a workflow comparison, and not evidence for multi-agent advantage because it does not use the complete AIRS harness and raw-data mount. A stronger paper would add completed human expert ratings, more diverse judge models, multiple task-local evaluators, larger task suites, simple zero-shot/few-shot baselines without workflow orchestration, and published-baseline comparisons [@lupidi2026airsbench; @researchgym2026; @firebench2026].

## 8. Conclusion

This project provides a pilot instrumentation benchmark for autonomous AI research workflows and treats artifact evolution as a falsifiable design axis. The evidence supports a narrow divergence conclusion: the structural rubric assigns higher raw artifact-completeness scores to role-specialized multi-agent orchestration, including on a 20-task, ten-seed DeepSeek repeated-seed experiment, but cross-model quality-primary analysis over the same task surface favors the fixed single-agent baseline. Multi-agent structural advantage is therefore not a quality advantage in this protocol. Budget-matched self-consistency does not account for the raw score gap, and append-only self-evolution is a negative result for the current shallow policy-update design rather than for self-evolving agents broadly. The structured-memory variant tests whether a stronger same-budget failure record changes that result, but it also fails to improve judged quality in this small setting. A policy-update audit suggests why the append-only version struggles: updates are often repeated, generic, or explicit no-ops rather than task-specific behavioral changes; this is a failure diagnosis for the implemented mechanism, not causal proof about all memory or policy-update designs. The repository now provides a reproducible testbed, audit trail, DeepSeek and Monica/gpt-4o artifact-quality judges with inter-judge agreement analysis, policy-update failure analysis, VLM figure critique, AIRS official-definition coverage, one evaluator-connected SVAMP sanity check, a ready-to-run blinded human-evaluation workflow, and an automated paper-quality review for extending or falsifying this result.
