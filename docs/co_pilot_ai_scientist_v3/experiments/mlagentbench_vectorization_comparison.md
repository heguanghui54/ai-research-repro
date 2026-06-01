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

## Artifact Paths

- Task wrapper: `mlagentbench_vectorization_task/`
- Direct LLM failed candidate: `mlagentbench_vectorization_direct_deepseek/`
- OpenEvolve run: `mlagentbench_vectorization_openevolve_3iter/`
- Best program: `mlagentbench_vectorization_openevolve_3iter/run/best/best_program.py`
- Best metrics: `mlagentbench_vectorization_openevolve_3iter/run/best/best_program_info.json`

## Interpretation

The direct rewrite failure is not a model indictment by itself; it is a useful
negative result showing why the evaluator gate matters. The same prompt family
can produce plausible vectorized code that is fast but numerically wrong. The
OpenEvolve run receives evaluator feedback and keeps only candidates that pass
the correctness gate, which is exactly the role intended for the
program-search-escalation node in Co-Pilot AI Scientist v3.
