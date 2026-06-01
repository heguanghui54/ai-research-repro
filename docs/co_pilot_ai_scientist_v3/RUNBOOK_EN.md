# Reproduction Runbook

This runbook reproduces the current Co-Pilot AI Scientist v3 artifact package.
It is written for the current repository plus the Ubuntu SSH host `ubuntu-heshi`.

## 1. Local PDF Build

From the repository root on macOS:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_copilot_v3_pdfs.py --language both
```

Expected outputs:

- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_en.pdf`
- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_zh.pdf`

## 2. Validate Local Artifacts

```bash
python3 -m py_compile \
  scripts/build_copilot_v3_pdfs.py \
  scripts/run_direct_llm_edit_baseline.py \
  scripts/run_direct_llm_program_baseline.py \
  scripts/run_openevolve_program_search.py

python3 - <<'PY'
import json
from pathlib import Path

for path in [
    "docs/co_pilot_ai_scientist_v3/repro_manifest.json",
    "docs/co_pilot_ai_scientist_v3/experiments/fml_branch_gate_replay/replay.json",
    "docs/co_pilot_ai_scientist_v3/human_gate_logs/program_search_gate_001.json",
    "docs/co_pilot_ai_scientist_v3/human_gate_logs/branch_gate_causality_after_two_drafts.json",
    "docs/co_pilot_ai_scientist_v3/human_gate_logs/branch_gate_fairness_after_two_attempts.json",
]:
    json.loads(Path(path).read_text())
    print("ok", path)
PY
```

## 3. Ubuntu Environment

On the remote host:

```bash
ssh ubuntu-heshi
mkdir -p /home/heshi/work/co-pilot-ai-scientist-v3
cd /home/heshi/work/co-pilot-ai-scientist-v3
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install openevolve openai
set -a
. ~/.codex/env
set +a
```

Required environment variables:

- `DEEPSEEK_API_KEY` and optionally `DEEPSEEK_BASE_URL`
- `MONICA_API_KEY` and optionally `MONICA_BASE_URL`

The verified preliminary runs used DeepSeek through the OpenAI-compatible API.
Do not print API keys into logs.

## 4. Direct LLM Baseline

Use the generic baseline when an evaluator exposes `evaluate(path) -> dict`:

```bash
python3 scripts/run_direct_llm_program_baseline.py \
  --initial-program docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/initial_program.py \
  --evaluator docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/evaluator.py \
  --output-dir /tmp/knapsack_direct_baseline \
  --signature "def select_items(items, capacity):" \
  --task-description "Choose a valid subset of 0/1 knapsack items to maximize total value under the capacity." \
  --provider deepseek \
  --model deepseek-chat
```

The archived run produced average ratio `0.9952700988954383`.

## 5. OpenEvolve Program Search

OpenEvolve is used as the open-source AlphaEvolve-style substrate because the
official AlphaEvolve system is not open sourced.

```bash
python3 scripts/run_openevolve_program_search.py \
  --initial-program docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/initial_program.py \
  --evaluator docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/evaluator.py \
  --output-dir /tmp/knapsack_openevolve_5iter/run \
  --iterations 5 \
  --provider deepseek \
  --model deepseek-chat
```

The archived run produced average ratio `0.9994394752555711`, higher than the
direct rewrite baseline on this richer heuristic task.

## 6. Human Gate Logging

Every human decision point should write a JSON log matching
`human_gate_schema.json`. Use the templates in
`skills/co-pilot-ai-scientist-v3/templates/` for new runs.

Current replay and live-probe evidence:

- Causality FML replay: stop the lower-value second draft and continue the
  stronger first branch.
- Fairness FML replay: pause after worse/buggy attempts and reset the evaluator
  or algorithm choice.
- Live Causality two-draft probe: select draft step 2 because its validation
  MAE `0.6212624733836205` is much lower than draft step 1's
  `1.1496098661684393`.
- Selected-branch continuation: apply the selected step 2 snapshot and continue
  AI Scientist-v2 for two more steps, reaching validation MAE
  `0.4012397173613497` and test MAE `0.4021701846791075`.

The current continuation is implemented by snapshot seeding. A stronger future
version should preserve and resume the original AI Scientist-v2 tree object.

## 7. Selected-Branch Continuation

Copy the continuation runner and selected snapshot to the Ubuntu host:

```bash
scp scripts/run_fmlbench_snapshot_continuation.py \
  ubuntu-heshi:/home/heshi/work/co-pilot-ai-scientist-v3/run_fmlbench_snapshot_continuation.py
scp docs/co_pilot_ai_scientist_v3/experiments/fml_online_branch_gate_drafts/step_0002_code.json \
  ubuntu-heshi:/home/heshi/work/co-pilot-ai-scientist-v3/selected_step_0002_code.json
```

Run from the official FML-bench repository:

```bash
ssh ubuntu-heshi
set -a
. ~/.codex/env
set +a
cd /home/heshi/work/FML-bench
CUDA_VISIBLE_DEVICES=0 /home/heshi/miniconda3/bin/conda run -n fmlbench \
  python /home/heshi/work/co-pilot-ai-scientist-v3/run_fmlbench_snapshot_continuation.py \
  --benchmark-name Causality_causalml \
  --snapshot-json /home/heshi/work/co-pilot-ai-scientist-v3/selected_step_0002_code.json \
  --agent-config configs/agents/ai_scientist_v2.yaml \
  --task-config configs/tasks/causality_causalml.yaml \
  --output-dir /home/heshi/work/copilotv3-selected-branch-continuation \
  --model deepseek-chat \
  --provider DeepSeek \
  --max-steps 2 \
  --num-ideas 1 \
  --num-parallel 1 \
  --stage-budgets "[1.0, 0.0, 0.0, 0.0]"
```

## 8. Non-FML MLAgentBench Baseline

Use MLAgentBench `vectorization` as the first non-FML benchmark path:

```bash
ssh ubuntu-heshi
cd /home/heshi/work/bench-probes/MLAgentBench
. .venv/bin/activate
python -u -m MLAgentBench.runner \
  --python "$(which python)" \
  --task vectorization \
  --device 0 \
  --log-dir /home/heshi/work/copilotv3-mlagentbench-vectorization-baseline \
  --work-dir /home/heshi/work/copilotv3-mlagentbench-vectorization-workspace \
  --agent-type Agent \
  --max-steps 1 \
  --agent-max-steps 1
python -m MLAgentBench.eval \
  --log-folder /home/heshi/work/copilotv3-mlagentbench-vectorization-baseline \
  --task vectorization \
  --output-file /home/heshi/work/copilotv3-mlagentbench-vectorization-baseline-eval.json
```

Archived official baseline: final runtime score `3.17250394821167` seconds and
total benchmark time `3.3655309677124023` seconds. Lower is better.

The controlled evaluator in
`docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_task/`
adds a correctness gate before accepting runtime. Under that evaluator:

- starter program median runtime: `3.261186361312866` seconds;
- direct DeepSeek rewrite: failed correctness gate;
- OpenEvolve-style search, 3 iterations: correct best program with median
  runtime `0.051882028579711914` seconds.

## 9. Remaining Evidence Needed Before Strong Submission Claims

- Replace snapshot-seeded continuation with native tree-object resume if
  feasible.
- Compare autonomous baseline, selected human gates, and full co-pilot variant
  under the same budget.
- Repeat the MLAgentBench `vectorization` comparison with more seeds or add a
  second MLAgentBench task, then decide whether to expand to ScienceAgentBench.
- Add external or rubric-based paper-quality scoring.
- Run at least one frontier-model claim-audit pass through Monica routing if
  budget allows.
- Push the complete repository package to GitHub.
