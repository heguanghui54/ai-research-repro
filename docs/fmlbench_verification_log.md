# FML-bench verification log

This log records what was verified in this worktree and on the Ubuntu host
reachable via `ssh ubuntu-heshi`.

## Verified in this worktree

- The minimal local reproduction scaffold runs on Ubuntu without API keys.
- The repo is pushed to GitHub on branch `codex/fmlbench-minimal`.
- The Ubuntu reproduction guide and smoke-test helper are in the repo.

## Verified on Ubuntu

### 1. Official FML-bench repository help path works

Command:

```bash
ssh ubuntu-heshi 'cd ~/work/FML-bench && python3 run_agent_benchmark.py --help'
```

Result:

- `run_agent_benchmark.py` starts successfully
- the CLI exposes `--agent-config`, `--task-config`, `--model`, `--provider`, and `--output-dir`

### 2. Monica provider patch works

Command:

```bash
ssh ubuntu-heshi 'cd ~/work/ai-research-repro && python3 scripts/patch_fmlbench_monica_provider.py --repo ~/work/FML-bench'
```

Then:

```bash
ssh ubuntu-heshi 'cd ~/work/FML-bench && MONICA_API_KEY=testkey python3 - <<\"PY\"\nfrom agents.llm import create_client\nclient, model = create_client(\"gpt-4o-mini\", \"Monica\")\nprint(model)\nprint(client.base_url)\nPY'
```

Result:

- the official repo now accepts `provider=Monica`
- the constructed client points to `https://openapi.monica.im/v1`

### 3. Minimal local reproduction runs end-to-end

Command:

```bash
ssh ubuntu-heshi 'cd ~/work/ai-research-repro && PYTHONPATH=src python3 -m ai_research_repro.cli run --workspace ~/work/fmlbench-local --ideas 1'
```

Result:

```json
{
  "workspace": "/home/heshi/work/fmlbench-local",
  "summary_metrics": {
    "baseline_val_loss": 0.43255431094511965,
    "best_val_loss": 0.40170218769559984,
    "delta_val_loss": -0.030852123249519803,
    "baseline_train_loss": 0.1908155709703061,
    "best_train_loss": 0.2915316256996926
  },
  "report_path": "/home/heshi/work/fmlbench-local/artifacts/report.md",
  "review": {
    "overall": 7.0,
    "strengths": [
      "Clear end-to-end workflow",
      "Reproducible local benchmark"
    ],
    "weaknesses": [
      "Small benchmark",
      "Limited novelty if ideas are only hyperparameter edits"
    ],
    "recommendation": "revise"
  }
}
```

## Still missing for a full paper-style run

The official benchmark still needs:

- a real API key for DeepSeek or Monica
- task-specific environment setup on the Ubuntu host
- time to run the chosen task configs at the intended step budget

The current worktree therefore proves the workflow and provider wiring, but
not yet the full 18-task paper-scale benchmark run.

