# Experiment Plan

## Proposed Method

Build an AI Scientist-v2 style research loop where agents produce persistent artifacts:

- `topic.md`
- `ideas.json`
- `literature_notes.md`
- `experiment_plan.md`
- runnable code/configs
- `metrics.json`
- `review.json`
- `paper.md`
- `strategy_policy.md`

After each task, a self-evolution step updates only `strategy_policy.md` and optionally role prompts. It must cite concrete failures from logs and cannot change scoring scripts.

## Main Comparison

1. **Single-Agent Fixed**: one agent performs all stages with fixed instructions.
2. **Single-Agent Reflection**: one agent adds a post-run reflection but does not persist an executable policy.
3. **Single-Agent Self-Consistency**: one researcher produces six independent attempts and one synthesis, matching the seven-call budget of the multi-agent workflows.
4. **Multi-Agent Fixed**: ideator, literature critic, experiment manager, coder, reviewer, writer.
5. **Multi-Agent Artifact Evolution**: same as Multi-Agent Fixed, plus policy evolution from run logs.

## Ablations

- Remove literature-grounded novelty guard.
- Remove reviewer/critic role.
- Remove executable artifact preservation and keep only natural-language memory.
- Disable VLM figure critique for figure-producing tasks.

## Robustness Checks

- Same total token budget across methods.
- Same total call budget for `single_self_consistency`, `multi_fixed`, and `multi_artifact_evolution`.
- Three random seeds or shuffled task orders.
- DeepSeek text/code model as primary backend; Monica VLM backend only for figure critique.
- Use `--role-mode orchestrated` for real multi-agent experiments; reserve `metadata` mode for smoke tests.
- Rerun top outputs from clean workspace commands.

## Failure-Mode Analysis

Track:

- hallucinated citations,
- unsupported novelty claims,
- broken code/configs,
- metric cherry-picking,
- incoherent multi-agent disagreement,
- policy drift that weakens constraints.

## Minimum First Run

Run four methods on five micro-benchmark tasks with seeds `0,1,2`. This is enough for a pilot table, not a final claim. Expand to 20 tasks if the pilot shows non-noisy differences.

Generated artifacts:

- `research_benchmark_results.json`
- `research_benchmark_summary.csv`
- `research_benchmark_summary.md`
- `claim_audit.json`
- `claim_audit.md`
- `paper_with_results.md`
- `repro_manifest.json`
- `submission_package/paper.tex`
- `submission_package/package_manifest.json`

The paper can only promote a result from pilot evidence to empirical claim when `claim_audit.md` has no errors and the result comes from API-backed runs, not fallback smoke tests.

## External Benchmark Expansion

Use `research_artifacts/external_tasks_template.json` as the schema for imported tasks. Each converted task must include:

- source benchmark,
- task/domain identifier,
- research question,
- known related-work or leakage trap,
- required evidence,
- minimal executable evaluation,
- expected artifacts.

Run imported tasks with `--task-file` and keep the resulting `repro_manifest.json` with the paper artifacts.

Current external expansions:

- `research_artifacts/external_tasks_curated.json`: benchmark-inspired robustness tasks, not official scores.
- `research_artifacts/airs_official_tasks_subset.json`: official AIRS-Bench RAD task definitions imported from `facebookresearch/airs-bench` metadata/project descriptions. These runs evaluate planning/evidence artifacts over official task descriptions; they are not official AIRS-Bench scores unless submissions are generated and task-local evaluators are executed.

## Expected Paper Claim

Conservative claim: artifact-centric self-evolution can reduce reproducibility and claim-grounding failures in autonomous AI-research agents under controlled micro-benchmark settings.
