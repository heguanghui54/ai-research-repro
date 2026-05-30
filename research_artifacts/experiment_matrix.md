# Experiment Matrix

## Pilot Matrix

| Axis | Setting |
| --- | --- |
| Task set | `default_micro_tasks` |
| Task count | 5 |
| Methods | `single_fixed`, `single_reflection`, `multi_fixed`, `multi_artifact_evolution` |
| Seeds | `0,1,2` |
| Role mode | `orchestrated` for real experiments; `metadata` only for cheap smoke tests |
| Text model | `deepseek-chat` |
| VLM model | `MONICA_VLM_MODEL`, default `gpt-4o` |
| Primary outputs | `research_benchmark_results.json`, `research_benchmark_summary.csv`, `claim_audit.md`, `paper_with_results.md`, `repro_manifest.json` |

## External Benchmark Matrix

After the pilot succeeds, convert 10 to 20 tasks from one external source into `ResearchTask` JSON:

| Source | Why It Matters | First Target |
| --- | --- | --- |
| AIRS-Bench | Full AI research lifecycle without baseline code | 5 tasks spanning different domains |
| ResearchGym | Fixed-compute real-world AI research tasks | 3 tasks with lightweight runtime |
| FIRE-Bench | Full-cycle insight rediscovery and evidence reasoning | 3 rediscovery tasks |
| ScienceAgentBench | Scientific code-generation/data-discovery grounding | 5 tasks where evaluation is cheap |

## Stopping Rules

- Do not claim a method is better unless the effect appears in at least three seeds.
- Do not claim a completed empirical result when `claim_audit.md` has errors.
- Do not make a strong multi-agent claim if the raw-score gain disappears under `score_per_call` or `score_per_1k_tokens`.
- Treat `pass_with_warnings` as pilot evidence only; manually inspect warnings before paper submission.
- If external tasks contradict the micro-benchmark trend, narrow the paper claim to the observed task family.

## Budget Proxies

Every run records:

- `llm_call_count`,
- `estimated_prompt_chars`,
- `estimated_output_chars`,
- provider `prompt_tokens`, `completion_tokens`, and `total_tokens` when available,
- `runtime_seconds`.

These are not provider billing metrics, but they are enough to compare whether multi-agent gains are simply coming from more calls. API-backed runs should additionally preserve provider usage metadata when available.

## Analysis Outputs

`analyze-results` writes:

- `analysis.json`
- `analysis.md`
- `figures/analysis_scores.svg`
- `figures/analysis_score_per_call.svg`
- `figures/analysis_delta_vs_baseline.svg`

The analysis includes paired seed deltas against `single_fixed`, win/tie/loss counts, score per call, score per 1k tokens, and score per 10k characters.
