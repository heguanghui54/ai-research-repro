# FML-bench 中文复现说明

本文档说明如何在 SSH 控制的 Ubuntu 机器上，基于官方仓库
[qrzou/FML-bench](https://github.com/qrzou/FML-bench) 做低成本最小复现。

本次复现遵循论文和官方仓库的核心流程：给定一个机器学习任务、baseline
代码、验证命令和测试命令，让研究 agent 修改目标文件，反复运行验证集，
最后选择验证集上最好的方案并在测试集上评估。

## 复现范围

本次完成的是低成本最小复现，不是完整 18 个任务的论文级全量 sweep。

已经在 Ubuntu 上实际验证的官方任务有两个：

- `Causality_causalml`
- `Fairness_fairlearn`

LLM API 使用顺序为：

1. `DeepSeek`
2. `Monica`

实际跑通的两次官方 benchmark 都使用 `DeepSeek`，模型为 `deepseek-chat`。

## 已验证结果

### 任务一：Causality_causalml

运行设置：

- 官方仓库：`qrzou/FML-bench`
- agent：`ai_scientist_v2`
- provider：`DeepSeek`
- model：`deepseek-chat`
- step budget：`4`

结果：

- Best Val Metric：`0.5989426968010781`
- Test Metric：`0.6177188971481032`
- Total Steps：`4`

Ubuntu 上的结果文件：

```text
/home/heshi/work/fmlbench-smoke-results-fixed2/ai_scientist_v2/Causality_causalml/20260530_004241_dced73c8/summary.json
```

### 任务二：Fairness_fairlearn

运行设置：

- 官方仓库：`qrzou/FML-bench`
- agent：`ai_scientist_v2`
- provider：`DeepSeek`
- model：`deepseek-chat`
- step budget：`4`

结果：

- Best Val Metric：`0.3164673438990605`
- Test Metric：`0.31600465679075357`
- Total Steps：`4`

Ubuntu 上的结果文件：

```text
/home/heshi/work/fmlbench-fairlearn-results-fixed3/ai_scientist_v2/Fairness_fairlearn/20260530_010425_087411ff/summary.json
```

## Ubuntu 环境准备

登录 Ubuntu：

```bash
ssh ubuntu-heshi
```

克隆官方仓库：

```bash
mkdir -p ~/work
cd ~/work
git clone https://github.com/qrzou/FML-bench.git
cd FML-bench
```

安装 conda 环境和任务环境。最小复现只需要先装单个任务：

```bash
python setup.py --task Causality_causalml
```

Fairlearn 任务需要：

```bash
python setup.py --task Fairness_fairlearn --skip-data
```

如果要完整论文级任务集合，可以运行：

```bash
python setup.py
```

这一步会明显更耗时，也会下载更多任务仓库和数据。

## 配置 DeepSeek

优先使用 DeepSeek：

```bash
export DEEPSEEK_API_KEY="your_deepseek_key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export CUDA_VISIBLE_DEVICES=0
```

官方仓库如果没有 DeepSeek provider 分支，可以用本仓库提供的补丁脚本：

```bash
python /path/to/ai-research-repro/scripts/patch_fmlbench_deepseek_provider.py \
  --repo /path/to/FML-bench
```

## 配置 Monica 备用

如果 DeepSeek 不可用，再使用 Monica：

```bash
python /path/to/ai-research-repro/scripts/patch_fmlbench_monica_provider.py \
  --repo /path/to/FML-bench

export MONICA_API_KEY="your_monica_key"
export MONICA_BASE_URL="https://openapi.monica.im/v1"
```

运行时把 provider 改为 `Monica`，model 改成 Monica 支持的模型即可。

## 运行 Causality_causalml 最小复现

在官方 `FML-bench` 仓库根目录执行：

```bash
cd /home/heshi/work/FML-bench

env DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
  DEEPSEEK_BASE_URL="https://api.deepseek.com" \
  CUDA_VISIBLE_DEVICES=0 \
  /home/heshi/miniconda3/bin/conda run -n fmlbench \
  python run_agent_benchmark.py \
  --agent-config configs/agents/ai_scientist_v2.yaml \
  --task-config configs/tasks/causality_causalml.yaml \
  --model deepseek-chat \
  --provider DeepSeek \
  --output-dir /home/heshi/work/fmlbench-smoke-results \
  agent.ai_scientist_v2.max_steps=4
```

成功时，终端最后应出现类似信息：

```text
Best Val Metric: ...
Test Metric: ...
Total Steps: 4
Summary saved to: ...
```

## 运行 Fairness_fairlearn 最小复现

Fairlearn 任务在当前 Ubuntu 环境中需要一个兼容性补丁，因为安装的
Fairlearn 版本不接受 `ExponentiatedGradient(random_state=...)`。

先打补丁：

```bash
python /path/to/ai-research-repro/scripts/patch_fmlbench_fairlearn_compat.py \
  --repo /home/heshi/work/FML-bench
```

然后运行：

```bash
cd /home/heshi/work/FML-bench

env DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
  DEEPSEEK_BASE_URL="https://api.deepseek.com" \
  CUDA_VISIBLE_DEVICES=0 \
  /home/heshi/miniconda3/bin/conda run -n fmlbench \
  python run_agent_benchmark.py \
  --agent-config configs/agents/ai_scientist_v2.yaml \
  --task-config configs/tasks/fairness_fairlearn.yaml \
  --model deepseek-chat \
  --provider DeepSeek \
  --output-dir /home/heshi/work/fmlbench-fairlearn-results \
  agent.ai_scientist_v2.max_steps=4
```

## 使用 helper 脚本

本仓库也提供了 helper：

```bash
FMLBENCH_REPO_DIR=/home/heshi/work/FML-bench \
FMLBENCH_PROVIDER=DeepSeek \
FMLBENCH_MODEL=deepseek-chat \
FMLBENCH_MAX_STEPS=4 \
  bash /path/to/ai-research-repro/scripts/fmlbench_smoke_test.sh
```

helper 默认跑 `Causality_causalml`。如需切换任务，可以设置：

```bash
export FMLBENCH_TASK=Fairness_fairlearn
export FMLBENCH_TASK_CONFIG=configs/tasks/fairness_fairlearn.yaml
```

## 成本控制

为了把成本控制在几美元以内，本次复现采用：

- 只跑两个官方任务，而不是 18 个任务全量 sweep
- 每个任务只设置 `agent.ai_scientist_v2.max_steps=4`
- 优先使用 `DeepSeek`
- 只在 DeepSeek 不可用时切换到 `Monica`

本次已验证运行的 token 用量为：

- `Causality_causalml`：约 `16,217` tokens
- `Fairness_fairlearn`：约 `15,096` tokens

## 与论文全量复现的差异

本说明复现的是 FML-bench 的官方运行闭环：

- 官方任务配置
- 官方 agent 入口
- LLM 生成代码修改
- 验证集评估
- 测试集评估
- 结果写入 `summary.json`

它没有复现论文中的完整 18 任务、多轮、多模型统计结果。要继续扩展到更接近论文级别，需要：

- 对 `configs/tasks/` 下更多任务重复 setup 和 run
- 提高 `agent.ai_scientist_v2.max_steps`，例如接近官方示例的 `100`
- 准备更多 API 预算和机器运行时间
- 对多个任务结果做汇总分析

## 本仓库新增文件

关键文件如下：

- `docs/fmlbench_official_ubuntu_runbook.md`
- `docs/fmlbench_verification_log.md`
- `docs/fmlbench_中文复现说明.md`
- `scripts/fmlbench_smoke_test.sh`
- `scripts/patch_fmlbench_deepseek_provider.py`
- `scripts/patch_fmlbench_monica_provider.py`
- `scripts/patch_fmlbench_fairlearn_compat.py`
- `scripts/bootstrap_causalml_smoke_repo.py`

