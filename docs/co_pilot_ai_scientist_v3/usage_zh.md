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
  --program-iterations 1 \
  --run-autonomous-baseline \
  --autonomous-steps 3
```

这会在远端运行 FML-bench、OpenEvolve 和同次 autonomous AI Scientist-v2
baseline。它用于证明编排可行性并生成 paired smoke comparison；但规模仍太小，
不能支持一般性能优越性主张。

当前已归档 smoke 的同预算 autonomous comparison 位于
`experiments/online_smoke_matched_autonomous_comparison.md`。autonomous
baseline 在 held-out test MAE 上胜出，因此它应作为负结果模板使用。

如果要通过 Monica 路由运行 AI Co-Scientist 风格的 hypothesis-frontier
smoke，先加载全局环境变量，然后运行：

```bash
source ~/.codex/env
python3 scripts/run_hypothesis_frontier_smoke.py \
  --model gpt-4o-mini
```

这个脚本会生成候选 research frontiers，并输出 critique/ranking artifact。
它只能作为前端编排证据，不能作为 benchmark 或论文质量提升证据。

如果要把这个 IGRE 前端与同模型 autonomous AI Scientist-v2-style hypothesis
front end 做对照，运行：

```bash
source ~/.codex/env
python3 scripts/run_hypothesis_frontend_baseline.py \
  --model gpt-4o-mini
```

这个脚本只比较前端研究方向 portfolio，不能作为下游 benchmark、论文质量或人类专家判断的证据。

如果要把被选中的 structured-feedback frontier 接到下游同稿件测量探针，
运行：

```bash
source ~/.codex/env
python3 scripts/run_structured_feedback_probe.py \
  --model gpt-4o-mini
```

该脚本会生成 informal feedback、IGRE-structured feedback、同一份基础稿件的
两版修订，以及固定 rubric 的模型评分。它只能作为 measurement-readiness
evidence，不能替代独立人类同行评审。

如果要把 Hugging Face/OpenReview 专家评审数据作为离线科研品味先验来探测，
并且不下载完整数据集，运行：

```bash
python3 scripts/run_expert_review_taste_prior_probe.py \
  --streaming \
  --stream-limit 160
```

当前 probe 使用 `nhop/OpenReview`，先验证 Dataset Viewer metadata，再流式抽样。
它只能作为 offline expert-review proxy for scientific taste，不能当作实时
human co-pilot interaction data。建议的实验用法是：用同一个 OpenReview-derived
rubric 比较不同参与模式产生的 artifact，例如 no gate、taste-prior gate、
evaluator-stress gate、structured-feedback gate 和 claim-calibration gate。

如果要直接运行这种 participation-mode comparison，使用：

```bash
source ~/.codex/env
python3 scripts/run_participation_mode_selection_probe.py \
  --model gpt-4o-mini
```

如果要测试真实评审意见是否能改善 ML/AI mini-paper artifact 的再生成，运行：

```bash
source ~/.codex/env
python3 scripts/run_openreview_guided_regeneration_probe.py \
  --model gpt-4o-mini \
  --indices 1,34,49
```

如果要挖掘哪些评审意见最适合作为 IGRE gate 的科研品味/insight 控制信号，运行：

```bash
source ~/.codex/env
python3 scripts/run_review_insight_taxonomy_probe.py \
  --model gpt-4o-mini \
  --review-limit 32
```

如果要在更大的 OpenReview 样本上构造确定性的 review utility map，并且不增加
模型调用，运行：

```bash
python3 scripts/run_review_utility_map_probe.py
```

该脚本会把 review snippets 映射到可行动的 gate 控制信号，并区分真正有用的
evaluation concerns、claim-boundary issues、novelty positioning、
reproducibility details、concrete suggestions 与泛泛表扬、模糊反应。

如果要通过 Monica 做论文质量评审，先加载全局环境变量，然后运行：

```bash
source ~/.codex/env
python3 scripts/run_paper_quality_review.py \
  --models gpt-4o-mini claude-3-7-sonnet-latest \
  --max-tokens 4096
```

这个输出应作为审稿证据使用，而不是“已经被接收”的证明。

如果要检查 human gate 是否记录了可度量的人类注意力成本，运行：

```bash
python3 scripts/audit_human_gate_attention_cost.py
```

后续 matched-budget 实验中的每个 prospective gate log 都应该填写
`attention_cost.active_review_minutes`、
`attention_cost.wall_clock_latency_minutes`、`options_reviewed`、
`artifacts_reviewed_count` 和 `decision_count`。不要凭记忆估计旧日志；缺失就
明确记为缺失。

如果要从当前仓库 artifact 构建脱敏的 Human Co-Pilot Trace Dataset，运行：

```bash
python3 scripts/build_human_copilot_trace_dataset.py
```

它会写出 `human_copilot_trace_dataset.md/json`，索引 gate records、commits、
prospective packages 和 artifact links。它刻意不发布原始 Codex chat logs 或密钥，
因此应被视为单作者纵向过程数据，而不是总体人群层面的 human-subject 数据。

如果要做发布前审计，运行：

```bash
python3 scripts/audit_human_copilot_trace_dataset.py
```

当前审计会写出 `audits/human_copilot_trace_dataset_audit.md/json`，检查必需字段、
gate schema、主张边界，并扫描类似密钥的字符串与原始日志标记。当前版本通过审计，
secret-pattern hits 和 raw-log marker hits 都为 0。

如果要生成同时带完整 attention cost 和 scientific taste/insight 的 prospective gate log，可以使用：

```bash
python3 scripts/create_human_gate_log.py \
  --gate-id frontier_gate_live_001 \
  --gate-type frontier_steering \
  --research-task-id your_task_id \
  --option 'branch_a::Continue branch A' \
  --option 'branch_b::Stop branch B' \
  --human-decision branch_a \
  --rationale 'Human rationale here.' \
  --prompted-at-utc 2026-06-01T18:00:00Z \
  --decision-at-utc 2026-06-01T18:04:30Z \
  --active-review-minutes 3.5 \
  --artifacts-reviewed-count 1 \
  --taste-score problem_depth=5 \
  --taste-score novelty_potential=4 \
  --taste-score mechanistic_value=4 \
  --taste-score failure_informativeness=5 \
  --taste-score benchmark_taste=5 \
  --taste-score claim_significance=4 \
  --taste-score risk_asymmetry=4 \
  --taste-insight-score 4.43 \
  --taste-rationale 'Why this changes the search frontier.' \
  --non-metric-factor 'high-tail-research-upside' \
  --require-complete-attention \
  --require-complete-taste \
  --output docs/co_pilot_ai_scientist_v3/human_gate_logs/frontier_gate_live_001.json
```

如果要记录科研品味和 insight，使用：

```text
docs/co_pilot_ai_scientist_v3/taste_insight_rubric.md
```

当人类因为新颖性、失败价值、benchmark 品味或风险不对称性等非指标原因改变搜索前沿时，在 prospective gate log 中填写可选的 `taste_insight` 区块。不要把这个分数当作 reward model；它是可审计的搜索先验，必须和 autonomous baseline 的下游结果一起比较。

如果要检查已归档 gate 是否包含完整 taste/insight 记录，运行：

```bash
python3 scripts/audit_taste_insight_coverage.py
```

当前严格归档审计中已有 2 条完整 taste/insight 记录：一条来自作者关于 benchmark portfolio 和高尾部科研框架的决策，另一条来自本轮 operator-recorded 的“先补 attention/taste 测量、再谈更强人类效率主张”的决策。同时已有 1 条完整 attention-cost 记录。应把它视为 logging 和 measurement-readiness 证据，而不是“人类科研品味有效或无效”的性能结果。

如果要检查当前仓库是否已经包含合格的 prospective matched-budget package，
运行：

```bash
python3 scripts/audit_prospective_matched_budget_package.py
```

这是升级强主张之前的硬门槛。只有当一个非 synthetic package 同时包含
prospective co-pilot trajectory、同预算 autonomous baseline、所有 human gate
的完整 `attention_cost` 和 `taste_insight`、claim audit，以及同一次运行生成的
manuscript 时，这个 audit 才会通过。

如果要汇总这些通过 package 的实际指标结果，运行：

```bash
python3 scripts/summarize_prospective_matched_packages.py
```

它会写出 `audits/prospective_matched_package_summary.md/json`。这张表用于区分
“证据形状通过”和“benchmark 结果是否正向”。当前 summary 包含一个 controlled
micro-task 的 co-pilot 正结果，以及一个 FML-bench 的 co-pilot 负结果。

如果要重新生成 FML matched-comparison 总表，运行：

```bash
python3 scripts/summarize_fml_matched_comparisons.py
```

它会写出 `audits/fml_matched_comparison_summary.md/json`，并把正式两组
Causality replicate 和 online smoke comparison 分开报告。

如果要给当前 matched FML mini-manuscripts 做质量评分，运行：

```bash
python3 scripts/score_matched_manuscripts.py
```

它会为同一个 package 生成 autonomous mini-manuscript，并写出
`experiments/prospective_matched_fml_causality_20260602_000001/paper_quality/summary.md`。
这只是窄范围 manuscript-quality probe，不能当作完整 paper-quality 证明。

如果要重新生成确定性的 full-manuscript generation probe，运行：

```bash
python3 scripts/generate_full_manuscript_probe.py --update-manifest
python3 scripts/generate_full_manuscript_probe.py \
  --package-dir docs/co_pilot_ai_scientist_v3/experiments/prospective_matched_fml_fairness-fairlearn_20260602_002821 \
  --update-manifest
```

它会写出两篇完整论文形态 manuscript，并生成
所选 package 下的 `full_manuscript_probe/summary.md`。最新 Fairness package
probe 的内部 rubric 为 co-pilot `4.18`、autonomous `4.11`，但 autonomous
是唯一拥有有效 FML 标量测试指标的路径。
这只是基于已归档证据的 manuscript probe，不是 fresh end-to-end research
trajectory，也不是独立专家评审。

如果要从 online full-gate trajectory 生成论文形态 manuscript，运行：

```bash
python3 scripts/generate_online_trajectory_manuscript.py \
  --trajectory-json docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/trajectory.json \
  --autonomous-summary-json docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/autonomous_baseline_summary.json \
  --update-manifest
```

归档的 `online_full_gate_smoke_20260602_010521` 是 fresh online smoke
trajectory，并且包含同次运行的 autonomous baseline。传入 `--autonomous-summary-json` 后会写出
`online_manuscript/autonomous_online_comparator_manuscript.md` 和
`online_manuscript/matched_budget_comparison_summary.md`。

如果要对这组 paired manuscripts 运行 Monica 路由的 A/B 模型评审 probe，运行：

```bash
set -a; . ~/.codex/env; set +a
python3 scripts/score_matched_manuscripts.py \
  --co-pilot-manuscript docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/online_manuscript/co_pilot_online_full_gate_manuscript.md \
  --autonomous-manuscript docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/online_manuscript/autonomous_online_comparator_manuscript.md \
  --output-dir docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/online_manuscript/paper_quality \
  --probe-id online_full_gate_smoke_20260602_010521_same_continuous \
  --probe-kind full-manuscripts
```

这个输出只能作为模型评审的 measurement evidence，不能当作专家同行评审。

如果要汇总所有已经归档的 same-run paired online smokes，运行：

```bash
python3 scripts/summarize_online_paired_smokes.py --update-manifest
```

当前 repeated-smoke summary 包含 `3` 条 paired online run：两条有效
Causality 指标对照的结果是 `0` 次 co-pilot benchmark 胜、`1` 次
autonomous 胜、`1` 次打平，另有一条 Fairness no-valid failure trajectory。
它只能作为在线编排和 manuscript-measurement readiness 证据，不能当作
co-pilot benchmark 优越性的证据。

如果要在 `ubuntu-heshi` 上重新生成 controlled micro-pilot package 形状，运行：

```bash
python3 scripts/run_prospective_matched_budget_micro_pilot.py \
  --host ubuntu-heshi
python3 scripts/audit_prospective_matched_budget_package.py
```

它适合验证 package format，但不能替代 AI Scientist-v2/FML 或 MLAgentBench 的
prospective matched-budget 实验。

如果要运行当前最小的 FML-bench prospective matched package，使用：

```bash
python3 scripts/run_prospective_fml_matched_package.py \
  --host ubuntu-heshi \
  --task-config configs/tasks/causality_causalml.yaml \
  --benchmark-slug causality-causalml \
  --max-steps 2
python3 scripts/audit_prospective_matched_budget_package.py
```

如果要跑当前可用的 Fairness workspace，使用 `--task-config
configs/tasks/fairness_fairlearn.yaml --benchmark-slug fairness-fairlearn`。
当前归档的 FML packages 在这个预算下是 co-pilot performance 负结果或无有效
continuation 的失败案例，因此应把它们作为 pilot evidence 和后续更大运行的模板。

## 人类参与节点

- `scientific_taste_prior`：基于科研品味和上行空间选择或改写研究假设，而不只看当前分数。
- `evaluator_stress_test`：审批指标、baseline 和防投机失败条件。
- `frontier_steering`：决定哪些实验分支继续获得预算，包括当前分数不是最好但上行空间更大的分支。
- `verifiable_micro_evolution`：决定某个子问题是否值得深度代码进化。
- `claim_calibration`：删除、弱化或重写缺乏证据支持的论文主张。

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
