# 复现运行手册

本手册用于复现当前 Co-Pilot AI Scientist v3 研究包。环境包括本地
macOS 仓库和 SSH Ubuntu 主机 `ubuntu-heshi`。

## 1. 本地生成 PDF

在仓库根目录运行：

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_copilot_v3_pdfs.py --language both
```

预期输出：

- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_en.pdf`
- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_zh.pdf`

## 2. 校验本地产物

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

## 3. Ubuntu 环境

在远程主机上运行：

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

需要的环境变量：

- `DEEPSEEK_API_KEY`，可选 `DEEPSEEK_BASE_URL`
- `MONICA_API_KEY`，可选 `MONICA_BASE_URL`

目前已验证的初步实验使用 DeepSeek 的 OpenAI-compatible API。不要把 API
key 打印进日志。

## 4. Direct LLM 基线

当 evaluator 暴露 `evaluate(path) -> dict` 时，可使用通用基线脚本：

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

已归档实验的平均比值为 `0.9952700988954383`。

## 5. OpenEvolve 程序搜索

由于官方 AlphaEvolve 系统没有开源，本项目使用 OpenEvolve 作为
AlphaEvolve-style 开源实现基底。

```bash
python3 scripts/run_openevolve_program_search.py \
  --initial-program docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/initial_program.py \
  --evaluator docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/evaluator.py \
  --output-dir /tmp/knapsack_openevolve_5iter/run \
  --iterations 5 \
  --provider deepseek \
  --model deepseek-chat
```

已归档实验的平均比值为 `0.9994394752555711`，在这个较复杂的启发式任务上
高于 direct rewrite 基线。

## 6. 人类 gate 日志

每个人类决策点都应写出符合 `human_gate_schema.json` 的 JSON 日志。新运行
可以复用 `skills/co-pilot-ai-scientist-v3/templates/` 中的模板。

当前 replay 和 live-probe 证据：

- Causality FML replay：停止较弱的第二个 draft，继续较强的第一分支。
- Fairness FML replay：在性能变差和出现 bug 后暂停，重置 evaluator 或算法选择。
- 在线 Causality 两 draft 小实验：选择第二个 draft，因为其验证 MAE
  `0.6212624733836205` 明显低于第一个 draft 的 `1.1496098661684393`。
- Selected-branch continuation：应用被选中的 step 2 快照，再继续运行
  AI Scientist-v2 两步，得到验证 MAE `0.4012397173613497` 和 test MAE
  `0.4021701846791075`。

当前 continuation 通过 snapshot seeding 实现。更强版本应保存并恢复原始
AI Scientist-v2 tree object。

## 7. 所选分支 continuation

把 continuation runner 和被选中的快照复制到 Ubuntu 主机：

```bash
scp scripts/run_fmlbench_snapshot_continuation.py \
  ubuntu-heshi:/home/heshi/work/co-pilot-ai-scientist-v3/run_fmlbench_snapshot_continuation.py
scp docs/co_pilot_ai_scientist_v3/experiments/fml_online_branch_gate_drafts/step_0002_code.json \
  ubuntu-heshi:/home/heshi/work/co-pilot-ai-scientist-v3/selected_step_0002_code.json
```

在官方 FML-bench 仓库中运行：

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

## 8. 非 FML 的 MLAgentBench baseline

把 MLAgentBench `vectorization` 作为第一条非 FML benchmark 路径：

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

已归档官方 baseline：final runtime score 为 `3.17250394821167` 秒，total
benchmark time 为 `3.3655309677124023` 秒。该任务分数越低越好。

`docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_task/`
中的受控 evaluator 会先做 correctness gate，再接受 runtime。在该 evaluator 下：

- starter program median runtime：`3.261186361312866` 秒；
- direct DeepSeek rewrite：未通过 correctness gate；
- OpenEvolve-style search，3 iterations：找到正确 best program，median
  runtime 为 `0.051882028579711914` 秒。

## 9. 顶会级投稿前仍需补强的证据

- 如果可行，把 snapshot-seeded continuation 升级为原生 tree-object resume。
- 在同等预算下比较 autonomous baseline、单个 human gate 和 full co-pilot variant。
- 在 MLAgentBench `vectorization` 上做更多 seed，或加入第二个 MLAgentBench task，然后再决定是否扩展到 ScienceAgentBench。
- 加入外部评审或 rubric-based paper-quality scoring。
- 如果预算允许，通过 Monica 路由跑一次 frontier model claim audit。
- 将完整项目包推送到 GitHub。
