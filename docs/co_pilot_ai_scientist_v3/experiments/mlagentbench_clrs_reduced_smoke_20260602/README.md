# MLAgentBench CLRS Reduced Feasibility Smoke

- Date: 2026-06-02
- Remote host: `ubuntu-heshi`
- Remote run root: `/home/heshi/work/copilotv3-mlagentbench-clrs-reduced-smoke-20260602`
- Base workspace: copied from the official CLRS runner workspace created by
  `mlagentbench_clrs_baseline_smoke_20260602`
- Mode: reduced feasibility run, not an official MLAgentBench score
- Timeout: 600 seconds for training

## Purpose

The official CLRS baseline runner entered `train.py` but timed out after
900 seconds without producing a checkpoint. This reduced smoke tests whether a
smaller pre-registered configuration can at least reach the CLRS checkpoint and
evaluation path on the CPU-only Ubuntu host.

## Reduced Configuration

```bash
python -u train.py \
  --train_steps=1 \
  --eval_every=1 \
  --test_every=1 \
  --log_every=1 \
  --train_lengths=4 \
  --batch_size=1 \
  --hidden_size=16 \
  --nb_triplet_fts=2 \
  --nb_msg_passing_steps=1 \
  --checkpoint_path=./checkpoints
```

This configuration is intentionally smaller than the official MLAgentBench CLRS
baseline. It should be interpreted only as feasibility/cost calibration.

## Outcome

The reduced run also timed out before creating `checkpoints/spec_list.pkl` or
`checkpoints/best.pkl`. The direct task evaluator therefore failed with:

```text
FileNotFoundError: .../CLRS/checkpoints/spec_list.pkl
```

The training exit code was `124`, the standard `timeout` exit code.

## Evidence Files

- `env_check.log`: dependency versions and reduced-run metadata.
- `train.log`: reduced training invocation log.
- `train_exit_code.txt`: `124`.
- `eval_original_logfolder.log/json`: MLAgentBench evaluator result for the
  original CLRS log folder.
- `direct_eval.log/json`: direct task evaluator attempt on the reduced
  submission folder.

## Claim Boundary

This is not a benchmark result and should not be reported as an official CLRS
score. It strengthens the cost-boundary evidence: even an aggressively reduced
CLRS feasibility configuration did not reach checkpoint creation on the current
CPU-only environment. Future CLRS evidence should use a GPU-enabled JAX setup,
a cached checkpoint path, or a separately preregistered lightweight CLRS variant
with an explicit non-official label.
