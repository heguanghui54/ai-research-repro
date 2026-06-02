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

For long-horizon scientific taste, also log whether a decision is an LHTG/DVRS
candidate. This is the case where human review may introduce short-term
friction but could point the agent toward later mainstream or SOTA directions.
Do not score such cases as positive until Temporal Frontier Replay validates
paper-only, review-guided, and shuffled-review-control conditions against
later-field evidence.

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
- Matched autonomous 4-step baseline: same task/model with four total steps,
  no human branch selection, reaching validation MAE `0.38945144308464624` and
  test MAE `0.42147360723655275`.
- Second matched pair: the selected human-gated continuation reached validation
  MAE `0.627836868090553` and test MAE `0.6462237240158367`, while the paired
  autonomous 4-step baseline reached validation MAE `0.5379716029896986` and
  test MAE `0.5956850978622356`. This makes the paired FML evidence mixed.

The current continuation is implemented by snapshot seeding. A stronger future
version should preserve and resume the original AI Scientist-v2 tree object.

## 6A. Long-Horizon Taste Gate / DVRS Audit

Run the delayed-value candidate and audit path locally:

```bash
python3 scripts/run_delayed_value_review_candidate_mining.py
python3 scripts/run_delayed_value_candidate_frontier_validation.py
python3 scripts/audit_temporal_frontier_replay.py
python3 scripts/audit_long_horizon_taste_gate.py
```

Expected current boundary:

- delayed-value replay candidates: `120`;
- positive delayed-value cases: `0`;
- LHTG/DVRS status: operationalized, with no positive delayed-value proof.

Use this as a routing and falsifiability audit. It is not evidence that human
reviews already improve long-horizon discovery.

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

Run the matched autonomous baseline from the official FML-bench repository:

```bash
ssh ubuntu-heshi
source /home/heshi/miniconda3/etc/profile.d/conda.sh
source ~/.codex/env
cd /home/heshi/work/FML-bench
TMP=$(mktemp /tmp/copilotv3_autonomous_matched_XXXX.yaml)
python3 - <<PY
from pathlib import Path
text = Path("configs/agents/ai_scientist_v2.yaml").read_text()
text = text.replace("num_ideas: 3", "num_ideas: 2")
text = text.replace("num_parallel: 4", "num_parallel: 2")
text = text.replace(
    "stage_budgets: [0.10, 0.20, 0.50, 0.20]",
    "stage_budgets: [0.50, 0.50, 0.0, 0.0]",
)
Path("$TMP").write_text(text)
PY
conda run -n fmlbench python run_agent_benchmark.py \
  --agent-config "$TMP" \
  --task-config configs/tasks/causality_causalml.yaml \
  --model deepseek-chat \
  --provider DeepSeek \
  --output-dir /home/heshi/work/copilotv3-autonomous-matched-budget-4step \
  agent.ai_scientist_v2.max_steps=4
rm -f "$TMP"
```

Archive path:
`docs/co_pilot_ai_scientist_v3/experiments/fml_autonomous_matched_budget_4step/`.

Second-pair archive paths:

- `docs/co_pilot_ai_scientist_v3/experiments/fml_matched_budget_rep2_gated_drafts/`
- `docs/co_pilot_ai_scientist_v3/experiments/fml_matched_budget_rep2_selected_continuation/`
- `docs/co_pilot_ai_scientist_v3/experiments/fml_matched_budget_rep2_autonomous_4step/`

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

Repeat the same 3-iteration setting with explicit seeds:

```bash
for seed in 0 1 2 3 4 7 42 123; do
  python scripts/run_openevolve_program_search.py \
    --initial-program docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_task/initial_program.py \
    --evaluator docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_task/evaluator.py \
    --output-dir "docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_openevolve_3iter_seed${seed}" \
    --iterations 3 \
    --random-seed "${seed}" \
    --provider deepseek \
    --model deepseek-chat
done
```

Archived results for seeds `0`, `1`, `2`, `3`, `4`, `7`, `42`, and `123`
retained correct best programs in all 8 runs and improved over the controlled
starter in all 8 runs. The median best runtime was `0.024580717086791992`
seconds, with a median speedup of about `132.67x`. The multi-seed probe
broadens the benchmark evidence beyond FML-Bench, but it still shows
seed/budget sensitivity under a tiny search budget.

## 9. Controlled Tabular Modeling Probe

The sklearn diabetes tabular regression probe is a second non-FML path that
does not depend on Kaggle credentials:

```bash
source ~/.codex/env
python scripts/run_direct_llm_program_baseline.py \
  --initial-program docs/co_pilot_ai_scientist_v3/experiments/sklearn_diabetes_tabular_task/initial_program.py \
  --evaluator docs/co_pilot_ai_scientist_v3/experiments/sklearn_diabetes_tabular_task/evaluator.py \
  --output-dir docs/co_pilot_ai_scientist_v3/experiments/sklearn_diabetes_direct_deepseek_dummy \
  --signature "def train_and_predict(X_train, y_train, X_eval):" \
  --task-description "Improve predictive performance on the sklearn diabetes tabular regression task." \
  --provider deepseek \
  --model deepseek-chat
```

Then run small OpenEvolve seeds:

```bash
for seed in 0 1 2; do
  python scripts/run_openevolve_program_search.py \
    --initial-program docs/co_pilot_ai_scientist_v3/experiments/sklearn_diabetes_tabular_task/initial_program.py \
    --evaluator docs/co_pilot_ai_scientist_v3/experiments/sklearn_diabetes_tabular_task/evaluator.py \
    --output-dir "docs/co_pilot_ai_scientist_v3/experiments/sklearn_diabetes_openevolve_3iter_dummy_seed${seed}/run" \
    --iterations 3 \
    --random-seed "${seed}" \
    --provider deepseek \
    --model deepseek-chat
done
```

Archived results: initial mean predictor RMSE `78.572189`; direct DeepSeek
rewrite RMSE `55.895460`; OpenEvolve seeds `0`, `1`, and `2` all improve over
the mean predictor with median RMSE `55.895460`. This is a boundary condition:
direct editing matches OpenEvolve on a simple standard modeling change.

## 10. Remaining Evidence Needed Before Strong Submission Claims

- Replace snapshot-seeded continuation with native tree-object resume if
  feasible.
- Extend the current two mixed matched-budget Causality pairs across more
  tasks, seeds, and budget schedules.
- Add a second official MLAgentBench task or download the verified
  ScienceAgentBench artifacts and run a first ScienceAgentBench instance.
- Add external or rubric-based paper-quality scoring.
- Run a full four-loop trajectory where hypothesis, evaluator, branch,
  program-search, and claim-audit gates all operate in one continuous run.
- Push the complete repository package to GitHub.

## 11. Monica-Routed Paper-Quality Review

The current package includes two model-review artifacts. Re-run them with:

```bash
source ~/.codex/env
python3 scripts/run_paper_quality_review.py \
  --models gpt-4o-mini claude-3-7-sonnet-latest \
  --max-tokens 4096
```

The archived reviews disagree on recommendation (`Weak accept` versus
`Reject`) but agree that matched-budget human-gate comparisons and a complete
four-loop trajectory are required before strong submission claims.
