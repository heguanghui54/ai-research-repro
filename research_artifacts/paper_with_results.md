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

The run at `runs/research_pilot_deepseek_v3/research_benchmark_results.json` produced the following instrumentation summary.

| Method | Mean Total Score | Std | Mean Runtime (s) | Mean Calls | Mean Tokens | Mean Output Chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_fixed` | 87.00 | 5.76 | 24.69 | 5.0 | 3965 | 10037 |
| `single_reflection` | 89.43 | 4.81 | 24.63 | 5.0 | 3938 | 10116 |
| `multi_fixed` | 107.71 | 5.09 | 136.35 | 35.0 | 60759 | 48837 |
| `multi_artifact_evolution` | 103.43 | 3.29 | 140.76 | 35.0 | 64581 | 49361 |
| `single_self_consistency` | 95.00 | 3.42 | 192.41 | 35.0 | 50568 | 25313 |
| `fixed_template` | 52.00 | 0.00 | 0.00 | 0.0 | 0 | 4150 |
| `author_curated_reference` | 134.00 | 0.00 | 0.00 | 0.0 | 0 | 17066 |
| `multi_structured_evolution` | 99.86 | 1.81 | 148.54 | 35.0 | 70304 | 53040 |

The highest mean structural-rubric score is `author_curated_reference` with 134.00 points; this is not a scientific-quality ranking.

Cost-normalized and paired-seed analysis:

| Method | Delta vs Baseline | Descriptive 95% CI | W/T/L | Score/Call | Score/1k Tokens | Score/10k Chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_fixed` | 0.00 | [0.00, 0.00] | 0/7/0 | 17.400 | 21.944 | 63.714 |
| `single_reflection` | 2.43 | [-4.00, 7.43] | 5/1/1 | 17.886 | 22.711 | 65.020 |
| `multi_fixed` | 20.71 | [16.29, 26.43] | 7/0/0 | 3.078 | 1.773 | 4.304 |
| `multi_artifact_evolution` | 16.43 | [11.43, 21.00] | 7/0/0 | 2.955 | 1.602 | 3.787 |
| `single_self_consistency` | 8.00 | [5.00, 11.86] | 7/0/0 | 2.714 | 1.879 | 6.590 |
| `fixed_template` | -35.00 | [-39.29, -30.71] | 0/0/7 | 0.000 | 0.000 | 125.301 |
| `author_curated_reference` | 47.00 | [42.71, 51.29] | 7/0/0 | 0.000 | 0.000 | 78.519 |
| `multi_structured_evolution` | 12.86 | [8.00, 17.43] | 7/0/0 | 2.853 | 1.420 | 3.428 |

The 95% intervals are paired bootstrap intervals over the available seeds. Because the main run has 7 seeds, these intervals are descriptive stability summaries only; they are not confirmatory statistics and should not be read as evidence of statistical significance. Exploratory sign-test and sign-flip diagnostics are retained in `analysis.md`, but the manuscript does not use them as significance evidence.

Generated analysis figures use short labels: Curated-Ref=`author_curated_reference`, Fixed-Template=`fixed_template`, S-Fixed=`single_fixed`, S-Reflect=`single_reflection`, S-Consist=`single_self_consistency`, M-Fixed=`multi_fixed`, M-Evolve=`multi_artifact_evolution`, and M-StructEvolve=`multi_structured_evolution`.

![Mean benchmark score by workflow. Labels include Curated-Ref author-curated non-LLM reference artifact, Fixed-Template deterministic non-LLM template, S-Fixed single fixed agent, S-Reflect reflective single agent, S-Consist budget-matched single-agent self-consistency, M-Fixed fixed multi-agent orchestration, M-Evolve append-only multi-agent artifact evolution, and M-StructEvolve structured-memory artifact evolution.](figures_png/analysis_scores.svg.png)

**Figure 1 caption.** Mean raw structural-rubric score by workflow. The x-axis uses short method labels defined above. Higher values mean the artifact contains more required evidence strings, expected artifacts, actionable commands, and final claim rows; the score is not a scientific-quality or truth metric.

![Score per LLM call by workflow using the same short labels as Figure 1. This panel highlights call efficiency rather than raw artifact-completeness score.](figures_png/analysis_score_per_call.svg.png)

**Figure 2 caption.** Structural-rubric score divided by provider calls. This view isolates call efficiency and shows that methods with high raw score can be much less efficient when they require many role calls.

![Score per 1k provider-reported tokens by workflow using the same short labels as Figure 1. This panel separates token efficiency from call efficiency.](figures_png/analysis_score_per_1k_tokens.svg.png)

**Figure 3 caption.** Structural-rubric score per 1,000 provider-reported tokens. This view separates token cost from call count; deterministic baselines and smoke tests with zero reported tokens should be interpreted with character/count proxies rather than token-normalized claims.

![Paired seed delta versus the fixed single-agent baseline. Positive values mean higher rubric score than S-Fixed on the same seed; intervals are descriptive because only 7 seeds are available.](figures_png/analysis_delta_vs_baseline.svg.png)

**Figure 4 caption.** Paired seed-level delta relative to `single_fixed`. Positive values indicate higher structural-rubric score on the same seed, not higher judged quality. The intervals are descriptive bootstrap intervals over seven seeds and should not be read as broad statistical generalization.

- Figure 1, `runs/research_pilot_deepseek_v3/figures/analysis_scores.svg`: mean raw rubric score by workflow; higher means more required evidence, expected artifacts, actionable commands, and final claim rows were present.
- Figure 2, `runs/research_pilot_deepseek_v3/figures/analysis_score_per_call.svg`: raw score divided by LLM API calls; this is the primary call-efficiency view.
- Figure 3, `runs/research_pilot_deepseek_v3/figures/analysis_score_per_1k_tokens.svg`: raw score divided by provider-reported tokens; this separates token efficiency from call efficiency.
- Figure 4, `runs/research_pilot_deepseek_v3/figures/analysis_delta_vs_baseline.svg`: paired seed delta relative to the single-agent fixed baseline.

Claim audit status: `pass_with_warnings` with 0 errors and 215 warnings.

The current evidence shows a narrow descriptive trade-off within this heuristic rubric: multi-agent role decomposition scores higher on raw artifact-completeness in this micro-benchmark than the API-backed single-agent workflows, but single-agent workflows remain far more efficient per call and per token. This raw-score result should not be read as a quality result. The quality-primary paired analysis in Appendix H changes the interpretation: when DeepSeek and Monica/gpt-4o judge scores are averaged on matched seed/task artifacts, `single_fixed` is the strongest autonomous API-backed method under this model-judge protocol and the observed multi-agent paired quality deltas are negative relative to it. The deterministic author-curated reference is not an autonomous-agent result; it is included only to calibrate the upper end of the structural rubric. The append-only artifact-evolution variant does not beat fixed multi-agent orchestration on mean raw score; Appendix I shows why this negative result for a shallow update mechanism is plausible, because the append-only updates are often repeated, generic, or explicitly no-op. The structured-memory variant is a same-call-budget stronger update mechanism that records missing evidence, missing artifacts, risk language, and prevention rules before retrieval, but it also fails to improve judged quality in this small setting. Thus the evolution result should be read as an ablation over concrete update mechanisms, not as evidence against all artifact-centric self-evolution designs. Because all statistical checks are small-sample and descriptive, the strongest claim is comparative and methodological rather than definitive.

The table reports provider token usage when the API returns it; fallback smoke tests report zero tokens and should use character/count proxies only. Because this benchmark includes heuristic instrumentation, these scores should be interpreted as pilot evidence about workflow behavior, not as a final claim that one agent design is scientifically superior. The AIRS evaluator-connected SVAMP run in Appendix G is a separate executable sanity check, not evidence for any workflow comparison. Broader claims require more task-local evaluators, more seeds, and spot review.


### VLM Figure Audit

Monica VLM figure critique is saved at `runs/research_pilot_deepseek_v3/figure_critique_monica.md`. The critique supports the descriptive visual readings that M-Fixed has the highest structural-rubric score, budget-matched S-Consist does not match M-Fixed on that structural rubric, S-Fixed/S-Reflect are strongest by efficiency views, and the quality judge must be consulted before interpreting raw score as artifact quality. It also flags remaining presentation issues: captions must state the short-label mapping, token-normalized and call-normalized efficiency should be discussed separately, and negative deltas should be visually emphasized before camera-ready submission.

## 7. Limitations

The mechanism-screen benchmark is small, author-created, and partly rubric-based. The 20-task diagnostic suite adds a ten-seed structural and model-judge quality check for `single_fixed`, budget-matched `single_self_consistency`, and `multi_fixed`, but it is still an author-created planning benchmark rather than a community leaderboard. Monica/gpt-4o generation broadens provider coverage only for three seeds, and role ablation remains seed-0 exploratory triage; neither replaces a statistically powered multi-model benchmark with human review. Heuristic scoring can overvalue polished text, and the automated claim audit still reports warnings where generated artifacts use planning language or non-final claim statuses. We therefore treat the warning audit and the weak rubric-versus-judge correlation as negative evidence about artifact reliability, not as a clean pass: those warnings motivate the paper's narrow conclusion and the need for human spot review. The cross-model quality-primary analysis is stronger than the raw rubric, and both DeepSeek and Monica/gpt-4o judges cover the full 20-task artifact set with moderate agreement, but it is still model-based rather than human expert review. Because DeepSeek is both the generator and one judge, same-family judge bias remains possible even though the Monica/gpt-4o judge independently preserves the same method ordering; the package includes a 40-artifact blinded human-evaluation packet, a local browser annotation app, and a scoring-analysis script so the next revision can directly calibrate the judge signal without changing the benchmark post hoc. Token and cost normalization depend on provider usage metadata. The SVAMP evaluator case study exercises a real task-local AIRS evaluator, but it is an appendix-only sanity check, not an official leaderboard submission, not a workflow comparison, and not evidence for multi-agent advantage because it does not use the complete AIRS harness and raw-data mount. A stronger paper would add completed human expert ratings, more diverse judge models, multiple task-local evaluators, larger task suites, simple zero-shot/few-shot baselines without workflow orchestration, and published-baseline comparisons [@lupidi2026airsbench; @researchgym2026; @firebench2026].

## 8. Conclusion

This project provides a pilot instrumentation benchmark for autonomous AI research workflows and treats artifact evolution as a falsifiable design axis. The evidence supports a narrow divergence conclusion: the structural rubric assigns higher raw artifact-completeness scores to role-specialized multi-agent orchestration, including on a 20-task, ten-seed DeepSeek repeated-seed experiment, but cross-model quality-primary analysis over the same task surface favors the fixed single-agent baseline. Multi-agent structural advantage is therefore not a quality advantage in this protocol. Budget-matched self-consistency does not account for the raw score gap, and append-only self-evolution is a negative result for the current shallow policy-update design rather than for self-evolving agents broadly. The structured-memory variant tests whether a stronger same-budget failure record changes that result, but it also fails to improve judged quality in this small setting. A policy-update audit suggests why the append-only version struggles: updates are often repeated, generic, or explicit no-ops rather than task-specific behavioral changes; this is a failure diagnosis for the implemented mechanism, not causal proof about all memory or policy-update designs. The repository now provides a reproducible testbed, audit trail, DeepSeek and Monica/gpt-4o artifact-quality judges with inter-judge agreement analysis, policy-update failure analysis, VLM figure critique, AIRS official-definition coverage, one evaluator-connected SVAMP sanity check, a ready-to-run blinded human-evaluation workflow, and an automated paper-quality review for extending or falsifying this result.


## Appendix A. Automated Claim Audit

- Status: `pass_with_warnings`
- Errors: 0
- Warnings: 215

| Severity | Method | Seed | Task | Message |
| --- | --- | ---: | --- | --- |
| warning | `single_fixed` | 0 | `paper_claim_grounding` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_fixed` | 0 | `paper_claim_grounding` | Claim row has non-final status `hypothesis`. |
| warning | `single_fixed` | 0 | `paper_claim_grounding` | Claim row has non-final status `hypothesis`. |
| warning | `single_fixed` | 1 | `artifact_evolution` | Claim row has non-final status `not supported`. |
| warning | `single_fixed` | 1 | `paper_claim_grounding` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_fixed` | 1 | `paper_claim_grounding` | Claim row has non-final status `hypothesis`. |
| warning | `single_fixed` | 1 | `paper_claim_grounding` | Claim row has non-final status `hypothesis`. |
| warning | `single_fixed` | 2 | `artifact_evolution` | Claim row has non-final status `supported`. |
| warning | `single_fixed` | 2 | `paper_claim_grounding` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_fixed` | 3 | `artifact_evolution` | Claim row has non-final status `baseline`. |
| warning | `single_fixed` | 3 | `artifact_evolution` | Claim row has non-final status `to be determined`. |
| warning | `single_fixed` | 3 | `figure_vlm_critic` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_fixed` | 3 | `paper_claim_grounding` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_fixed` | 3 | `multi_agent_topology` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_fixed` | 4 | `paper_claim_grounding` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_fixed` | 4 | `artifact_evolution` | Claim row has non-final status `inconclusive`. |
| warning | `single_reflection` | 0 | `artifact_evolution` | Claim row has non-final status `to_be_measured`. |
| warning | `single_reflection` | 0 | `artifact_evolution` | Claim row has non-final status `to_be_measured`. |
| warning | `single_reflection` | 0 | `paper_claim_grounding` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_reflection` | 0 | `figure_vlm_critic` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_reflection` | 1 | `artifact_evolution` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_reflection` | 1 | `artifact_evolution` | Claim row has non-final status `preliminary`. |
| warning | `single_reflection` | 1 | `artifact_evolution` | Claim row has non-final status `preliminary`. |
| warning | `single_reflection` | 1 | `figure_vlm_critic` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_reflection` | 1 | `paper_claim_grounding` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_reflection` | 1 | `paper_claim_grounding` | Claim row has non-final status `hypothesis`. |
| warning | `single_reflection` | 1 | `paper_claim_grounding` | Claim row has non-final status `proven`. |
| warning | `single_reflection` | 2 | `paper_claim_grounding` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_reflection` | 2 | `novelty_guard` | Claim row has non-final status `pending`. |
| warning | `single_reflection` | 2 | `novelty_guard` | Claim row has non-final status `pending`. |
| warning | `single_reflection` | 3 | `artifact_evolution` | Claim row has non-final status `to be measured`. |
| warning | `single_reflection` | 3 | `multi_agent_topology` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_reflection` | 4 | `paper_claim_grounding` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_reflection` | 4 | `artifact_evolution` | Claim row has non-final status `preliminary`. |
| warning | `single_reflection` | 4 | `artifact_evolution` | Claim row has non-final status `preliminary`. |
| warning | `single_reflection` | 5 | `paper_claim_grounding` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_reflection` | 6 | `figure_vlm_critic` | Contains planning/fallback language; do not present as completed empirical evidence. |
| warning | `single_reflection` | 6 | `figure_vlm_critic` | Claim row has non-final status `planned`. |
| warning | `single_reflection` | 6 | `figure_vlm_critic` | Claim row has non-final status `planned`. |
| warning | `single_reflection` | 6 | `figure_vlm_critic` | Claim row has non-final status `planned`. |
| warning | all | - | all | 175 additional findings omitted. |

## Appendix B. Curated Robustness Check

We also ran a seed-0 robustness check on six benchmark-inspired tasks at `research_artifacts/external_tasks_curated.json`. These tasks are inspired by AIRS-Bench, FIRE-Bench, ScienceAgentBench, MultiAgentBench, and AI Scientist-v2 evaluation patterns, but they are not official benchmark scores.

| Method | Delta vs Baseline | Descriptive 95% CI | W/T/L | Score/Call | Score/1k Tokens | Score/10k Chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_fixed` | 0.00 | [0.00, 0.00] | 0/1/0 | 20.667 | 28.401 | 84.440 |
| `single_reflection` | 8.00 | [8.00, 8.00] | 1/0/0 | 22.000 | 24.618 | 71.618 |
| `multi_fixed` | 38.00 | [38.00, 38.00] | 1/0/0 | 3.857 | 2.094 | 5.197 |
| `multi_artifact_evolution` | 32.00 | [32.00, 32.00] | 1/0/0 | 3.714 | 1.488 | 3.785 |

Single-seed structural-rubric leader: `multi_fixed`. Best score-per-call method: `single_reflection`. This is illustrative only and not a quality or statistical claim. Claim audit status: `pass_with_warnings` with 0 errors and 26 warnings.

This supplemental run supports the same narrow trade-off as the main experiment: multi-agent decomposition scores higher on raw artifact-completeness, while simpler workflows are far more inference-efficient. Because the robustness run uses one seed and benchmark-inspired tasks rather than official benchmark evaluators, it should be treated as a single-seed robustness probe, not as an external benchmark result.

## Appendix C. AIRS-Bench Official-Definition Subset

To move beyond hand-written micro-tasks, we imported six official AIRS-Bench RAD task definitions from `facebookresearch/airs-bench` at revision `18e4f1d501069cf7d7e2740d81c2ca748c56a6a1`. The importer uses `metadata.yaml` and `project_description.md` to construct planning/evidence tasks in our schema. This subset is not an official AIRS-Bench score because it evaluates planning/evidence artifacts rather than generated submissions. Appendix G separately reports one task-local AIRS evaluator run for SVAMP.

| AIRS Task | Domain | Dataset | Metric |
| --- | --- | --- | --- |
| `CodeGenerationAPPSPassAt5` | Code | `codeparrot/apps` | `Pass@5` |
| `MathQuestionAnsweringSVAMPAccuracy` | Math | `ChilleD/SVAMP` | `Accuracy` |
| `CvMolecularPropertyPredictionQm9MeanAbsoluteError` | Molecules and Proteins ML | `nimashoghi/qm9` | `MeanAbsoluteError` |
| `QuestionAnsweringDuoRCAccuracy` | Question Answering | `ibm-research/duorc` | `Accuracy` |
| `SentimentAnalysisYelpReviewFullAccuracy` | Text Classification | `Yelp/yelp_review_full` | `Accuracy` |
| `CoreferenceResolutionSuperGLUEWSCAccuracy` | Text Extraction and Matching | `aps/super_glue` | `Accuracy` |

| Method | Delta vs Baseline | Descriptive 95% CI | W/T/L | Score/Call | Score/1k Tokens | Score/10k Chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_fixed` | 0.00 | [0.00, 0.00] | 0/1/0 | 26.500 | 24.394 | 65.841 |
| `single_reflection` | -19.00 | [-19.00, -19.00] | 0/0/1 | 23.333 | 20.319 | 55.642 |
| `multi_fixed` | 22.00 | [22.00, 22.00] | 1/0/0 | 4.310 | 1.822 | 4.603 |
| `multi_artifact_evolution` | 17.00 | [17.00, 17.00] | 1/0/0 | 4.190 | 1.686 | 3.970 |

Single-seed structural-rubric leader: `multi_fixed`. Best score-per-call method: `single_fixed`. This is illustrative only and not a quality or statistical claim. Claim audit status: `pass_with_warnings` with 0 errors and 21 warnings.

The AIRS-definition subset reinforces the main trade-off under official task descriptions: multi-agent decomposition yields stronger raw planning/evidence artifacts, while single-agent workflows remain much more efficient per API call and token.

## Appendix D. Extended AIRS-Definition Coverage

After the six-task AIRS-definition subset, we ran an additional seed-0 coverage check on 12 official AIRS-Bench RAD task definitions at `research_artifacts/airs_official_tasks_12.json`. The task file was imported from `facebookresearch/airs-bench` revision `18e4f1d501069cf7d7e2740d81c2ca748c56a6a1` with at most two tasks per category. Domains covered: Code: 2, Math: 1, Molecules and Proteins ML: 2, Question Answering: 2, Text Classification: 2, Text Extraction and Matching: 2, Time Series: 1. Metrics covered: Accuracy: 6, MASE: 1, MRR: 1, MeanAbsoluteError: 2, Pass@5: 1, RougeL: 1.

This run compares three methods only: `single_fixed`, budget-matched `single_self_consistency`, and `multi_fixed`. It excludes `multi_artifact_evolution` to keep API cost bounded while checking whether the structural-rubric pattern appears on a broader official-definition set.

| Method | Delta vs Baseline | Descriptive 95% CI | W/T/L | Score/Call | Score/1k Tokens | Score/10k Chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_fixed` | 0.00 | [0.00, 0.00] | 0/1/0 | 25.667 | 22.250 | 60.505 |
| `single_self_consistency` | -13.00 | [-13.00, -13.00] | 0/0/1 | 3.512 | 1.931 | 6.226 |
| `multi_fixed` | 47.00 | [47.00, 47.00] | 1/0/0 | 4.226 | 1.854 | 4.661 |

Single-seed structural-rubric leader: `multi_fixed`. Best score-per-call method: `single_fixed`. This is illustrative only and not a quality or statistical claim. Claim audit status: `pass_with_warnings` with 0 errors and 43 warnings.

The broader official-definition coverage is consistent with the structural-rubric pattern, while `single_fixed` remains the most call-efficient. Because this is still a single-seed planning/evidence proxy rather than an official AIRS evaluator run, it is illustrative external-validity context only; it does not establish official benchmark performance or statistical reliability.

## Appendix E. Twenty-Task Diagnostic Coverage Check

To reduce dependence on the five default micro-tasks, we added an author-created 20-task diagnostic suite at `research_artifacts/ai_research_tasks_20.json`. It covers agent_memory: 1, automated_review: 1, benchmark_integrity: 1, benchmark_selection: 1, coding_agent: 1, cost_accounting: 1, evaluation_protocol: 1, experiment_execution: 1, literature_review: 1, multi_agent_collaboration: 3, multimodal_review: 1, novelty_checking: 1, paper_revision: 1, paper_writing: 2, reproducibility_package: 1, research_traceability: 1, statistics: 1. This is still not an official benchmark, but the main `single_fixed` versus `multi_fixed` structural comparison now uses the largest completed repeated-seed DeepSeek run available in the package.

The retained table compares deterministic `author_curated_reference`, deterministic `fixed_template`, `single_fixed`, and `multi_fixed`. It tests whether the raw structural-rubric pattern appears on a broader task surface while keeping API cost bounded. The primary structural comparison uses seeds 0 through 9 (10 seeds) for `single_fixed` and `multi_fixed`. The deterministic `author_curated_reference` and `fixed_template` rows are retained as seed-0 calibration anchors only, so their zero variance should not be read as a repeated-sampling estimate. The budget-matched `single_self_consistency` row now also uses seeds 0 through 9, testing whether extra single-agent calls account for the structural gap under the same task and seed coverage.

| Method | Delta vs Baseline | Descriptive 95% CI | W/T/L | Score/Call | Score/1k Tokens | Score/10k Chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `author_curated_reference` | 214.00 | [214.00, 214.00] | 1/0/0 | 0.000 | 0.000 | 76.932 |
| `fixed_template` | -131.00 | [-131.00, -131.00] | 0/0/1 | 0.000 | 0.000 | 117.470 |
| `single_fixed` | 0.00 | [0.00, 0.00] | 0/10/0 | 16.800 | 17.725 | 51.461 |
| `multi_fixed` | 92.70 | [84.50, 99.80] | 10/0/0 | 3.062 | 1.710 | 4.159 |
| `single_self_consistency` | 23.90 | [17.60, 31.10] | 10/0/0 | 2.571 | 1.354 | 4.947 |

Structural-rubric leader: `author_curated_reference`. Best score-per-call method: `single_fixed`. Claim audit status: `pass_with_warnings` with 0 errors and 520 warnings.



Cross-model quality analysis on the 20-task, ten-seed artifact set with the budget-matched self-consistency baseline again separates structural score from judged quality. Among API-backed methods, rubric/quality correlation is Pearson r=0.2721829346743291 and Spearman rho=0.2726968596508414. `single_fixed` has higher cross-judge mean quality (3.513) than `multi_fixed` (3.190) despite lower structural-rubric score; the paired quality delta for `multi_fixed` versus `single_fixed` is -0.323 over 200 matched comparisons, with descriptive paired-bootstrap CI [-0.438, -0.207]. Judge-specific sensitivity preserves this direction for `multi_fixed`: DeepSeek-only paired delta -0.420 with CI [-0.555, -0.275], and Monica/gpt-4o-only paired delta -0.225 with CI [-0.340, -0.110]. The budget-matched `single_self_consistency` baseline has mean quality 3.107 over 200 artifacts and paired delta -0.405 versus `single_fixed`, so extra single-agent calls do not remove the judged-quality gap. The interval is a percentile interval from 5,000 paired bootstrap resamples over matched seed/task artifacts. The paired standardized mean difference is d_z=-0.387. The two model judges have Pearson r=0.5782908896460613 and Spearman rho=0.5738774217438741 over 640 matched artifacts; Monica/gpt-4o averages 0.3797 quality points higher than DeepSeek. Both judges individually rate `single_fixed` above `multi_fixed` (DeepSeek 3.405 versus 2.985; Monica/gpt-4o 3.620 versus 3.395). A paired divergence test gives `multi_fixed` mean structural delta 4.635 with CI [4.155, 5.110] and mean quality delta -0.323 with CI [-0.440, -0.205] against `single_fixed`; 85/200 paired artifacts have positive structural delta and negative quality delta. After controlling for output-length, risk-term, non-final-claim, hedge-term, and lexical-diversity deltas, the `multi_fixed` quality delta intercept is -0.130. The budget-matched `single_self_consistency` row shows the same sign pattern: structural delta 1.195 and quality delta -0.405, with 62/200 opposite-direction pairs. This is now a repeated-seed model-judge diagnostic, but it is still not a human-evaluation result.

| Method | N | Cross-Judge Mean Quality | Mean Rubric | Delta vs S-Fixed | Descriptive 95% CI | W/T/L |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `author_curated_reference` | 20 | 3.375 | 27.000 | -0.225 | [-0.550, 0.075] | 5/5/10 |
| `fixed_template` | 20 | 2.500 | 9.750 | -1.100 | [-1.375, -0.825] | 0/2/18 |
| `multi_fixed` | 200 | 3.190 | 21.435 | -0.323 | [-0.438, -0.207] | 51/43/106 |
| `single_fixed` | 200 | 3.513 | 16.800 | 0.000 | [0.000, 0.000] | 0/200/0 |
| `single_self_consistency` | 200 | 3.107 | 17.995 | -0.405 | [-0.507, -0.302] | 38/42/120 |




### Monica/gpt-4o Twenty-Task Generator Check

To test whether the structural-rubric pattern is specific to DeepSeek generation, we ran the same 20-task `single_fixed` versus `multi_fixed` comparison with Monica's `gpt-4o` route as the generator for seeds 0, 1, and 2. This is now a small repeated-seed external-generator check, not a powered model-family replication.

| Method | Delta vs Baseline | Descriptive 95% CI | W/T/L | Score/Call | Score/1k Tokens | Score/10k Chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_fixed` | 0.00 | [0.00, 0.00] | 0/3/0 | 15.933 | 18.078 | 47.173 |
| `multi_fixed` | 91.00 | [82.00, 106.00] | 3/0/0 | 2.926 | 1.154 | 2.454 |

Claim audit status: `fail` with 6 errors and 42 warnings. The errors are important: across all three seeds, `single_fixed` missed reproducibility commands and a claim-evidence table on `artifact_memory_retrieval`, so the run should be read as a robustness diagnostic rather than a clean pass.



Quality judging on these 120 gpt-4o-generated artifacts again favors `single_fixed`: `multi_fixed` has paired mean quality delta -0.367 versus `single_fixed` with descriptive paired-bootstrap CI [-0.533, -0.192], while rubric/quality correlation is Pearson r=0.39509201085305135 and Spearman rho=0.3376646998915615. The two judges have Pearson r=0.6122125505385695 and Spearman rho=0.5995694549481522 over 120 artifacts.

| Method | N | Cross-Judge Mean Quality | Mean Rubric | Delta vs S-Fixed | Descriptive 95% CI | W/T/L |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `multi_fixed` | 60 | 2.942 | 20.483 | -0.367 | [-0.533, -0.192] | 13/11/36 |
| `single_fixed` | 60 | 3.308 | 15.933 | 0.000 | [0.000, 0.000] | 0/60/0 |



This coverage check supports the paper's diagnostic conclusion rather than a broad performance claim: expanding to 20 tasks and the currently completed repeated-seed DeepSeek structural run preserves the raw-rubric advantage for `multi_fixed` over `single_fixed`, while the completed cross-model quality-primary analysis over the same ten-seed DeepSeek artifact set favors the simpler `single_fixed` baseline. The remaining missing step is human expert review over the expanded task set.

## Appendix F. AIRS Evaluator Smoke Test

To reduce the gap between planning-proxy evaluation and official task execution, we ran the AIRS task-local evaluator for `MathQuestionAnsweringSVAMPAccuracy`. The run uses the official `evaluate.py` from `/tmp/airs-bench` and verifies submission formatting, label loading, metric parsing, and metric sensitivity on 300 examples.

| Submission | Exit | Accuracy |
| --- | ---: | ---: |
| `gold` | 0 | 1.0 |
| `constant_zero` | 0 | 0.0 |
| `shifted_gold` | 0 | 0.013333333333333334 |

This is not an official AIRS-Bench submission: the full AIRS raw data directory is not present locally, so the labeled evaluator mount is reconstructed from the repository's `gold_submission.csv`. The value of this smoke test is narrower but important: the paper package now contains a verified path from `submission.csv` to a task-local AIRS metric, and the evaluator distinguishes perfect, degenerate, and deliberately misaligned submissions.

## Appendix G. DeepSeek SVAMP Submission Run

We connected the DeepSeek text model to the AIRS `MathQuestionAnsweringSVAMPAccuracy` evaluator by generating a full `submission.csv` for all 300 SVAMP test questions and then running the task-local `evaluate.py`. The model prompt receives the test questions and four training examples, but not test labels; labels are mounted only for the evaluator.

| Model | Examples | LLM Calls | Fallback Calls | Accuracy | Prompt Tokens | Completion Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `deepseek-chat` | 300 | 30 | 0 | 0.9266666666666666 | 28748 | 4193 |

Approximate Wilson 95% confidence interval for this 300-example accuracy is [0.8915, 0.9511]. The evaluator smoke test in Appendix F reports 0.0 accuracy for a constant-zero degenerate submission and 0.0133 for a deliberately shifted-gold submission, so the local DeepSeek result is not a formatting artifact. It is still a single-task, single-workflow case study rather than a workflow comparison.

The task metadata lists a literature SOTA of 0.942 accuracy; our local DeepSeek run is -0.0153 absolute accuracy points relative to that metadata value. This comparison is context only, not a competitive claim: we do not convert this to the AIRS normalized score because the official normalized score depends on the benchmark harness and cross-agent worst-score reference.

The run produced 22 incorrect predictions out of 300 examples. First error examples:

| Index | Prediction | Label | Question excerpt |
| ---: | ---: | ---: | --- |
| 6 | `24` | `21` | Ed had 10 more marbles than Doug. Doug lost 11 of his marbles at the playground. If Ed had 45 marbles How many more m... |
| 26 | `86` | `3` | Dave had 21 apps on his phone. He added 89 new apps. After deleting some he had 24 left. How many more apps did he ad... |
| 28 | `15` | `11` | The grasshopper and the frog had a jumping contest. The grasshopper jumped 13 inches. The grasshopper jumped 2 inches... |
| 32 | `40` | `184` | Baker made 144 cakes. He sold 71 of them. Then he made 111 more cakes. How many more cakes did baker make than those ... |
| 58 | `624` | `1396` | In a school there are 315 girls and 309 boys. There are also 772 teachers How many people are there in that school? |

This result is complementary evidence to the planning-proxy benchmark because it exercises a real task-local AIRS evaluator. It is still not an official AIRS leaderboard submission, not a workflow comparison, and not evidence that the research-agent workflows solve AIRS: the run uses the Hugging Face SVAMP dataset locally rather than the complete AIRS raw-data mount and harness. We therefore report it only as a verified evaluator-connected case study, not as a benchmark leaderboard score.

## Appendix H. Independent Artifact Quality Judge

To test whether the automatic rubric is merely rewarding well-formed output, we added an independent DeepSeek-backed artifact-quality judge over all 280 main-run artifacts. The judge scored each artifact on 1-5 overall quality, scientific validity, claim grounding, reproducibility, novelty calibration, and overclaim risk. It was explicitly instructed to penalize unsupported claims, fake completed evidence, missing executable checks, and shallow novelty checks. The run used 28 judge calls with 0 fallback calls.

| Method | N | Mean Judge Quality | Std | Mean Rubric Score | Mean Overclaim Risk Index |
| --- | ---: | ---: | ---: | ---: | ---: |
| `author_curated_reference` | 35 | 3.143 | 0.350 | 26.800 | 0.000 |
| `fixed_template` | 35 | 2.000 | 0.000 | 10.400 | 0.000 |
| `multi_artifact_evolution` | 35 | 2.714 | 0.658 | 20.686 | 1.229 |
| `multi_fixed` | 35 | 2.686 | 0.622 | 21.543 | 1.143 |
| `multi_structured_evolution` | 35 | 2.800 | 0.668 | 19.971 | 0.829 |
| `single_fixed` | 35 | 3.229 | 0.759 | 17.400 | 0.771 |
| `single_reflection` | 35 | 3.133 | 0.812 | 17.886 | 0.800 |
| `single_self_consistency` | 35 | 2.829 | 0.609 | 19.000 | 1.343 |

Including the deterministic calibration baselines, the correlation between automatic rubric score and independent judge quality is moderate: Pearson r=0.47773850074188645 and Spearman rho=0.4645850611778528. Among API-backed methods only, the correlation is weaker: Pearson r=0.40763650325932205 and Spearman rho=0.34906931891355697. This split is important. The fixed template receives low rubric and quality scores, while the author-curated reference receives high rubric and quality scores, so the rubric captures some task-specific artifact coverage but should not be mistaken for autonomous scientific quality. Among real LLM workflows, the raw rubric still favors `multi_fixed`, while independent judges generally rate simpler single-agent outputs as competitive with or better than multi-agent variants on average quality. Therefore the main raw-score result should be read as artifact-completeness behavior, not as evidence that multi-agent outputs are better scientific artifacts. This judge pass strengthens the paper's limitation: a high-quality benchmark must combine structural completeness metrics with independent or human quality judgments.


We also reran the same judge protocol through Monica's OpenAI-compatible `gpt-4o` route to reduce same-model judging bias. The two judge outputs cover 280 matched artifacts. Quality agreement is moderate: Pearson r=0.5363618546720597 and Spearman rho=0.5615752529943492. Monica is more lenient on average (mean B-A delta 0.4624), but it preserves the main qualitative pattern: the deterministic author-curated reference is judged strongest as a calibration target, and among API-backed workflows the simpler single-agent fixed/reflection outputs remain competitive with or stronger than the multi-agent variants even though the structural rubric assigns higher raw scores to multi-agent methods.

| Method | N | DeepSeek Judge Mean | Monica/gpt-4o Judge Mean | Monica-DeepSeek Delta |
| --- | ---: | ---: | ---: | ---: |
| `author_curated_reference` | 35 | 3.143 | 3.943 | 0.800 |
| `fixed_template` | 35 | 2.000 | 2.714 | 0.714 |
| `multi_artifact_evolution` | 35 | 2.714 | 3.232 | 0.518 |
| `multi_fixed` | 35 | 2.686 | 3.314 | 0.629 |
| `multi_structured_evolution` | 35 | 2.800 | 3.057 | 0.257 |
| `single_fixed` | 35 | 3.229 | 3.371 | 0.143 |
| `single_reflection` | 35 | 3.133 | 3.314 | 0.182 |
| `single_self_consistency` | 35 | 2.829 | 3.286 | 0.457 |



### Quality-Primary Paired Analysis

Because the structural rubric is only an instrumentation signal, we also treat cross-model mean judge quality as the primary artifact-quality metric. This analysis averages the DeepSeek and Monica/gpt-4o overall-quality scores for each matched artifact, then computes paired deltas against `single_fixed` on the same seed and task. It covers 280 artifacts. Among API-backed methods, rubric/quality correlation remains limited: Pearson r=0.40763650325932205 and Spearman rho=0.34906931891355697. The best method by cross-judge mean quality is `author_curated_reference`; among autonomous API-backed workflows, `single_fixed` has the highest mean quality under this judge-pair protocol. For `multi_fixed`, the paired quality delta is -0.300 with descriptive paired-bootstrap CI [-0.545, -0.045]. Judge-specific sensitivity reports the same sign for both judges: DeepSeek-only delta -0.543 and Monica/gpt-4o-only delta -0.057. The interval is a percentile interval from 5,000 paired bootstrap resamples over matched seed/task artifacts. The paired standardized mean difference is d_z=-0.387. The supplemental `quality_primary_analysis.md` includes exploratory paired randomization checks, but the manuscript does not use them as significance evidence.

| Method | N | Cross-Judge Mean Quality | Mean Rubric | Mean Delta | DeepSeek Delta | Monica Delta | Descriptive 95% CI | W/T/L | Overclaim Risk |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `author_curated_reference` | 35 | 3.543 | 26.800 | 0.243 | -0.086 | 0.571 | [0.014, 0.471] | 15/14/6 | 0.029 |
| `fixed_template` | 35 | 2.357 | 10.400 | -0.943 | -1.229 | -0.657 | [-1.186, -0.686] | 2/4/29 | 0.000 |
| `multi_artifact_evolution` | 35 | 2.973 | 20.686 | -0.327 | -0.514 | -0.139 | [-0.562, -0.095] | 8/9/18 | 1.086 |
| `multi_fixed` | 35 | 3.000 | 21.543 | -0.300 | -0.543 | -0.057 | [-0.545, -0.045] | 8/5/22 | 1.014 |
| `multi_structured_evolution` | 35 | 2.929 | 19.971 | -0.371 | -0.429 | -0.314 | [-0.586, -0.171] | 8/5/22 | 0.800 |
| `single_fixed` | 35 | 3.300 | 17.400 | 0.000 | 0.000 | 0.000 | [0.000, 0.000] | 0/35/0 | 0.657 |
| `single_reflection` | 35 | 3.223 | 17.886 | -0.077 | -0.096 | -0.057 | [-0.294, 0.152] | 12/7/16 | 0.757 |
| `single_self_consistency` | 35 | 3.057 | 19.000 | -0.243 | -0.400 | -0.086 | [-0.486, -0.014] | 9/7/19 | 1.057 |



### Monica/gpt-4o Generator Sanity Check

To reduce dependence on a single generator model, we ran a small seed-0 external-model check using Monica's OpenAI-compatible `gpt-4o` route for the two primary autonomous baselines, `single_fixed` and `multi_fixed`, on the same five default micro-tasks. This is not a powered replication, but it tests whether the structural-score/quality-score split is specific to DeepSeek generation.

| Method | Delta vs Baseline | Descriptive 95% CI | W/T/L | Score/Call | Score/1k Tokens | Score/10k Chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_fixed` | 0.00 | [0.00, 0.00] | 0/1/0 | 14.600 | 17.680 | 45.909 |
| `multi_fixed` | 28.00 | [28.00, 28.00] | 1/0/0 | 2.886 | 1.119 | 2.371 |

Claim audit status: `pass_with_warnings` with 0 errors and 3 warnings.

| Method | N | Cross-Judge Mean Quality | Mean Rubric | Delta vs S-Fixed | W/T/L |
| --- | ---: | ---: | ---: | ---: | ---: |
| `multi_fixed` | 5 | 3.100 | 20.200 | -0.300 | 2/0/3 |
| `single_fixed` | 5 | 3.400 | 14.600 | 0.000 | 0/5/0 |

This seed-0 provider check preserves the qualitative split: `multi_fixed` has the higher structural-rubric score, while cross-judge mean quality favors `single_fixed` by 0.300 points on matched artifacts. The run is included as external-model context only; it does not remove the need for multi-seed, multi-model experiments.



### Seed-0 Multi-Agent Role Ablation

To make the multi-agent traces easier to inspect, we ran a seed-0 role-ablation probe on the five default micro-tasks. The run compares `single_fixed`, full `multi_fixed`, and three leave-one-role-out variants: `multi_no_literature`, `multi_no_coder`, and `multi_no_reviewer`. It is not a powered ablation and should not be used to infer role importance; it only selects hypotheses for a future larger role study.

| Method | Delta vs Baseline | Descriptive 95% CI | W/T/L | Score/Call | Score/1k Tokens | Score/10k Chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_fixed` | 0.00 | [0.00, 0.00] | 0/1/0 | 15.600 | 20.695 | 60.895 |
| `multi_fixed` | 31.00 | [31.00, 31.00] | 1/0/0 | 3.114 | 1.839 | 4.479 |
| `multi_no_literature` | 31.00 | [31.00, 31.00] | 1/0/0 | 3.633 | 2.599 | 6.430 |
| `multi_no_coder` | 24.00 | [24.00, 24.00] | 1/0/0 | 3.400 | 2.112 | 5.123 |
| `multi_no_reviewer` | 25.00 | [25.00, 25.00] | 1/0/0 | 3.433 | 2.242 | 5.670 |

Claim audit status: `pass_with_warnings` with 0 errors and 15 warnings.

| Method | N | Cross-Judge Mean Quality | Mean Rubric | Delta vs S-Fixed | Overclaim Risk | W/T/L |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `multi_fixed` | 5 | 3.100 | 21.800 | -0.100 | 0.800 | 1/2/2 |
| `multi_no_coder` | 5 | 3.500 | 20.400 | 0.300 | 0.600 | 3/1/1 |
| `multi_no_literature` | 5 | 2.700 | 21.800 | -0.500 | 1.300 | 0/2/3 |
| `multi_no_reviewer` | 5 | 3.200 | 20.600 | 0.000 | 0.800 | 2/1/2 |
| `single_fixed` | 5 | 3.200 | 15.600 | 0.000 | 0.700 | 0/5/0 |

This role-ablation probe is seed-0 exploratory triage, not evidence for role importance. In this run, the leave-one-role-out variants change structural score, judged quality, and overclaim-risk index in different directions, but these observations are too underpowered to interpret causally. They only motivate a future powered role study on whether novelty/risk critique and code/artifact detail affect structural completeness and judged quality differently.



### Quality-Gap Diagnostic

To diagnose why structural scores and judged quality diverge, we added a feature diagnostic over the same 280 matched artifacts. It measures output length, lexical diversity, claim-row counts, non-final claim rows, risk terms, and hedging terms, then compares each method with `single_fixed` on the same seed and task. This diagnostic is associative rather than causal, but it identifies concrete failure modes for trace inspection.

| Method | N | Mean Quality | Delta Q vs S-Fixed | Delta Chars | Unique Token Ratio | Delta Nonfinal Claims | Delta Risk Terms | Delta Hedges |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `multi_artifact_evolution` | 35 | 2.973 | -0.327 | 7864.8 | 0.262 | -0.143 | 9.400 | 12.086 |
| `multi_fixed` | 35 | 3.000 | -0.300 | 7759.9 | 0.267 | 0.000 | 6.171 | 12.057 |
| `multi_structured_evolution` | 35 | 2.929 | -0.371 | 8600.6 | 0.249 | 0.314 | 15.229 | 12.229 |
| `single_fixed` | 35 | 3.300 | 0.000 | 0.0 | 0.597 | 0.000 | 0.000 | 0.000 |
| `single_self_consistency` | 35 | 3.057 | -0.243 | 3055.1 | 0.339 | 0.429 | 7.829 | 9.657 |

Among API-backed artifacts, risk-term count has Pearson r=-0.33880126101117874 and Spearman rho=-0.37309030677323196 with cross-judge quality; non-final claim rows have Pearson r=-0.25892118974998074 and Spearman rho=-0.2654088316060581; output length has Pearson r=-0.1281498489948131 and Spearman rho=-0.08999302936515217; lexical diversity has Pearson r=0.13562598987599112 and Spearman rho=0.1194912585309798. The multi-agent variants are thousands of characters longer than `single_fixed`, have much lower unique-token ratios, and add many more risk and hedge terms. This feature diagnostic is correlational: higher structural coverage in these multi-agent artifacts co-occurs with verbose, repetitive, and risk-qualified synthesis rather than sharper judged scientific evidence, but the analysis does not establish causality.

## Appendix I. Artifact-Evolution Failure Analysis

Because `multi_artifact_evolution` is a negative result for the shallow append-only mechanism tested here, we analyzed the actual policy updates instead of treating the failure as an unexplained outcome. The analysis covers 35 policy updates from the main run and measures repeated text, no-update language, feedback terms, and task-specific overlap.

| Seed | Total Score | Final Policy Chars | Mean Update Chars | Repeat Rate | No-Update Rate | Feedback-Term Rate | Task-Specific Rate |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 111 | 1701 | 320.8 | 0.6 | 0.0 | 1.0 | 0.4 |
| 1 | 103 | 1044 | 189.4 | 0.8 | 0.0 | 1.0 | 0.0 |
| 2 | 103 | 620 | 104.6 | 0.2 | 1.0 | 0.4 | 0.0 |
| 3 | 103 | 2287 | 438 | 0.8 | 0.0 | 0.0 | 0.0 |
| 4 | 101 | 1640 | 308.6 | 0.4 | 0.0 | 0.4 | 0.2 |
| 5 | 103 | 1654 | 311.4 | 0.6 | 0.4 | 1.0 | 0.6 |
| 6 | 100 | 2187 | 418 | 0.8 | 0.0 | 0.0 | 0.0 |

Overall, mean update length is 298.6857 characters, mean Jaccard overlap with the prior accumulated policy is 0.5199, repeated-update rate is 0.6, no-update rate is 0.2, feedback-term rate is 0.5429, and task-specific update rate is only 0.1714. This failure mode is concrete: the append-only policy often repeats generic instructions or states that no update was applied. The negative result therefore should be read as evidence against this shallow update mechanism, not against artifact-centric self-evolution in general. A stronger next design would require structured error objects, before/after behavioral checks, update acceptance tests, and retrieval over previous failures rather than unvalidated text appends.

## Appendix J. Structured-Memory Evolution Analysis

The `multi_structured_evolution` method was added after the append-only policy-update failure analysis as a stronger same-call-budget ablation. After each task, it records missing evidence, missing expected artifacts, non-final claim statuses, risk language, and prevention rules. Before each later task in the same seed, it retrieves up to three prior records by lexical relevance and injects them as a checklist. This changes only the explicit strategy context; it does not add LLM calls or modify the task set or scoring function.

The analysis covers 35 structured memory records. On average, each task retrieved 1.8 prior records, but mean lexical retrieval relevance was only 0.0604. The dominant recorded failure tag was `risk_language`, suggesting that the structured checklist made failures visible but did not reliably prevent conservative/planning language from reappearing.

| Seed | Total Score | Mean Retrieved Records | Mean Retrieval Relevance |
| ---: | ---: | ---: | ---: |
| 0 | 101 | 1.8 | 0.058 |
| 1 | 97 | 1.8 | 0.0632 |
| 2 | 99 | 1.8 | 0.065 |
| 3 | 102 | 1.8 | 0.0561 |
| 4 | 100 | 1.8 | 0.0594 |
| 5 | 98 | 1.8 | 0.061 |
| 6 | 102 | 1.8 | 0.0602 |

| Failure Tag | Count |
| --- | ---: |
| `risk_language` | 30 |
| `non_actionable_command` | 8 |
| `nonfinal_claim_status` | 8 |
| `missing_expected_artifact` | 7 |
| `missing_required_evidence` | 3 |
| `preserve_success_pattern` | 2 |

This is a second negative result for shallow self-evolution: simply structuring and retrieving failure records is not enough in this micro-benchmark. A stronger version should test update acceptance criteria, task-specific repair actions, and behavioral checks that confirm whether a retrieved memory changed the next artifact rather than only lengthening the prompt.

## Appendix K. Prompt and Rubric Details

The benchmark uses one shared system instruction: return JSON only, stay conservative, and do not invent citations, benchmark numbers, or completed experiments. The role objectives are: ideator proposes a focused hypothesis and smallest useful experiment; literature critic identifies novelty risks and related-work traps; experiment manager turns the idea into baselines, ablations, commands, and a reproducible plan; coder specifies executable artifacts and failure checks; reviewer critiques claim grounding and missing evidence; writer synthesizes a conservative artifact grounded only in the trace; researcher produces the full artifact directly in single-agent conditions.

Direct and synthesis prompts require these output fields: `hypothesis`, `novelty_check`, `experiment_plan`, `required_evidence_addressed`, `claim_evidence_table`, `limitations`, `reproducibility_commands`, and `policy_update`. In `multi_artifact_evolution`, only the explicit `policy_update` text may carry between tasks; in `multi_structured_evolution`, only explicit structured failure records and retrieved checklist text may carry between tasks. Neither method can change the task set, role objectives, analysis script, or scoring function.

The policy update rule is intentionally simple: after each task, if the method has `self_evolve=True`, the next task receives the previous strategy policy plus the previous artifact's `policy_update` string. No gradient update, hidden memory, retrieval index, or scorer feedback other than the logged artifact text is used. One seed-0 policy trace begins with "Always ground novelty and claims in explicit evidence. Keep commands reproducible.", then appends updates such as "Artifact preservation reduces reproducibility failures; policy drift is low (edit distance 0.12)" and "Ensure that all claims in generated paper sections are explicitly grounded in a claim-evidence table." This transparency is also a limitation: the updates are shallow, which is consistent with the observed failure of `multi_artifact_evolution` to beat `multi_fixed`.

The exact scoring implementation is `src/ai_research_repro/research_benchmark.py::_score_answer`. In prose, the score is:

- `3 * evidence_hits`
- `2 * expected_artifact_hits`
- `2` if an experiment plan is present
- up to `3` points for limitations
- `1` point each for reproducibility commands, actionable command terms, a claim-evidence table, and a related-work-trap mention
- up to `3` points for final claim rows whose status is `observed`, `measured`, `verified`, or `completed`
- minus up to `3` points for non-final claim rows
- minus one point for each explicit `fallback`, `simulated`, or `placeholder` risk mention

This rubric intentionally measures artifact completeness and conservatism, not scientific truth. The paper package therefore includes both `claim_audit.md` and `paper_quality_review.md` so downstream reviewers can inspect where the automatic scoring may be misleading.

The SVAMP case-study prompt is implemented in `scripts/run_svamp_deepseek_submission.py`. The system instruction says that the model is solving SVAMP arithmetic word problems for an AIRS-Bench submission and must return JSON only, with each answer as a single integer string and no units. Each user message includes four training examples with answers plus a batch of test questions without answers, and requests exactly `{"answers": [{"index": 0, "answer": "42"}, ...]}`. Test labels are written only to the local evaluator mount and are not included in the model prompt.

The independent artifact-quality judge prompt is implemented in `src/ai_research_repro/artifact_quality_judge.py`; the full source is copied into `supplemental/code_snapshot/src/ai_research_repro/artifact_quality_judge.py`. The judge system message is:

```
You are an independent ML research artifact judge.
Score generated autonomous-research artifacts for actual research usefulness, not
for whether they merely contain required fields. Be skeptical of plans that claim
completed evidence without execution. Return strict JSON only.
```

For each batch of artifacts, the user prompt begins:

```
Evaluate each generated autonomous-research artifact.

Use 1-5 scores, where 1 is not useful, 3 is a plausible but incomplete research plan,
and 5 is a strong, conservative, reproducible research artifact. Penalize unsupported
claims, missing executable checks, fake completed evidence, and shallow novelty checks.
```

It then requires JSON with `overall_quality`, `scientific_validity`, `claim_grounding`, `reproducibility`, `novelty_calibration`, `overclaim_risk`, and one-sentence `notes` for every `(method, seed, task_id)` item. The artifact payload includes method, seed, task id, question, related-work trap, rubric score, and a compacted JSON serialization of the generated artifact. The DeepSeek and Monica/gpt-4o judge runs use the same prompt template; the Monica run differs only in the model route (`multimodal=True`).

All DeepSeek chat-completion calls in this package use the OpenAI-compatible client in `src/ai_research_repro/llm.py` with temperature `0.2`, API timeout controlled by `AI_RESEARCH_API_TIMEOUT_SECONDS` (default 45 seconds), and two client retries. Monica/gpt-4o VLM calls use the same OpenAI-compatible client path with temperature `0.1`, the Monica base URL, and two client retries. The main run uses seeds `0`, `1`, `2`, `3`, `4`, `5`, `6`; these seeds control task ordering, sampling of benchmark subsets, bootstraps, and local deterministic code paths, but the remote LLM APIs do not expose a request-level sampling seed control in the logged OpenAI-compatible calls. The local package was assembled on macOS 26.5 arm64, Python 3.9.6, Apple M4, 16 GB RAM; runtime measurements should be treated as machine-local rather than hardware-normalized. Provider-side immutable model snapshot IDs for `deepseek-chat` and Monica-routed `gpt-4o` were not returned in the logged responses, so the package records provider, route, model alias, base URL, timestamp, and token usage but cannot recover exact provider snapshot identifiers. The curated and AIRS-definition robustness appendices are explicitly marked as seed-0 checks. Full per-task role traces for every retained main-run seed are included under `role_traces/` in the submission package.

