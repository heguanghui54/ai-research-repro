# MLAgentBench IMDB Setup Probe

This probe attempted to add another official MLAgentBench task beyond the
archived `vectorization` run. The `imdb` benchmark folder includes an official
`eval.py`, so it is a plausible second non-FML official scoring path.

## Outcome

The first blocker was a missing Python dependency: `MLAgentBench/benchmarks/imdb/scripts/eval.py`
imports HuggingFace `datasets`, which was absent from the MLAgentBench virtual
environment. We installed `datasets==4.8.5` in the remote venv. After that
repair, even a five-example IMDB load failed because the Ubuntu host could not
reach HuggingFace:

```text
[Errno 101] Network is unreachable
```

No IMDB score is reported. This is a setup/data-access probe, not a benchmark
result.

## Interpretation

The probe strengthens the benchmark-selection record: a second official
non-FML score remains a real gap. The next attempt should either run from an
environment with HuggingFace access, pre-cache the IMDB dataset on
`ubuntu-heshi`, or select an official MLAgentBench task whose data are already
local and whose dependencies are installed.

## Artifacts

- `run.log`: dependency check and failed HuggingFace dataset load.
