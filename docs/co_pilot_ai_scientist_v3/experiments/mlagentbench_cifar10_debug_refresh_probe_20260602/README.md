# MLAgentBench CIFAR10 Debug Refresh Probe

This refresh probe revisits the second official MLAgentBench task path after
the earlier CIFAR10/debug setup attempt. The purpose is to test whether the
blocker is still a hard network failure or a slower-but-reachable data path.

## Remote Environment

- Host: `ubuntu-heshi`
- Repository: `/home/heshi/work/bench-probes/MLAgentBench`
- Task alias: `debug`
- Benchmark folder: `cifar10`
- Python: `/home/heshi/work/bench-probes/MLAgentBench/.venv/bin/python`
- Remote run directory:
  `/home/heshi/work/copilotv3-mlagentbench-cifar10-debug-refresh-20260602`

## Commands

The first command used a relative Python path:

```bash
cd /home/heshi/work/bench-probes/MLAgentBench
.venv/bin/python -u -m MLAgentBench.prepare_task debug .venv/bin/python
```

This failed because `prepare_task.py` changes into the benchmark `scripts`
directory before launching `prepare.py`, so the relative Python path no longer
exists.

The second command used an absolute Python path:

```bash
cd /home/heshi/work/bench-probes/MLAgentBench
/home/heshi/work/bench-probes/MLAgentBench/.venv/bin/python -u -m MLAgentBench.prepare_task \
  debug /home/heshi/work/bench-probes/MLAgentBench/.venv/bin/python
```

This reached the official CIFAR10 download from
`https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz`, but the transfer was
too slow for the interactive budget. After about 61 seconds, only about
3.28 MB of the 170 MB archive had been downloaded, with observed throughput
mostly around tens of KB/s. The run was terminated and no `prepared` marker was
created.

## Evidence

- `prepare_relative_python.log`: failed relative-Python invocation.
- `prepare_abs_python.log`: absolute-Python invocation showing slow CIFAR10
  download progress.

## Claim Boundary

No MLAgentBench CIFAR10/debug score is reported. This probe improves the
diagnosis from "unreachable" to "reachable but too slow under the current
interactive budget." The next viable path is to pre-cache CIFAR10 on
`ubuntu-heshi`, use a faster mirror, or choose another official MLAgentBench
task with already available data.
