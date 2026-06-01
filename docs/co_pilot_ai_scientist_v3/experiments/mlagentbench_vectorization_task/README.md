# MLAgentBench Vectorization Task Wrapper

This wrapper uses the official MLAgentBench `vectorization` task program as the
initial program and keeps the official runtime objective, but adds a small
correctness gate before accepting a runtime score.

The official task asks the agent to vectorize the `Conv2DLayer.forward` method
using NumPy and to write the measured runtime into `submission.csv`. The wrapper
evaluates a candidate by:

1. importing the candidate and comparing `Conv2DLayer.forward` against a nested
   loop reference implementation on a small deterministic input;
2. running the full script three times;
3. reporting the median runtime in seconds;
4. exposing `score = 1 / runtime_seconds` for OpenEvolve, which maximizes
   scalar metrics.

This is a non-FML, machine-gradeable benchmark path for the
program-search-escalation part of Co-Pilot AI Scientist v3.
