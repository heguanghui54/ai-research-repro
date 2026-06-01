# ScienceAgentBench Metadata Setup Probe

This probe attempted to move the ScienceAgentBench path beyond "repository
cloned" by checking whether the official HuggingFace annotation metadata and
verified benchmark split are accessible from `ubuntu-heshi`.

## Outcome

The repository is present under `/home/heshi/work/bench-probes/ScienceAgentBench`.
The local `benchmark/` directory currently contains only `benchmark/README.md`,
not the required verified benchmark artifacts (`datasets/`, `eval_programs`,
`gold_programs`, and `scoring_rubrics`).

The project README states that the April 30, 2026 verified release should use
the HuggingFace dataset verified split plus `benchmark_verified.zip`. We created
a metadata-only Python environment and installed `datasets`, but the remote host
could not reach HuggingFace:

```text
[Errno 101] Network is unreachable
```

No ScienceAgentBench score is reported.

## Interpretation

ScienceAgentBench remains a strong next benchmark because it evaluates
data-driven scientific discovery tasks, but it currently needs external data
access before it can support a paper claim. The correct next step is to download
the verified benchmark artifacts through a reachable network path and keep those
large/private artifacts off GitHub while committing only scripts, logs, and
derived aggregate metrics.

## Artifacts

- `repo_probe.log`: local repository and README evidence.
- `huggingface_metadata_error.log`: failed metadata access attempt.
