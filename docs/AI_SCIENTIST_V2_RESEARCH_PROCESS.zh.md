# AI Scientist V2 风格论文生成过程说明

本文档记录本仓库如何按 AI Scientist V2 风格完成一次端到端科研工作流：从选题、候选方向、实验设计、自动化实验、模型评审、论文写作，到最终提交包。研究主题是 AI 自动做科研、自动写论文、agent 自我进化和多 agent 协作。

## 1. 研究目标

最初目标不是只写一篇综述，而是让 agent 按科研流程产生可检验证据：

- 研究 AI Scientist / AI Scientist V2 式自动科研流程；
- 比较单 agent、多 agent、self-consistency、artifact evolution、structured memory 等工作流；
- 设计小型但可复现实验，记录所有生成 artifact；
- 用 DeepSeek 作为主要文本模型；
- 在需要多模态或外部 judge 时，通过 Monica OpenAI-compatible API 调用 `gpt-4o`；
- 最终生成一篇可作为 workshop draft 的科研论文和提交包。

当前版本的论文定位被刻意收窄为 pilot diagnostic study：它不声称证明多 agent 更好，也不声称评估完整科学发现能力，而是研究结构化 artifact-completeness rubric 与模型 judged quality 之间是否会出现分歧。

## 2. 环境和 API

全局环境文件位于：

```bash
$HOME/.config/ai_research_repro/.env
```

运行命令时使用：

```bash
export AI_RESEARCH_ENV_FILE="$HOME/.config/ai_research_repro/.env"
export PYTHONPATH=src
```

已验证的 provider 状态：

- DeepSeek text provider: `deepseek-chat`
- DeepSeek base URL: `https://api.deepseek.com`
- Monica VLM/text route: `gpt-4o`
- Monica base URL: `https://openapi.monica.im/v1`

注意：仓库不会提交 `.env` 或 API key。`.gitignore` 保留 `.env.example`，忽略真实 key 文件。

## 3. 方法设计

仓库实现了一个 compact AI Scientist V2 style benchmark。每个任务要求生成：

- hypothesis
- novelty check
- experiment plan
- required evidence coverage
- claim-evidence table
- limitations
- reproducibility commands

比较的工作流包括：

1. `author_curated_reference`：非 LLM、作者构造的结构化上界校准，不是 human baseline。
2. `fixed_template`：非 LLM 固定模板下界。
3. `single_fixed`：单 researcher agent。
4. `single_reflection`：单 agent 加反思。
5. `single_self_consistency`：六次独立尝试加一次综合，调用预算匹配 multi-agent。
6. `multi_fixed`：ideator、literature critic、experiment manager、coder、reviewer、writer 六角色。
7. `multi_artifact_evolution`：multi-agent 加 append-only policy update。
8. `multi_structured_evolution`：multi-agent 加结构化 failure memory 检索。

其中 artifact evolution 和 structured memory 只表示本仓库里的浅层机制，不代表所有 self-evolving agent 设计。

## 4. 实验树

### 4.1 五任务机制筛选

主运行目录：

```bash
runs/research_pilot_deepseek_v3
```

任务覆盖：

- novelty guard
- multi-agent topology evaluation
- artifact-evolution measurement
- VLM figure critic ablation
- paper claim-grounding audit

设置：

- model: `deepseek-chat`
- seeds: `0,1,2,3,4,5,6`
- methods: all eight workflows
- role mode: `orchestrated`

结果摘要：

- `author_curated_reference`: structural mean 134.0
- `multi_fixed`: structural mean 107.7143
- `multi_artifact_evolution`: structural mean 103.4286
- `multi_structured_evolution`: structural mean 99.8571
- `single_self_consistency`: structural mean 95.0
- `single_reflection`: structural mean 89.4286
- `single_fixed`: structural mean 87.0
- `fixed_template`: structural mean 52.0

这个实验用于发现机制现象，但任务数太小，不能作为强泛化结论。

### 4.2 二十任务主诊断实验

任务文件：

```bash
research_artifacts/ai_research_tasks_20.json
```

主合并目录：

```bash
runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek
```

这个实验只比较三个主要 budget-control 方法：

- `single_fixed`
- `single_self_consistency`
- `multi_fixed`

它不评估 artifact-evolution 方法。原因是 review 后论文范围被收窄为结构分数和 judged quality 的诊断分歧，而不是完整自进化方法胜负。

结构分数结果：

- `single_fixed`: 336.0
- `single_self_consistency`: 359.9
- `multi_fixed`: 428.7
- `multi_fixed - single_fixed` paired delta: +92.7，bootstrap interval [84.50, 99.80]

质量主分析结果：

- matched artifacts: 640
- DeepSeek judge + Monica/gpt-4o judge 都覆盖全部 640 artifacts
- inter-judge Pearson: 0.5783
- inter-judge Spearman: 0.5739
- `single_fixed` cross-judge mean quality: 3.5125
- `multi_fixed` cross-judge mean quality: 3.1900
- `single_self_consistency` cross-judge mean quality: 3.1075
- `multi_fixed - single_fixed` paired quality delta: -0.3225
- DeepSeek-only paired delta: -0.420
- Monica/gpt-4o-only paired delta: -0.225

关键结论：在这个协议里，multi-agent 和 extra-call self-consistency 获得更高的结构覆盖分数，但模型 judged scientific quality 低于 `single_fixed`。因此论文的贡献是 measurement / failure analysis，不是 multi-agent superiority claim。

### 4.3 Monica/gpt-4o generator sanity check

已有完成目录：

```bash
runs/ai_research_tasks20_monica_gpt4o_3seed
```

它使用 Monica routed `gpt-4o` 作为 generator，运行 seeds `0,1,2`，比较：

- `single_fixed`
- `multi_fixed`

结构结果：

- `single_fixed`: 318.6667
- `multi_fixed`: 409.6667

质量结果：

- `single_fixed`: 3.3083
- `multi_fixed`: 2.9417
- paired delta: -0.3667

这支持“现象不只在 DeepSeek 生成下出现”的 sanity check，但仍然不是充分的跨模型主实验。由于当前算力和 API 成本限制，额外 generator 模型和更大 seed/task 扩展留作后续学校算力集群上的工作。

### 4.4 AIRS / SVAMP 外部校准

仓库包含 AIRS official-definition planning tasks 和一个 task-local evaluator sanity check。

SVAMP evaluator run 是附录性质，只证明代码可以连接真实 evaluator，不是官方 leaderboard 结果，也不是多 agent 优势证据。

## 5. 自动审稿和论文修订

自动论文质量 review 文件：

```bash
runs/research_pilot_deepseek_v3/submission_package/paper_quality_review.json
```

当前状态：

- overall score: 5
- readiness: `workshop_draft`
- overclaiming risk: medium

review 反复指出：

- 主实验 generator 主要是 DeepSeek；
- 任务套件仍然是作者自建；
- 没有人类 expert calibration；
- Monica/gpt-4o generator check 只是 3 seeds；
- artifact evolution 结果不能推广到所有 self-evolving agents。

这些意见已经被写入论文限制和未来工作。当前阶段不继续追求人工校准，因为人工校准不能靠本机自动完成；更大模型/更多 seed 的实验也需要后续学校算力集群或更多 API 预算。

## 6. 最终论文包

主要论文输出：

```bash
runs/research_pilot_deepseek_v3/submission_package/paper.md
runs/research_pilot_deepseek_v3/submission_package/paper.tex
runs/research_pilot_deepseek_v3/submission_package/paper.pdf
```

当前标题：

```text
A Pilot Diagnostic Study of Structural and Judged Quality Signals in AI Research Workflows
```

提交包还包含：

- claim audit
- structural analysis
- quality-primary analysis
- DeepSeek judge output
- Monica/gpt-4o judge output
- judge comparison
- divergence analysis
- policy update analysis
- structured memory analysis
- role traces
- human-eval packet template
- code snapshot

其中大型 `runs/` 目录默认不提交 GitHub，以避免仓库过大；最终 PDF 会强制加入 Git，完整实验日志保留在本机。

## 7. 复现命令摘要

环境检查：

```bash
PYTHONPATH=src AI_RESEARCH_ENV_FILE="$HOME/.config/ai_research_repro/.env" \
python3 -m ai_research_repro.cli doctor
```

主五任务实验：

```bash
PYTHONPATH=src AI_RESEARCH_ENV_FILE="$HOME/.config/ai_research_repro/.env" \
python3 -m ai_research_repro.cli research-benchmark \
  --workspace runs/research_pilot_deepseek_v3 \
  --model deepseek-chat \
  --seeds 0,1,2,3,4,5,6 \
  --role-mode orchestrated
```

20-task 主诊断实验的具体 merge / judge / divergence 命令见：

```bash
research_artifacts/reproducibility_checklist.md
```

论文重建：

```bash
PYTHONPATH=src AI_RESEARCH_ENV_FILE="$HOME/.config/ai_research_repro/.env" \
python3 -m ai_research_repro.cli write-paper-from-results \
  --results runs/research_pilot_deepseek_v3/research_benchmark_results.json \
  --base-draft research_artifacts/paper_draft.md \
  --output research_artifacts/paper_with_results.md

PYTHONPATH=src AI_RESEARCH_ENV_FILE="$HOME/.config/ai_research_repro/.env" \
python3 -m ai_research_repro.cli export-paper-package \
  --paper research_artifacts/paper_with_results.md \
  --output-dir runs/research_pilot_deepseek_v3/submission_package \
  --results-dir runs/research_pilot_deepseek_v3 \
  --references research_artifacts/references.bib
```

PDF 编译：

```bash
python3 /Users/hgh54913/.codex/plugins/cache/openai-bundled/latex/0.2.2/scripts/compile_latex.py \
  --compiler tectonic \
  runs/research_pilot_deepseek_v3/submission_package/paper.tex
```

## 8. 当前阶段结论

当前仓库完成了一个诚实的 workshop draft：

- 有可运行代码；
- 有多种 workflow；
- 有 repeated-seed 主实验；
- 有 DeepSeek 和 Monica/gpt-4o 双 judge；
- 有外部 generator sanity check；
- 有 claim audit 和自动 paper review；
- 有完整论文草稿和 PDF。

但它还不是强结论论文。下一阶段应在学校算力集群或更高预算下补：

- 50+ task suite；
- 至少一个额外 generator 的 10-seed 主实验；
- 人类专家子集评价；
- 更简单的 multi-agent topology ablation；
- 更强的 artifact-evolution / memory update 机制。

因此当前最准确的定位是：一个可复现、证据链完整、限制写清楚的 AI Scientist V2 风格自动科研 pilot paper。
