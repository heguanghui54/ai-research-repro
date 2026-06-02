# Co-Pilot AI Scientist v3 投稿卡片

## 身份信息

- 题目：Co-Pilot AI Scientist v3: Insight-Gated Research Evolution for Collaborative Automated Science
- 作者记录：He Shi，National University of Singapore, School of Computing，本科生
- 当前状态：可复现交付包已经完成；顶会级实证充分性尚未完成
- 人类评估状态：盲评专家评审包和协议已经准备好；尚未收集独立人类评分
- 核心方法：Insight-Gated Research Evolution（IGRE，洞察门控科研演化）
- 长期扩展：Long-Horizon Taste Gate（LHTG，长期科研品味门控）与 Delayed-Value Review Signal（DVRS，延迟价值评议信号）

## 一句话贡献

Co-Pilot AI Scientist v3 把人类参与自动科研的方式变成可记录、可审计、可复用的门控流程，用人类科研品味和 insight 引导 AI Scientist-v2 式生成、AI Co-Scientist 式讨论，以及 OpenEvolve 式可验证搜索，从而形成更会校准主张的科研轨迹。

## 本文自己的方法在哪里

这篇论文不应写成把几篇自动科研论文拼在一起。IGRE 是本文为“人类如何参与自动科研”重新命名并调整过的参与范式：人类科学家不是简单批准、润色或打分，而是在六个明确门控点改变搜索轨迹。

1. 科研品味先验门控：在短期指标不确定时，判断哪些方向值得消耗稀缺算力。
2. 评估器压力测试门控：先检查 benchmark 或 reward 是否容易被投机利用。
3. 前沿转向门控：把搜索从局部短期结果转向未来前沿、冷门但高潜力的问题。
4. 可验证微演化门控：只在机器可评分的子问题上使用 OpenEvolve 式搜索。
5. 结构化反馈门控：把清晰度、可复现性、定义缺失和组织结构意见转化为具体修订计划。
6. 主张校准门控：防止论文声称超过证据支持的结论。

LHTG/DVRS 是这个思想的长期版本：有些人类评议短期看可能不能提高原论文分数，甚至会降低局部结果，但如果它把过去的研究轨迹引向后来真正成为主流或 SOTA 的方向，就说明它具有延迟价值。

下一步人类评估是一个低风险盲评专家实验：招募 3-5 名 NUS 或学校关联的 ML/AI 教授、博士后、博士生或高级研究学生，在机构伦理审查或豁免判定之后，对匿名 A/B 再生成 mini-paper PDF 评分。评分维度包括新颖性、方法可靠性、实验具体性、可复现性、主张校准、未来前沿潜力和总体偏好。

## 现有证据快照

- 评议效用图谱：筛选 473 条 OpenReview 评议片段，其中 398 条具有可行动门控信号。
- 门控结构消融：完整门控 1.000，最佳单门控 0.369，随机 0.199。
- 留出验证：完整门控 1.000，最佳单门控 0.374。
- 门控结果归因：完整门控 75.17，最佳单门控 37.25。
- OpenReview 重新生成：一个模型评分器下评议引导版本 5/6 获胜；跨模型复评为 3/6 获胜、基线 1/6 获胜、2 个平局。
- 等上下文消融：真实论文相关评议 8 胜，非相关评议 1 胜，3 个平局。
- 深度再生成案例 PDF：3 篇选中 OpenReview 论文已经生成可查看的原始评议引导和六门控混合评议引导 mini-paper PDF。
- 候选前沿验证：16 个延迟价值候选中 13 个完成评分，delayed-control 平均差为 +0.064。
- 边界证据：当前小样本中 LHTG/DVRS 的正向延迟价值案例为 0；FML 短预算证据仍然混合或偏负。

## 现在不能声称什么

- 不能声称 Co-Pilot AI Scientist v3 已经实证超过全自动 AI Scientist-v2。
- 不能声称人类参与总是提高论文质量。
- 不能把 OpenReview 历史评议当作真实在线 co-pilot 交互数据。
- 不能声称 DVRS 已经找到正向高尾部延迟价值案例。

当前最稳妥的主张是：人类科研品味和 insight 可以被操作化为可审计的参与模式；历史评议数据可以用于设计和压力测试这些模式；本交付包已经明确指出下一步还缺哪些实证证据。

## 外部复现入口

在仓库根目录运行：

```bash
python3 -m pip install -r requirements.txt
python3 scripts/audit_long_horizon_taste_gate.py
python3 scripts/audit_temporal_frontier_replay.py
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 scripts/build_deep_regeneration_cases.py
python3 scripts/build_six_gate_hybrid_review_cases.py
python3 scripts/build_deep_case_pdfs.py
python3 scripts/audit_deep_regeneration_cases.py
python3 scripts/audit_objective_delivery.py
python3 scripts/audit_package_consistency.py
```

## 审稿人阅读顺序

1. `docs/co_pilot_ai_scientist_v3/paper_en_focused.md`
2. `docs/co_pilot_ai_scientist_v3/audits/top_conference_readiness_audit.md`
3. `docs/co_pilot_ai_scientist_v3/audits/claim_evidence_audit.md`
4. `docs/co_pilot_ai_scientist_v3/audits/lhtg_dvrs_audit.md`
5. `skills/co-pilot-ai-scientist-v3/SKILL.md`
6. `docs/co_pilot_ai_scientist_v3/human_expert_blind_review_protocol.md`
