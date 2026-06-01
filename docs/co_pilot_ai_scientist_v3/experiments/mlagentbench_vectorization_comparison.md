# MLAgentBench Vectorization Program-Search Comparison

This comparison extends the non-FML benchmark probe from setup-only evidence to
a controlled method comparison.

## Task

- Benchmark family: MLAgentBench
- Task: `vectorization`
- Objective: optimize `Conv2DLayer.forward` in the provided `train.py` using
  NumPy vectorization.
- Metric: runtime in seconds, lower is better.
- Added gate: the local evaluator first compares the candidate convolution
  output with a nested-loop reference on a deterministic small input.

## Results

| Variant | Model / method | Correct | Runtime seconds | Notes |
| --- | --- | --- | ---: | --- |
| Official MLAgentBench Agent baseline | built-in `Agent` | yes | 3.172504 | Official MLAgentBench eval artifact; no extra correctness gate. |
| Controlled initial program | starter `train.py` | yes | 3.261186 | Same evaluator as OpenEvolve; median of 3 runs. |
| Direct LLM rewrite | DeepSeek `deepseek-chat` | no | invalid | Failed correctness gate with numerical mismatch. |
| OpenEvolve-style search | DeepSeek `deepseek-chat`, 3 iterations | yes | 0.051882 | Best found at iteration 1; median of 3 runs. |

The controlled OpenEvolve-style run improved runtime by about 62.86x over the
controlled initial program on the same evaluator. This is strong evidence for
using an AlphaEvolve/OpenEvolve-style module on small machine-gradeable
subproblems, but it should not be interpreted as proof that the full co-pilot
system improves whole-paper quality.

## Multi-Seed Check

After the initial run, we repeated the same 3-iteration OpenEvolve configuration
with additional random seeds. This checks whether the program-search result is
robust under a tiny search budget.

| Seed | Correct best program | Best runtime seconds | Best iteration | Interpretation |
| ---: | --- | ---: | ---: | --- |
| 0 | yes | 0.010945 | 2 | Found an extremely fast vectorized solution. |
| 1 | yes | 0.209423 | 1 | Found a speedup, but much weaker than most seeds. |
| 2 | yes | 0.009210 | 3 | Found the strongest vectorized solution. |
| 3 | yes | 0.017378 | 1 | Found a strong vectorized solution. |
| 4 | yes | 0.010991 | 3 | Found an extremely fast vectorized solution. |
| 42 | yes | 0.051882 | 1 | Found a strong vectorized solution. |
| 7 | yes | 2.984610 | 0 | Retained a starter-like program; only a weak speedup over the controlled starter. |
| 123 | yes | 0.031783 | 3 | Found a strong vectorized solution. |

Under this small 3-iteration budget, all 8 seeds retained a correct best
program and improved over the controlled starter runtime of 3.261186 seconds.
The median best runtime across all eight seeds was 0.024581 seconds, a median
speedup of about 132.67x. Six of eight seeds found a sub-0.1-second program.
However, seed 7 only achieved a weak 1.09x speedup and seed 1 achieved a
15.57x speedup, so the search remains seed-sensitive under tiny budgets even
though the aggregate result is now substantially stronger than the initial
three-seed probe.

## Artifact Paths

- Task wrapper: `mlagentbench_vectorization_task/`
- Direct LLM failed candidate: `mlagentbench_vectorization_direct_deepseek/`
- OpenEvolve run: `mlagentbench_vectorization_openevolve_3iter/`
- OpenEvolve seed 0 run: `mlagentbench_vectorization_openevolve_3iter_seed0/`
- OpenEvolve seed 1 run: `mlagentbench_vectorization_openevolve_3iter_seed1/`
- OpenEvolve seed 2 run: `mlagentbench_vectorization_openevolve_3iter_seed2/`
- OpenEvolve seed 3 run: `mlagentbench_vectorization_openevolve_3iter_seed3/`
- OpenEvolve seed 4 run: `mlagentbench_vectorization_openevolve_3iter_seed4/`
- OpenEvolve seed 7 run: `mlagentbench_vectorization_openevolve_3iter_seed7/`
- OpenEvolve seed 123 run: `mlagentbench_vectorization_openevolve_3iter_seed123/`
- Best program: `mlagentbench_vectorization_openevolve_3iter/run/best/best_program.py`
- Best metrics: `mlagentbench_vectorization_openevolve_3iter/run/best/best_program_info.json`

## Interpretation

The direct rewrite failure is not a model indictment by itself; it is a useful
negative result showing why the evaluator gate matters. The same prompt family
can produce plausible vectorized code that is fast but numerically wrong. The
OpenEvolve run receives evaluator feedback and keeps only candidates that pass
the correctness gate, which is exactly the role intended for the
program-search-escalation node in Co-Pilot AI Scientist v3.
