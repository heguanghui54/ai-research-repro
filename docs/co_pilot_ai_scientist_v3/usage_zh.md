# Co-Pilot AI Scientist v3 使用说明

## 这个流程做什么

这个 workflow 把一个研究主题转化为“人类参与的自动科研循环”。它保留 AI Scientist-v2 的自动化能力，但在人类判断最有价值的位置加入明确的 gate。

## 最小运行流程

1. 从 `problem_statement.md` 开始确认研究问题。
2. 生成候选假设，并写入 `candidates.json`。
3. 让人类研究者审批或改写最好的假设。
4. 把通过的假设转化为 benchmark、baseline 和 evaluator。
5. 在同样预算下运行完全自动版本和 human-gated 版本。
6. 对机器可评分的子问题调用 OpenEvolve 或类似代码进化循环。
7. 只根据日志和指标写论文，不编造结果。
8. 生成 PDF 前进行最终主张审计。
9. 跑一次 paper-quality review，并根据审稿意见弱化缺乏证据的顶会级主张。

当前项目包已经包含一次示例 claim audit，位于
`docs/co_pilot_ai_scientist_v3/audits/`。后续运行也应沿用这个模式：在最终
PDF 生成前，把每条主张标记为 supported、partially supported、unsupported
或 overstated。

如果要重新生成当前 executable gate-chain replay，运行：

```bash
python3 scripts/run_full_gate_trajectory.py
```

这会写入 `experiments/full_gate_executable_trace/trajectory.json` 和
`README.md`。它是对已归档 artifact 的可复现检查，不是一次新的在线
full-gate 实验。

如果要在 `ubuntu-heshi` 上启动一个小预算的 fresh online full-gate smoke
trajectory，运行：

```bash
python3 scripts/run_online_full_gate_smoke.py \
  --branch-steps 2 \
  --continuation-steps 1 \
  --program-iterations 1
```

这会远端运行 FML-bench 和 OpenEvolve。它用于证明编排可行性；在任何性能
主张之前，仍需要同预算 autonomous baseline。

当前已归档 smoke 的同预算 autonomous comparison 位于
`experiments/online_smoke_matched_autonomous_comparison.md`。autonomous
baseline 在 held-out test MAE 上胜出，因此它应作为负结果模板使用。

如果要通过 Monica 做论文质量评审，先加载全局环境变量，然后运行：

```bash
source ~/.codex/env
python3 scripts/run_paper_quality_review.py \
  --models gpt-4o-mini claude-3-7-sonnet-latest \
  --max-tokens 4096
```

这个输出应作为审稿证据使用，而不是“已经被接收”的证明。

## 人类参与节点

- `idea_selection`：选择或改写研究假设。
- `evaluator_approval`：审批指标、baseline 和失败条件。
- `branch_selection`：决定哪些实验分支继续获得预算。
- `program_search_escalation`：决定某个子问题是否值得深度代码进化。
- `claim_audit`：删除或弱化缺乏证据支持的论文主张。

## 环境建议

API key 使用全局环境变量，不在日志中打印。建议：

- DeepSeek 用于低成本代码生成和 smoke test。
- Monica 聚合的 GPT/Gemini/Anthropic 用于假设辩论、高风险审稿和最终写作。
- 较重 benchmark 放到 SSH 控制的 Ubuntu 机器上运行。

## Benchmark 选择

不要把所有主张都默认交给 FML-bench。应按主张类型选择 benchmark：

- FML-bench：用于 AI Scientist-v2 风格 branch gate 和 continuation。
- OpenEvolve-controlled tasks：当前包括函数最小化、knapsack 和 Max-Cut，
  用于机器可评分的算法/程序搜索。
- MLAgentBench：用于非 FML 的 ML 实验与 correctness-gated 代码优化。
- 受控 sklearn tabular probes：当外部 benchmark 凭证不可用时，用于低成本非
  FML 建模证据和 escalation 边界测试。
- ScienceAgentBench：用于数据驱动科学发现，但必须先在 Ubuntu 主机下载
  verified benchmark artifacts。
- PaperBench-style rubric：当完整 PaperBench 太贵时，用于 claim 和 manuscript
  quality audit。

## OpenEvolve 子问题搜索

使用 OpenEvolve 作为 AlphaEvolve-style 优化的开源替代实现。官方
AlphaEvolve 系统没有开源，所以论文中应写成 “AlphaEvolve-style” 或
“基于 OpenEvolve”，不能声称复现了官方 AlphaEvolve。

使用本仓库 wrapper 的最小 OpenEvolve 命令：

```bash
python3 scripts/run_openevolve_program_search.py \
  --initial-program docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/initial_program.py \
  --evaluator docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/evaluator.py \
  --output-dir /tmp/knapsack_openevolve_5iter/run \
  --iterations 5 \
  --provider deepseek \
  --model deepseek-chat
```

如果走 Monica 聚合接口，使用 `--provider monica --model <model-name>`，并确保
shell 中已有 `MONICA_API_KEY` 和 `MONICA_BASE_URL`。

完整复现路径见 `RUNBOOK_ZH.md`。
