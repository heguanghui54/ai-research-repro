# Co-Pilot AI Scientist v3：面向协作式自动科研的洞察门控科研演化

**作者：**何石，新加坡国立大学计算机学院

## 摘要

自动科研智能体已经开始把创意生成、实验执行、benchmark 评估和论文写作连接成闭环。然而，完全自动化的科研流水线仍然难以处理一些关键节点：选择什么问题值得做、如何判断证据强弱、如何解释失败结果、以及哪些结论可以负责任地写进论文。本文提出 Co-Pilot AI Scientist v3 及其核心方法：洞察门控科研演化（Insight-Gated Research Evolution, IGRE）。IGRE 不是把已有科研 agent 直接拼装在一起，而是把其中有用的设计压力重新组织成一个面向高尾部科研产出的过程：自动系统维持广泛、可执行的搜索前沿，人类则在显式 gate 中注入科研品味、风险偏好和主张责任。本文定义一个可复现评估协议，用于比较完全自动、局部 gate 和完整 co-pilot 版本在小型自动科研任务上的表现。核心假设是非对称的：人类参与可能降低短预算 benchmark 的平均表现，但可能提高产生高新颖性、高影响力科研结果的概率，而这类高尾部结果才是科学发现中最重要的部分。

## 1. 引言

自动科研的下一步，不应该只是“无人参与的论文工厂”。科学研究不仅是可执行步骤的串联，也包括选择有价值问题、识别弱证据、重新解释失败、决定哪些主张值得提出。已有系统提供了重要启发：假设辩论、可执行实验搜索、以及自动评估驱动的代码演化。但本文的方法目标不同：科研 co-pilot 不应只最大化短期 benchmark 的平均分，还应提高系统进入质变方向的概率，例如更尖锐的问题、更能揭示机制的 evaluator、更有解释力的失败、或者能打开新研究线索的主张。

本文提出 Co-Pilot AI Scientist v3，并把它形式化为洞察门控科研演化。目标不是用随意审批拖慢自动流水线，而是把人类介入视为一种稀缺、高方差的搜索算子，只在科研判断能改变搜索前沿形状的位置触发。本文定义五类 gate：科研品味先验、评估器压力测试、前沿转向、可验证微演化，以及主张校准。

## 2. 相关工作

AI Co-Scientist 将科学发现建模为假设生成、讨论和演化，优势在于研究早期的想象力和证据组织。AI Scientist-v2 通过 agentic tree search 将候选想法转化为可运行实验和论文。AlphaEvolve 使用自动评估驱动代码进化，适合机器可评分问题。FunSearch 是 LLM 引导程序搜索用于数学发现的早期代表。Coscientist 则展示了 LLM agent 如何连接化学工具和实验自动化。

IGRE 借鉴这些系统带来的设计压力，但不照搬它们的控制逻辑。它从假设生成系统中吸收多样化 conjecture 的需求，但把自由辩论改造成可记录的科研品味先验；它从自动论文系统中吸收可执行实验搜索，但在 benchmark 分数不足以决定方向的地方加入前沿转向和主张校准；它从程序演化系统中吸收机器可评分子问题的深度搜索，但通过选择性升级 gate 控制成本和适用范围。因此，本文优化的不是单个任务指标，而是一条证据对齐、上限更高的科研轨迹。

### 2.1 与一般科研 co-pilot 的区别

很多 co-pilot 系统把人类看作审批者、提示词编写者、偏好标注者或异常兜底者。IGRE 的算法主张不同：人类对自动科研最重要的贡献，往往是对“什么样的科研值得做”的非指标化先验，也就是科研品味。这种先验很难压缩成单一 reward。它包括：一个问题是否有深度，一个负结果是否揭示机制，一个 benchmark 是否太容易被投机，一个看似当前分数不高的分支是否值得保留，以及一个主指标只小幅提升的结果是否仍然值得写成论文主张。

因此，IGRE 区分了三种在人机协作 agent 中经常被混在一起的角色。**偏好**是在人类已经看到若干完成选项后选择更喜欢的一个；**监督**是阻止无效或不安全行为；**科研品味**则是在结果尚未显现之前改变系统应该搜索什么。第三种才是本文的核心区别。IGRE 不把 taste 强行拟合成完整 reward model，而是把它记录为结构化、可审计、但保留部分定性判断的 gate record，用它改变搜索前沿。这样，系统可以诚实评估人类输入：它可能降低平均分，但应该被检验的是它是否提高了少数开创性科研轨迹出现的概率。

## 3. 方法

Co-Pilot AI Scientist v3 实现的是洞察门控科研演化。IGRE 包含四个机器循环和五个面向人类的算子。机器循环保留自动科研的规模化能力：假设扩展、实验构造、可执行前沿搜索和可验证微演化。人类算子则放在科研品味可能改变“哪些前沿值得继续展开”的位置。

图 1 展示了系统的数据流：研究目标先进入假设循环，再进入实验构造和可执行前沿搜索；对于机器可评分子问题，系统可以升级到基于 OpenEvolve 的可验证微演化；最后进入论文生成和主张校准。每个 gate 都接收结构化的候选前沿，并输出可复现的决策记录。

```text
研究目标 -> 假设循环 -> 实验循环 -> 搜索循环
        |          |          |          |
  科研品味先验  评估器压力测试  前沿转向  微演化 gate
                                      |
                                      v
                         可验证微演化
                                      |
                                      v
                         论文草稿 -> 主张校准 gate
                                      |
                                      v
                         证据对齐的论文包
```

第一，科研品味先验让人类科学家根据早期指标难以捕捉的标准选择、合并或改写方向：概念新鲜度、领域重要性、上行空间的不对称性，以及即使失败也是否能带来有价值的知识。

第二，评估器压力测试把被选中的假设转化为 benchmark、baseline、消融实验、可执行脚本和拒绝条件。这个 gate 不只问指标是否方便，还要问指标是否会被投机、是否漏掉最低效用、以及如果结果为正是否真的能支撑论文主张。

第三，前沿转向 gate 运行在可执行实验分支之上。在预设检查点，系统总结指标、代码快照、错误和新颖性线索。人类科学家可以把预算分给当前主指标并非最优、但科研上行空间更大或失败模式更重要的分支。

第四，可验证微演化 gate 只把机器可评分的子问题交给代码演化引擎。由于官方 AlphaEvolve 没有开源核心系统，本文的可复现实验使用 OpenEvolve 作为实际实现底座。OpenEvolve 提供自定义 evaluator、OpenAI-compatible 模型路由、MAP-Elites 质量多样性搜索、岛屿种群和可复现随机种子。该算子进化代码、保存候选程序，并把通过验证的改进返回主科研流程。

第五，主张校准 gate 把最终论文草稿和证据记录逐条对齐。它会削弱、删除或重写尚未被支持的主张，并记录哪些更强主张仍然只是下一阶段 benchmark 要检验的假设。

```text
算法 1：洞察门控科研演化（IGRE）
输入：研究目标 g，benchmark 预算 B，人类注意力预算 H
1. 从 g 生成多样化假设前沿 F_h。
2. 执行 scientific_taste_prior(F_h, H)，选择或改写高上行空间假设，
   包括当前指标尚未显现价值的分支。
3. 将被选假设转化为 evaluator、baseline 和失败测试。
4. 执行 evaluator_stress_test，拒绝不可执行、易被投机、
   或不足以支撑论文主张的指标。
5. 在预算 B 下运行可执行前沿搜索，并记录分支状态。
6. 在检查点执行 frontier_steering，用指标、定性上行空间和失败价值共同分配预算。
7. 对机器可评分子问题，仅当直接编辑不足且 evaluator 可靠时，
   执行 verifiable_micro_evolution。
8. 根据日志生成论文草稿，再执行 claim_calibration，
   将主张与证据对齐，并把未支持结论降级为未来假设。
输出：证据对齐的论文包和可审计 gate 轨迹。
```

每一次人类介入都被记录为结构化数据，包括决策类型、候选选项、理由、影响到的产物和后续结果。这样，人类参与不是隐藏的旁路，而是可复现记录的一部分。

当前 artifact package 还加入了一条 retrospective full-gate trajectory，覆盖本文提出的全部 gate 类型。它把选择窄版 human-gated tree-search 贡献的 idea gate、拒绝公平性指标投机分支的 evaluator gate、在两个 Causality draft 中选择较优分支的 live branch gate、升级到 OpenEvolve 的 program-search gate，以及把未被证实的优越性主张降级为 future work 的 claim gate 串成一条可审计链条。这个轨迹证明了日志格式和证据链可以成立，但还不是一次所有 gate 都在线连续运行的端到端实验。

此外，本文还提供了一个可重新运行的 full-gate trace 脚本。该脚本读取当前已归档的实验摘要，连续重新计算 idea、evaluator、branch、program-search 和 claim 五类 gate 决策，并输出 JSON 与 Markdown artifact。这证明 gate policy 可以在当前证据包上被程序化执行；但它被明确标注为 executable artifact replay，而不是新的在线训练 run。

在 replay artifact 之后，我们又在 `ubuntu-heshi` 上跑了一次新的 online full-gate smoke trajectory。该 orchestrator 生成 idea gate，审批低成本 evaluator bundle，启动新的两 draft FML-bench Causality frontier，选择验证 MAE 更低的分支，从所选 snapshot 继续运行一步 AI Scientist-v2，同时在同一轨迹中跑一次一轮 OpenEvolve knapsack 搜索，并写出 claim-audit gate。branch frontier 选择 step 2（验证 MAE `0.627837`）而不是 step 1（验证 MAE `0.677448`）。随后一 步 continuation 的 test MAE 为 `0.862015`，差于所选 frontier 的 test MAE `0.646224`；同一轨迹中的 knapsack OpenEvolve smoke 达到 best score `1.000000`。这是第一条覆盖五类 gate 的在线编排证据，但它只是 smoke test，且 continuation 是负结果，不能作为 co-pilot 优越性的证据。

随后，我们为这条 online smoke 增加了同 FML step 数的 autonomous baseline。该 baseline 使用同一个 Causality 任务和 DeepSeek 模型，运行三步 AI Scientist-v2，但不进行人类 branch gate。它得到验证 MAE `0.354147` 和 held-out test MAE `0.428516`，明显优于 human-gated smoke continuation 的 test MAE `0.862015`。因此，这个配对 smoke 结果对性能提升主张是负证据，但仍支持更窄的“在线 co-pilot 编排可以执行”这一主张。

随后我们又跑了一条 same-continuous-trajectory paired online full-gate smoke，并直接从这条轨迹日志生成完整的 co-pilot 和 autonomous manuscript artifacts。co-pilot 路径选择验证 MAE 为 `0.621461` 的 Causality 分支，继续后得到 held-out test MAE `0.862015`，同时完成一次 OpenEvolve knapsack smoke，best score 为 `0.994177`。同一次 orchestrator invocation 也启动了一个 autonomous AI Scientist-v2 baseline，使用同一 Causality 任务、模型和 provider，test MAE 为 `0.640451`。生成的 co-pilot manuscript 在内部 rubric 上得到 `4.64`，autonomous manuscript comparator 得到 `3.48`。这比 archived matched-budget comparator 更强，因为两篇 manuscript 来自同一条连续在线 smoke；但它仍不能证明 co-pilot 优越性，因为 autonomous benchmark 明显更好、预算极小，而且没有独立论文质量评审。

## 4. Benchmark 选择与评估计划

我们计划比较六种系统版本：完全自动 baseline、仅创意节点介入、仅分支节点介入、仅评估器节点介入、仅论文主张审计介入，以及完整 co-pilot v3。Benchmark 不应只局限于 FML-bench，而应根据论文主张分层选择。对于 AI Scientist-v2 风格的实验搜索，FML-bench 是近期最合适的载体，因为它已经能在 Ubuntu 环境中跑通，并且能产生分支级日志。对于机器可评分的算法子问题，我们使用 OpenEvolve-controlled tasks，例如函数最小化、0/1 knapsack 启发式搜索和加权 Max-Cut。对于 FML-bench 之外的更广泛证据，本文已加入一个 MLAgentBench vectorization 小实验来测试端到端 ML 实验能力，并进一步记录了 MLAgentBench CIFAR10/debug、MLAgentBench IMDB 与 ScienceAgentBench 的 setup probes。当前证据还没有第二个已打分的官方非 FML benchmark：CIFAR10/debug 被慢速数据下载阻塞，IMDB 在补齐 `datasets` 依赖后仍因 Ubuntu 主机无法访问 HuggingFace 而失败，ScienceAgentBench 的元数据和 verified artifacts 也暂时不可达。更高成本的 stretch benchmark 包括 MLE-bench Lite、PaperBench 和 AIRS-Bench：前者测试 Kaggle 风格 ML engineering，PaperBench 测试从论文到代码复现与层级 rubric 评分，AIRS-Bench 则更接近完整 ML research lifecycle。

指标包括任务分数、论文质量、主张支持率、搜索效率、人类注意力成本和假设多样性。对于程序化搜索模块，关键消融是：在相同 evaluator 和迭代预算下，比较 OpenEvolve 与直接重复 LLM 代码编辑。因此，FML-bench 应被理解为当前证据来源之一，而不是整个项目的完整 benchmark 定义。

因为 IGRE 的核心贡献是科研品味，而不是普通审批，本文在评估包中加入 taste/insight rubric。该 rubric 从 1 到 5 记录 problem depth、novelty potential、mechanistic value、failure informativeness、benchmark taste、claim significance 和 risk asymmetry，并要求写下简短理由。它刻意不被当作 reward model，而是记录导致人类保留、改写或剪枝某个分支的非指标先验。后续评估应同时报告平均任务表现和高尾部信号：例如一个 autonomous policy 本来会剪掉、但人类保留的分支，是否最终带来更强主张、更好 evaluator 或更有信息量的负结果。

我们也对 gate records 加入 taste/insight coverage audit。因为本文的核心主张涉及人类科研品味，而不是普通 human approval，所以仅靠公开 human-AI interaction 数据并不够。我们检查了若干相邻公开数据集：CoAuthor 记录人类与 GPT-3 协作写作，CUPID 记录多轮偏好交互，`neulab/agent-data-collection` 汇总多类 agent trajectories，WebChain 记录 human-annotated web trajectories；但这些数据都没有直接覆盖“人类科学家在 AI Scientist-v2 风格假设—实验—论文循环中介入，并连接到 benchmark、代码 artifact、claim audit 和 manuscript”的场景。因此本文把作者自己的 Codex 使用记录构造成一个脱敏的 single-author longitudinal co-pilot trace corpus，只发布派生元数据层：gate records、artifact paths、commit IDs、benchmark metrics、manuscript revisions 和 claim-audit outcomes，而不公开原始聊天记录或密钥。当前派生快照包含 31 条 gate records、14 条带 attention-cost 字段的记录、9 条带 taste/insight 字段的记录、4 个 prospective matched packages 和 48 个相关 commit。它可以支撑真实使用场景和过程审计主张，但不能单独支撑总体人群层面的有效性结论。我们还加入了 release-readiness audit，检查顶层字段、gate schema、主张边界，并扫描疑似密钥和原始日志字段；当前结果为 pass，0 个 secret-pattern hits，0 个 raw-log marker hits。这说明该数据适合作为派生元数据 case-study artifact 发布，但如果未来扩展到多位研究者，仍需要独立的人类受试者/伦理审查。

根据最新 paper-quality review 的意见，我们把人类注意力成本从口头指标变成了可审计 artifact。human-gate schema 现在包含可选的 `attention_cost` 对象，用于记录 active review minutes、wall-clock latency、reviewed options、reviewed artifacts 和 decision count。我们还对现有 18 个 gate records 做了 coverage audit：其中包括 8 个 standalone human-gate logs，以及 2 个 trajectory artifacts 中的 10 个 embedded gates。结果是：当前 18 个 gate records 都没有完整 attention-cost 记录；其中 5 个重新生成的 executable-trace gates 已经显式标注 timing 缺失，较早的记录则是在该字段加入之前生成的。这是一个重要的负向 measurement-readiness 结果：现有日志可以证明决策来源，但还不能支持“人类注意力效率更高”的主张。后续 prospective matched run 必须填写该字段，才能比较 co-pilot 和 autonomous variants 的人类成本。

为了让这一原则可以执行，我们维护了一份 benchmark-to-claim matrix。
FML-bench Causality 支持 branch-gate 可行性主张，但还不能证明人类 gate
整体优于 autonomous baseline。FML-bench Fairness 支持 evaluator gate 的必要性，因为可执行性修复和退化预测器暴露了单指标投机风险。OpenEvolve 函数最小化、knapsack、Max-Cut、MLAgentBench vectorization 和 sklearn diabetes probe 分别从不同子问题类型检验 program-search escalation policy。ScienceAgentBench、MLE-bench Lite、PaperBench 和 AIRS-Bench 仍是下一阶段扩展目标，而不是当前已打分主张。因此，后续实验应按“最弱且尚未被支持的主张”来选择，而不是按哪个 benchmark 最方便来选择。

### 4.1 初步程序化搜索 smoke test

作为可行性检查，我们已经在 SSH 控制的 Ubuntu 主机上运行了 OpenEvolve 0.2.27，并通过 OpenAI-compatible API 调用 DeepSeek。任务是一个小型函数最小化 evaluator，初始程序为随机搜索。一次 OpenEvolve 迭代后，系统将 evaluator 分数从 0.0345 提高到 0.0378，并保存了一个模拟退火风格的 evolved program。这个结果只是 smoke test：它证明远程 OpenEvolve 路径、evaluator 加载、模型路由、checkpoint 和 artifact 捕获可以跑通，但还不能证明本文核心主张，即 human-gated research 能提升最终论文质量。

我们还在相同 DeepSeek 模型、相同初始程序和相同 evaluator 下运行了 direct one-shot LLM-edit baseline。该直接编辑基线得分为 0.038021，略高于一次迭代 OpenEvolve 的 0.037816，也略高于五次迭代 OpenEvolve 的 0.038007。这个边界结果支持 Co-Pilot AI Scientist v3 的一个核心设计：程序化搜索不应该默认总是启动，而应该由明确的升级 gate 控制。对于极小预算或简单局部改写，直接编辑可能已经足够；当搜索空间更丰富、预算更大时，OpenEvolve 风格的种群搜索才更可能发挥价值。

为了测试后一种情况，我们进一步加入了一个更复杂的 0/1 knapsack 启发式任务。初始 value/weight 贪心程序在 18 个确定性实例上的平均最优比为 0.991519。direct LLM rewrite 将分数提升到 0.995270。五次迭代 OpenEvolve 进一步提升到 0.999439，且没有非法实例。进化出的程序加入了局部改进：移除一个或两个已选物品后，再用贪心方式重新填充容量。这个结果为升级 gate 提供了正例：当子问题具有更丰富的组合结构，并且存在自动 evaluator 时，OpenEvolve-style search 确实可能优于直接编辑。

为了避免只依赖一个手工 knapsack 结果，我们又加入了第二个受控组合优化任务：加权 Max-Cut。初始程序交替分配节点，在 16 个确定性图实例上相对于多起点局部搜索 reference 的归一化得分为 0.734680。一次 direct DeepSeek rewrite 将得分提升到 0.962237。使用相同模型和 evaluator 的五次迭代 OpenEvolve run 达到 0.970833，比 direct rewrite 高 0.008596，且没有非法实例。这个优势很小，而且只有一个 seed，但它给出了第二个算法子问题正例。结合函数最小化任务中的负边界结果，这更支持 selective program-search gate，而不是无条件启动 OpenEvolve。

### 4.2 AI Scientist-v2 分支 gate 回放分析

我们还对已有的两个 AI Scientist-v2/FML-bench smoke run 做了回放分析。在 Causality_causalml 任务中，第一个 draft 就取得了四步运行中的最佳验证 MAE：0.598943，而原始 baseline 为 1.296259；第二个 draft 和后续 refinement 都没有超过它。如果在两个 draft 之后加入 branch gate，人类会保留第一条分支，并避免至少一次低价值后续尝试。在 Fairness_fairlearn 任务中，第一个 draft 反而让公平性指标比 baseline 更差：0.316467 对比 baseline 0.186632；第二次尝试因为 Fairlearn 兼容性问题失败，后续尝试也要么更差、要么出错。此时 human branch gate 应暂停该分支，并把系统路由到 evaluator/兼容性修复或新的公平策略。这个回放证据还不能替代在线 human-gated benchmark，但它说明 AI Scientist-v2 的日志轨迹中已经存在适合人类 co-pilot 介入的可操作检查点。

### 4.3 在线 AI Scientist-v2 分支 gate 小实验

为了从回放证据推进到在线证据，我们在 Ubuntu 主机上新跑了一次 FML-bench 小实验。任务仍为 Causality_causalml。我们把 AI Scientist-v2 设置为两步预算、两个 draft idea、两个模拟并行 worker，并用临时 agent 配置把全部预算放到第一阶段，从而强制产生两个可比较的 draft 分支。第一个 draft 的验证 MAE 为 1.149610，第二个 draft 的验证 MAE 为 0.621262；该任务中 MAE 越低越好。因此，结构化 branch gate 选择第二个 draft，并剪枝第一个 draft。benchmark 自动对最佳验证分支做最终测试，得到 test MAE 0.640451。

这个在线小实验说明，本文提出的 branch gate 可以插入真实 AI Scientist-v2 决策前沿，并基于日志指标和代码快照做出清晰的预算分配决策。它还不能证明 human gating 优于完全自动 AI Scientist-v2：该实验尚未从被选中的分支继续 resume 进行后续 human-gated search，而且其测试分数略弱于之前的四步 autonomous smoke run。因此，我们把它定位为在线人类介入可行性证据，而不是系统级优势的最终证据。

随后，我们实现了一个最小 selected-branch continuation runner。该 runner 会把人类 gate 选中的代码快照临时写回官方 FML-bench 任务模板，从该状态启动一个短预算 AI Scientist-v2 continuation run，并在结束后恢复模板文件。从被选中的第二个 draft 出发，继续两步后验证 MAE 达到 0.401240，test MAE 达到 0.402170。这个结果优于 live two-draft gate run 的 test MAE 0.640451，也优于早期四步 autonomous smoke run 的 test MAE 0.617719。这个比较仍然是初步的：当前 continuation 是通过 snapshot seeding 实现的，还没有保存原始内存中的 tree 对象；同时它只覆盖一个小任务和一个 seed。因此，我们只把它作为“branch gate -> selected snapshot -> additional AI Scientist-v2 budget”这条路径可以执行的证据，而不是最终统计结论。

根据 paper-quality review 的意见，我们又补了更接近同预算的 autonomous baseline。第一组 matched run 使用同一个 Causality_causalml 任务、同一个 DeepSeek 模型、两个初始 idea、两个并行分支和四个 AI Scientist-v2 总步数，但不进行人类分支选择。它得到验证 MAE 0.389451、test MAE 0.421474。在这一组中，human-gated 路径在 held-out test MAE 上略好：0.402170 对比 0.421474；但 autonomous baseline 在验证 MAE 上略好。

随后我们又跑了第二组 matched Causality replicate。human-gated 两 draft frontier 选择了验证 MAE 0.605881、test MAE 0.646224 的分支；snapshot-seeded continuation 没有进一步改善 held-out test，最终验证 MAE 为 0.627837、test MAE 为 0.646224。对应的四步 autonomous baseline 得到验证 MAE 0.537972、test MAE 0.595685。在第二组中，autonomous 路径在验证集和 held-out test 上都更好。

因此，两组同预算对照的结论是 mixed evidence：一组 held-out test 支持 human-gated continuation，另一组支持 autonomous baseline。两组平均后，human-gated test MAE 为 0.524197，autonomous test MAE 为 0.508579；由于该指标越低越好，均值反而略支持 autonomous baseline。这个结果消除了一个重要的计算预算混淆因素，但不支持“人类 gate 普遍优越”的宽泛结论；它只支持 branch gate 可以插入、selected snapshot 可以继续搜索这一可行性主张。

我们现在还用脚本生成这组 FML matched-comparison aggregate，而不只依赖手写表格。生成的 audit 显示：两组正式 pair 中，human-gated 胜 1 次，autonomous/tie 胜 1 次；autonomous-minus-human 的平均 delta 为 -0.015618，delta SEM 为 0.034921，并显式标注 statistical claim 为 `not_supported_n_too_small`。单独的 online-smoke comparison 对 co-pilot performance 也是负结果：test MAE 为 0.862015 对 0.428516。因此，这份脚本化 summary 是当前 FML performance evidence 的权威汇总。

在第二个 Causality prospective package 之后，我们又把同一个 package runner 扩展到
`ubuntu-heshi` 上另一个实际可用的 FML-bench workspace：`Fairness_fairlearn`。这个结果
同样不是 co-pilot 的正结果，但失败方式不同：co-pilot branch frontier 的两个候选都没有通过
validation，因此记录的 frontier gate 选择 `abort_no_valid_branch`，而不是强行继续一个无效分支。
匹配的 autonomous run 成功完成，test primary metric 为 0.172152
（`abs_demographic_parity_diff_mean`，越低越好）。当前 prospective package audit 因此覆盖 4 个
通过格式审计的 package：1 个受控 micro-task 正结果、2 个 Causality FML 负结果，以及 1 个
Fairness FML 无有效 continuation 的失败案例；四个 package 都包含完整的 attention-cost 和
taste/insight gate record。这扩展了 benchmark 形态，但让平均性能叙事更保守，而不是更强。

### 4.4 非 FML benchmark 与程序搜索小实验

根据上面的 benchmark 选择原则，我们还把 MLAgentBench 作为非 FML 评估来源。我们在 Ubuntu 主机上克隆 MLAgentBench，并先运行其轻量 `vectorization` 任务，使用内置 `Agent` baseline。该 baseline 只执行 starter `train.py` 并提交结果。官方 baseline 成功完成，final score 为 3.172504 秒，total benchmark time 为 3.365531 秒，且没有错误标记。

随后，我们把同一个任务封装成更严格的本地 evaluator：在接受运行时间之前，evaluator 会用一个小型确定性输入，把候选 `Conv2DLayer.forward` 的输出和 nested-loop reference 做数值比对。在这个受控 evaluator 下，starter program 的 median runtime 为 3.261186 秒。一次 direct DeepSeek `deepseek-chat` rewrite 生成了看似合理的向量化代码，但因为数值不一致没有通过 correctness gate。相反，使用同一 DeepSeek 模型的三轮 OpenEvolve-style run 在第 1 轮找到了正确候选，median runtime 为 0.051882 秒，相比受控 starter program 约快 62.86 倍。这个结果支持一个较窄但重要的结论：program-search-escalation 节点可以在 FML-bench 之外的机器可评分子问题上发挥作用。但它还不能证明完整 co-pilot 架构能提升整篇论文质量。

为了检查稳健性，我们又用更多 random seed 重复同样的三轮 OpenEvolve 设置。在 seed 0、1、2、3、4、7、42、123 共八次运行中，所有运行都保留了正确 best program，并且都比受控 starter 更快。八个 seed 的 best runtime 中位数为 0.024581 秒，相当于相对 starter 约 132.67 倍的中位加速；其中 6 个 seed 找到低于 0.1 秒的程序。这个结果明显强于最初的三 seed probe，但仍不是确定性成功：seed 7 只有约 1.09 倍加速，seed 1 约 15.57 倍加速。因此，该结果增强了“程序搜索模块可以找到有效代码变换”的证据，同时保留了极小预算下 seed/budget sensitivity 的重要 caveat。

为了避免非 FML 证据只覆盖底层 runtime optimization，我们又加入了一个使用 sklearn 内置 diabetes regression dataset 的受控 tabular modeling probe。这个 probe 不需要 Kaggle 凭证，也不应被报告为官方 MLAgentBench 分数。初始程序是刻意粗糙的均值预测器，在五个确定性 split 上 mean RMSE 为 78.572189。一次 direct DeepSeek rewrite 找回了标准 Ridge 风格 baseline，mean RMSE 为 55.895460。三个三轮 OpenEvolve seed 也都明显优于均值预测器，best RMSE 分别为 55.895460、55.946535 和 55.895460；其中位 RMSE 为 55.895460，基本与 direct rewrite 持平。这个结果把 benchmark 覆盖扩展到了表格建模子问题，同时也给出了重要边界条件：当改进只是一个标准的小型建模修改时，direct editing 可以和 program search 一样有效。因此 program-search gate 应该选择性触发，而不是自动触发。

我们还尝试了三个 benchmark 扩展 probe。首先，我们尝试加入第二个官方 MLAgentBench `debug` 任务，它映射到 CIFAR10。该 setup probe 先修复了远端环境缺少 `torchvision` 的问题，并安装了与本地 `torch` 匹配的 CPU wheel；但运行在数据准备阶段停止，因为 170 MB 的 CIFAR10 压缩包下载速度过慢，不适合当前交互预算。其次，我们检查了 ScienceAgentBench。该仓库已经存在于 Ubuntu 主机，README 指向 2026 年 4 月 verified split 和 `benchmark_verified.zip`，但本地 benchmark 目录缺少 verified artifacts，而且 HuggingFace metadata 请求返回 `[Errno 101] Network is unreachable`。第三，我们尝试官方 MLAgentBench `imdb` 任务：补齐其官方 `eval.py` 需要的 `datasets` 依赖后，即使只加载 5 条测试样本也因为同样的 HuggingFace 网络错误失败。因此，本文只把这些记录为 setup artifacts，而不报告 benchmark 分数；下一步需要预缓存数据或换一条可访问的数据路径，而不是因为方便就退回只用 FML-bench。

### 4.5 主张审计

在完成这些 pilot 实验后，我们做了一次 claim-evidence audit。通过 Monica 路由的 `gpt-4o-mini` 审稿式检查认为：本文的架构贡献是合理的，但当前实验证据还不足以支持“人类 gate 提高论文质量”或“完整 co-pilot 系统优于 autonomous AI Scientist-v2”这类宽泛结论。因此，本文把这些表述保留为 evaluation protocol 要检验的假设，而不是已经证明的结论。当前 audit 只支持较窄的实证主张：OpenEvolve-style search 可以在部分机器可评分子问题上有效，但在极小预算下存在 seed sensitivity；direct editing 在简单 tabular modeling probe 上可以匹配 OpenEvolve；branch gate 可以插入 AI Scientist-v2 风格日志轨迹；evaluator gate 必须在 continuation 前拒绝无法执行以及指标投机的分支；两组 matched Causality 对照给出的是混合证据，而不是稳定的人类 gate 优势。第一次把 online branch gate 扩展到 `Fairness_fairlearn` 时，两条候选都在 validation 阶段失败，因此本文只把它作为 failure-mode evidence 归档，而不计入 matched-budget performance evidence。后续 evaluator-gate repair probe 进一步暴露了这个问题：一个修复 API 后可运行的公平性候选在 demographic parity difference 上反而更差，test 指标为 0.317603，而 baseline 为 0.173030；一个退化的全负类预测器虽然把目标公平性指标做到 0.000000，却把 balanced accuracy 降到 0.500000。因此，在公平性任务中，gate 不能只看单一 fairness metric，还必须同时检查代码可执行性和最低效用下限。

在加入 prospective matched-budget 指标汇总后，我们又通过 Monica 路由刷新了两次 paper-quality review。`gpt-4o-mini` 给出 weak-accept 建议，认为新颖性和可复现性较强，但严谨性和证据仍只有中等水平。`claude-3-7-sonnet-latest` 更严格，认为如果目标是强 ML/NLP systems venue，当前版本应被拒，因为核心 human-gating 和 paper-quality 主张仍未被证明，最强的 FML-bench prospective package 对 co-pilot performance 是负结果，而且系统仍缺少 same-continuous-trajectory 的 paper-generating 对照。两个模型的共同结论是：下一版必须在更多任务和随机种子上比较 autonomous AI Scientist-v2 与 human-gated variants，记录人类注意力成本，并更清楚地区分已经完成的系统证据和 future work。

## 5. 当前贡献与尚未证明的主张

本文当前贡献包括：

1. 一个面向协作式自动科研的模块化架构。
2. 一个用于科研 agent 的人类参与节点形式化 schema。
3. 一条 retrospective full-gate trajectory，展示 idea、evaluator、branch、program-search 和 claim-audit gate 都可以用同一 schema 记录。
4. 一个可重新运行的 full-gate trace 脚本，可以从已归档实验摘要中重新计算 gate chain，并明确把输出标记为 artifact replay。
5. 第一条 online full-gate smoke trajectory，在一次远端运行中覆盖 idea、evaluator、branch、program-search 和 claim gate，同时记录了负向 continuation 结果。
6. 一个同时评估平均 benchmark 表现和人类参与下高尾部科研上限的实验协议。
7. 远程 OpenEvolve 与 FML-bench 小实验，证明可验证微演化和前沿转向两个 IGRE 算子可以在 Ubuntu 主机上运行。
8. 两组同预算 FML-bench Causality 对照：human-gated branch continuation 与四步 autonomous AI Scientist-v2 baseline，结果呈混合状态。
9. 第一条 online full-gate smoke 的同 FML step autonomous baseline，显示 human-gated continuation 在该 smoke 对照中表现更差。
10. 两个非 FML 程序搜索小实验，分别覆盖 runtime optimization 和 tabular regression，用于扩展 FML-bench 之外的 benchmark 覆盖面。
11. 一个可在 Codex 中复用的 workflow skill。
12. 中英文论文、使用文档和主张审计 artifact，便于复现和传播。
13. Monica 路由的 paper-quality review artifact，用于记录下一轮修改前的外部模型批评。
14. human-gate attention-cost audit，显示当前 gate log 还没有记录 active review time 和 latency；未来 prospective run 必须补齐这些字段后，才能提出 attention-efficiency claim。
15. taste/insight coverage audit，显示当前已有 1 条完整 scientific-taste prior 记录，另有 17 条较早 gate 仍缺少 taste/insight 字段。
16. prospective matched-budget package validator，用来定义在声称论文质量提升、人类注意力效率提升或优于 autonomous AI Scientist-v2 之前，最低限度需要具备的非 synthetic 证据形状。
17. 一个 controlled prospective Max-Cut micro-pilot package，已经通过该 validator，并包含完整 attention/taste logging、matched baseline metrics、claim audit 和同次运行生成的 manuscript artifact。
18. 一个 prospective FML-bench Causality package，包含完整 attention/taste logging 和 matched autonomous baseline；在这个两步小预算设置中，co-pilot test MAE 为 0.646224，autonomous baseline 为 0.624703，因此是负向 co-pilot performance 结果。
19. 一个 prospective package 指标汇总表，把通过 audit 的 package 按任务、指标方向、co-pilot 分数、autonomous 分数和 claim implication 汇总；当前结果是 1 个 controlled micro-task 正向结果、2 个 Causality FML-bench 负向结果，以及 1 个 Fairness_fairlearn 无有效 continuation 的失败案例。
20. 一个 matched mini-manuscript quality probe：为同一个 FML package 生成 autonomous mini-manuscript，并让 Monica 路由的 `gpt-4o-mini` 和 `claude-3-7-sonnet-latest` 对匿名 A/B manuscript 评分；两个模型都偏好 co-pilot package mini-manuscript，overall 为 4 对 3。
21. 一个 matched full-manuscript generation probe：把同一个已归档 FML evidence package 渲染成两篇完整论文形态的 manuscript，并用确定性内部 rubric 评分；最新 Fairness package 中，co-pilot manuscript 因结构完整、证据绑定、主张校准和方法区分度得到 4.18 overall，autonomous manuscript 得到 4.11 overall，但 autonomous 是唯一拥有有效 FML 标量测试指标的路径。
22. 一个 same-continuous-trajectory paired online full-gate manuscript-production smoke，从同一次在线 orchestrator run 生成完整 co-pilot manuscript 和 autonomous comparator；co-pilot 内部评分为 4.64、autonomous comparator 为 3.48，但 autonomous benchmark metric 更好（test MAE 0.640451 对 0.862015）。
23. 一个 Human Co-Pilot Trace Dataset protocol，把本文实际 Codex 使用记录转化为脱敏派生数据集，而不是依赖不匹配的通用 human-AI interaction 数据集。

当前证据还不能证明人类 gate 能提升论文质量，也不能证明完整 co-pilot 系统优于 autonomous AI Scientist-v2。这些仍是下一阶段 benchmark 要验证的目标主张。

## 6. 局限性

本文不预设人类参与一定有效。人类 gate 可能引入偏见、降低搜索速度、压缩探索多样性；在短预算 benchmark 中，它甚至可能不如完全自动搜索策略。这不是附带 caveat，而是本文方法需要正面评估的一部分。IGRE 把人类科学家视为高方差搜索算子，其价值可能不体现在平均分上，而体现在高尾部：更好的问题品味、更能揭示机制的 evaluator、更尖锐的失败解释，或者愿意追踪一个更冒险但更原创的方向。程序化搜索也可能只优化局部指标，却不能提高论文层面的科学贡献；在极小预算下，它也未必优于直接 LLM 编辑。专家论文评分成本较高，而且不同评审可能存在分歧。因此，第一版实验应保持窄主张，并在 gate 无法改善结果时如实报告负结果。当前 selected-branch continuation 证据在两组 matched pair 中呈混合状态，还不是统计受控 benchmark；retrospective full-gate trajectory 和 executable artifact replay 证明了 schema、决策链和可复现 traversal logic。online smoke trajectory 已经在一次远端运行中覆盖五类 gate，但预算极小、混合了 FML branch task 和 knapsack program-search 子问题，并且 continuation test score 变差；同 FML step autonomous baseline 也优于 human-gated continuation。更强主张需要更多任务、更多随机种子、更丰富的预算分配设置、更大规模在线轨迹、独立论文质量评审，以及能捕捉少数高质量科研结果的指标，而不只是平均任务分数。

当前 human-gate logs 也缺少可度量的人类注意力成本。我们可以统计决策 artifact，但还不能计算 active review minutes 或 wall-clock latency，因此不能声称 gate 提高了单位人类努力产出的科研质量。下一轮 matched-budget 实验必须前瞻性记录 attention cost。

新的 prospective matched-budget package audit 现在已经在一个 controlled micro-pilot、两个 FML-bench Causality pilot 和一个 FML-bench Fairness pilot 上通过。这个进展说明最小证据形状可以被真实远端计算生成和审计，而且已经延伸到 AI Scientist-v2 风格 benchmark；但 FML packages 在当前小预算设置中都是 co-pilot 平均性能的负结果或无有效 continuation 的失败案例，且这些 package 仍没有独立评价完整论文质量。因此当前论文仍应被限制在 pilot-system evidence，直到更多任务、更多 seed、更大预算和独立论文质量评审完成。

我们还新增了 package 指标汇总，而不只报告 artifact audit 是否通过。当前四个 passing package 中，controlled Max-Cut micro-task 的 human-selected branch 在 mean normalized score 上胜出（0.984419 对 0.596214），但这只是微任务；两个 FML-bench Causality package 都由 autonomous baseline 在 test MAE 上胜出，分别为 0.624703 对 0.646224，以及 0.296399 对 0.646224；Fairness_fairlearn package 中 co-pilot frontier 没有有效测试分数，而 autonomous baseline 的 primary metric 为 0.172152。四个 human gate 都已经记录完整 attention-cost 和 taste/insight。这个结果正是 IGRE 需要坚持的证据纪律：人类科研品味是高方差搜索干预，不能预设它提高短预算平均分；它更可能需要通过高尾部科研质量、问题选择和主张校准来体现。

我们还补了第一个 matched mini-manuscript quality probe。该 probe 从同一个 FML package 的 autonomous baseline 生成一篇 autonomous mini-manuscript，把 co-pilot package manuscript 匿名为 A，把 autonomous manuscript 匿名为 B，并让 Monica 路由的 `gpt-4o-mini` 和 `claude-3-7-sonnet-latest` 按 claim calibration、evidence use、methodological completeness、limitation honesty、clarity 和 overall quality 评分。两个模型都偏好 A，overall 为 4 对 3；理由是 co-pilot mini-manuscript 虽然 benchmark 分数更差，但对主张边界和局限性写得更清楚。这个结果只能说明 manuscript-quality measurement pipeline 可运行，不能证明完整 co-pilot 系统已经能写出更好论文。

这次新增的 full-manuscript probe 只缩小了一个具体缺口，并没有关闭顶会证据缺口。它说明已归档 FML package 中的结构化证据足以生成两篇完整、主张校准的论文形态 manuscript；最新 Fairness probe 中 co-pilot manuscript 的内部 rubric 为 4.18，autonomous manuscript 为 4.11，但 autonomous 是唯一拥有有效 FML 标量测试指标的路径。更新的 online trajectory manuscript smoke 进一步说明 fresh online co-pilot trajectory 可以生成完整论文形态 artifact，并且已经有 same-continuous-trajectory autonomous comparator；co-pilot manuscript 得到 4.64，autonomous comparator 得到 3.48，但 autonomous 的 benchmark 指标更好（0.640451 对 0.862015 test MAE），而且没有独立专家论文质量评审。因此 co-pilot 的当前主张必须停留在方法区分度、科学品味记录和高尾部科研搜索空间塑形，而不能说它已经在短预算平均 benchmark 上优于 autonomous AI Scientist-v2。

taste/insight 证据目前也只是 logging-readiness 阶段。归档中已有 1 条完整 scientific-taste prior 记录，来自作者要求扩展 benchmark 并突出高尾部科研品味的指令；但它还不能证明该决策改善了下游科研结果。下一轮实验必须前瞻性记录 taste rationale，才能检验人类 insight 是否真的改变了科研搜索分布。

当前实现现在已有 smoke 级别的 same-continuous-trajectory 在线论文生成对照，但规模仍不足以支撑 systems paper 的强主张。下一版 systems paper 至少需要报告多组更大规模的 matched 在线轨迹，覆盖更多任务和随机种子，从假设生成一直到最终 claim-audited manuscripts。

## 7. 结论

Co-Pilot AI Scientist v3 将自动科学发现重新定义为洞察门控科研演化。该系统保留自动 agent 的大规模搜索能力，同时给人类科学家提供明确、可记录、可实验检验的影响节点。它最重要的主张不是“人类总能提高平均 benchmark 表现”，而是人类科研品味和 insight 可以改变搜索分布，使系统更有机会产生少数但更原创、更可能开创新方向的成果。如果未来 matched benchmark 支持这一高尾部假设，co-pilot 科研系统可能通过改变“系统尝试什么样的科学”来写出更好的论文，而不是简单把人类排除在科学之外。当前论文应被理解为一个带 pilot evidence 的可复现系统 proposal，而不是最终优越性证明。
