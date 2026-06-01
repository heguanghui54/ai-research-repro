# MLAgentBench CIFAR10 Debug Setup Probe

This probe attempted to add a second official MLAgentBench task beyond the
already archived `vectorization` run. The available `tasks.json` maps the
`debug` task to the official `cifar10` benchmark folder.

## Outcome

The first attempt failed because the MLAgentBench virtual environment did not
include `torchvision`. We repaired this locally inside the MLAgentBench venv by
installing the matching CPU wheel:

```text
torch==2.12.0+cpu
torchvision==0.27.0+cpu
```

After the import smoke test passed, the official runner advanced to
`prepare.py`, but the CIFAR10 download was too slow for the current interactive
budget: after roughly 35 seconds it had downloaded only about 426 KB of a 170 MB
archive. The run was stopped and is archived as a data-access/setup probe, not
as a benchmark score.

## Interpretation

This strengthens the benchmark-selection record: the project should not claim a
second official MLAgentBench score yet. The next run needs either a pre-cached
CIFAR10 dataset on `ubuntu-heshi`, a faster mirror, or a different official
MLAgentBench task with already available data.

## Artifacts

- `run.log`: official runner output through the slow CIFAR10 download.
- `env_versions.json`: Python package versions after the `torchvision` repair.
