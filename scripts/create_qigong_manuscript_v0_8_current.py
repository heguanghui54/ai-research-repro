#!/usr/bin/env python3
"""Create manuscript draft v0.8 from the current evidence boundary."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "qigong_platform_paper"
SRC = DOC_DIR / "manuscript_draft_v0_7_current_evidence.md"
OUT = DOC_DIR / "manuscript_draft_v0_8_current_evidence.md"


NEW_ABSTRACT = """## 摘要

目的：在健康中国、全民健身与中华优秀传统文化创造性转化背景下，健身气功正在由在场式传授进入以短视频平台为核心的可视化、算法化和标签化传播环境。既有研究多关注传统体育文化传播效果、传播策略或短视频影响因素，对平台如何重塑健身气功的意义生成条件与身体经验结构关注不足。本文以德里达“延异”理论为核心参照，引入身体文本和媒介时间性视角，提出“平台化身体”概念，用以解释健身气功在短视频平台中的身体可见性重排、意义延宕和经验痕迹化过程。方法：研究采用“真实平台样本-学生网页人工编码-LLM 辅助语义编码-匿名评论语境-典型视频身体证据”的分层方案，并以审计文件限定每一层证据的解释边界。当前工作包形成 628 条公开可见短视频筛选元数据，其中 185 条进入真实平台样本池；抽取 120 条正式编码样本；建立 Vercel + Supabase 网页人工编码系统，分配给 STU01-STU10 进行多名学生编码；使用 deepseek-chat 形成 120 条辅助语义编码记录；整理 263 条匿名评论，覆盖 59 个正式样本视频；设计 5 个典型视频案例。结果：当前版本报告证据链建设、理论模型和机制解释，不报告尚未完成人工编码、双编码一致性和授权视频分析的正式经验结果。评论层隐私与匿名化审计通过，但评论总量、覆盖率和单视频评论数尚未达到频率分析门槛。结论：短视频平台既扩大健身气功可见性，也通过可视性中心、媒介时间压缩、功效标签和平台踪迹改变其身体经验生成方式。本文提出“传播延异-影像痕迹”框架和“平台化身体”概念，为后续形成可投稿的体育新闻传播与民族传统体育交叉研究奠定基础。
"""


NEW_HUMAN_CODING = """### 4.3 学生网页人工编码与 LLM 辅助

正式编码表当前包含 120 行。为把人工编码从单机表格推进到可复核、可分工、可导出的数据采集流程，研究已建立 Vercel + Supabase 网页编码系统。网页端把 120 条正式样本分配给 STU01-STU10 十名学生编码员，并设置少量双编码复核任务；学生登录后可看到视频链接、中文填报说明、编码字段和提交状态。该平台本身不是论文结论，而是本研究人工编码数据采集方法的一部分：它把编码员身份、任务分配、填写完整性和后续导出流程纳入审计链条。

截至当前审计，网页提交汇总为：预期主编码任务 120 条，完整提交 0 条，主编码提交 0 条，双编码提交 0 条。因此，本文当前版本不能报告人工编码分布，也不能报告编码一致性。只有当 120 条主编码完整提交、导出并转写为正式编码表，且不少于 20% 的双编码子样本完成一致性检验后，才能报告主导意义框架、影像痕迹强度、媒介时间性、戏仿密度和具身消解程度等变量分布。

LLM 辅助语义编码当前记录 120 条，具体模型名为 deepseek-chat。其用途是生成复核线索和低置信度队列，而不是替代学生人工编码。正式结果必须等待人工编码和双编码一致性分析完成后才能报告。公共稿件只写具体模型名和方法边界，不写模型聚合平台、私有接口或 AI 工作流为作者。
"""


NEW_COMMENT_SECTION = """### 4.4 评论语境层

当前正式评论文件包含 263 条匿名文本，覆盖 59 个正式样本视频。评论审计计数为 pass=6、warn=0、fail=3。隐私字段、匿名化状态、文本标识符扫描和评论 ID 唯一性通过审计；评论总量、正式编码样本覆盖率和单视频评论数未通过正式频率分析门槛。为推进后续补采，研究已生成评论补采目标表：按每个样本视频至少 5 条匿名公开评论估算，仍需补采 447 条；其中 59 个视频属于已有评论但不足 5 条的 `P1_top_up_to_five`，61 个视频属于无评论或需标注不可采原因的 `P2_mark_unavailable_or_find_alternative`。

因此，评论材料当前只能作为网络民族志式语境近读证据。评论中的玩梗、收藏、求证、跟练和商业怀疑等表达，可辅助解释平台语境中的意义延异，但不能写成总体流行程度、平台差异或用户心理比例。只有评论补采和评论审计通过后，评论层才可进入频率描述或组间比较。
"""


NEW_VIDEO_SECTION = """### 4.5 典型视频身体证据层

典型视频 manifest 当前包含 5 个案例，本地可分析视频为 0 个，权利确认为 1 个。当前视频文件预检显示 `ready_local_rights=0/5`，低于至少 3 个可分析本地视频的门槛。工具环境方面，本地 macOS 仅确认 OpenCV 后备链路可用，SportsLabKit 和 MediaPipe 尚未在当前环境跑通；Ubuntu 实验机仍需安装/验证 SportsLabKit，并在 TC0001-TC0003 等本地视频上传后重跑预检和特征提取。

该层的设计不是为了把论文变成计算机视觉论文，而是为了让体育学审稿人看到“身体”没有被纯符号分析吞没。若后续获得权利确认视频，可以比较官方标准示范与平台改编样本在身体可见性、动作连续性、运动能量、节奏变化和镜头切分上的差异，并把这些差异放回调身、调息、调心的传统身体逻辑中解释。在当前证据状态下，论文不能报告姿态轨迹、身体中心、节奏变化、动作偏移或 SportsLabKit 实测结论。
"""


NEW_REF_SECTION = """## 参考文献核验清单

以下文献分为目标刊对话文献与外部理论/技术/平台传播文献。目标刊文献来自已解析的《武汉体育学院学报》题录矩阵，外部文献来自当前核验包；投稿前仍需逐条核验作者、题名、期卷页码、DOI、出版社和中文译名。

### 一、目标刊对话文献

1. 左逸帆;刘双双;罗亮. 体育非遗短视频传播的关键影响因素与逻辑研究[J]. 武汉体育学院学报, 2025, 59(08):24-30.
2. 李乾丙;王相飞;周榕. 中国民族传统体育文化国际传播效果提升的影响因素与组态路径——基于YouTube热门视频的实证分析[J]. 武汉体育学院学报, 2024, 58(05):35-42.
3. 程宇;王相飞;王真真;李乾丙. 如何提升体育健康科普效能?——基于对体育健康辟谣短视频传播的组态分析[J]. 武汉体育学院学报, 2025, 59(11):38-45+54.
4. 马天辕;郭玉成. 技术与思想：导引史料认知的历史逻辑寻绎[J]. 武汉体育学院学报, 2023, 57(07):62-68.
5. 尹海立;颜芬;颜辉;王艳红;段倩倩. 新时代中国传统体育养生文化创新性发展路径研究[J]. 武汉体育学院学报, 2024, 58(06):65-72.
6. 于晓梅;张业安. 体育媒介传播的转向与未来：从符号传播回归具身传播[J]. 武汉体育学院学报, 2023, 57(08):13-18+32.
7. 江松;侯小琴. 传统武术图腾隐喻与身体实践[J]. 武汉体育学院学报, 2025, 59(06):65-72.
8. 崔琪;王坤. 体育非物质文化遗产智能化保护与传播的数字技术赋权策略研究[J]. 武汉体育学院学报, 2024, 58(09):59-65+96.
9. 徐正旭. 人机对齐与价值对齐：奥林匹克运动中人工智能风险及中国治理方案[J]. 武汉体育学院学报, 2026, 60(01):43-51.
10. 刘宏宇;陈诺;孙贵龙. 从“离身”到“具身”:中小学体育教学的实践转向[J]. 武汉体育学院学报, 2026, 60(01):86-93.
11. 白晋湘. 机遇、挑战、跨越：强国建设背景下民族传统体育传承发展研究[J]. 武汉体育学院学报, 2026, 60(01):1-8.
12. 陈积银;王琪琪. 城市群众性体育赛事传播模式的变革与启示——基于“苏超”传播的田野调查[J]. 武汉体育学院学报, 2025, 59(12):1-9+27.

### 二、外部理论、技术与平台传播文献

13. Derrida, J. (1976). Of Grammatology. Translated by Gayatri Chakravorty Spivak. Baltimore: Johns Hopkins University Press.
14. Derrida, J. (1982). Margins of Philosophy. Translated by Alan Bass. Chicago: University of Chicago Press.
15. Li, Y., Chen, L., He, R., Wang, Z., Wu, G., & Wang, L. (2021). MultiSports: A Multi-Person Video Dataset of Spatio-Temporally Localized Sports Actions. ICCV 2021.
16. Deliège, A., Cioppa, A., Giancola, S., Seikavandi, M. J., Dueholm, J. V., Nasrollahi, K., Ghanem, B., Moeslund, T. B., & Van Droogenbroeck, M. (2021). SoccerNet-v2: A Dataset and Benchmarks for Holistic Understanding of Broadcast Soccer Videos. CVPR Workshops 2021.
17. Bian, J., Li, X., Wang, T., Wang, Q., Huang, J., Liu, C., Zhao, J., Lu, F., Dou, D., & Xiong, H. (2024). P2ANet: A Large-Scale Benchmark for Dense Action Detection from Table Tennis Match Broadcasting Videos. ACM Transactions on Multimedia Computing, Communications, and Applications, 20(4), Article 118.
18. SportsLabKit. Python package for sports analytics, PyPI project sportslabkit, version 0.3.1.
19. Bradski, G. (2000). The OpenCV Library. Dr. Dobb's Journal of Software Tools, 25, 120-125.
20. Grishchenko, I., Bazarevsky, V., Zanfir, A., Bazavan, E. G., Zanfir, M., Yee, R., Raveendran, K., Zhdanovich, M., Grundmann, M., & Sminchisescu, C. (2022). BlazePose GHUM Holistic: Real-time 3D Human Landmarks and Pose Estimation. arXiv:2206.11678.
21. Liu, Y., & Wang, X. (2022). Communication Mechanism and Optimization Strategies of Short Fitness-Based Videos on TikTok During COVID-19 Epidemic Period in China. Frontiers in Communication, 7, 778782.
22. Tian, Y., Liu, S., & Zhang, D. (2023). Clearness qualitative comparative analysis of the spread of TikTok health science knowledge popularization accounts. Digital Health, 9.
23. Basch, C. H., Meleo-Erwin, Z., Fera, J., Jaime, C., & Basch, C. E. (2023). Using TikTok to Educate, Influence, or Inspire? A Content Analysis of Health-Related EduTok Videos. Journal of Health Communication, 28(8).
24. Yin, H., Huang, X., & Zhou, G. (2024). An Empirical Investigation into the Impact of Social Media Fitness Videos on Users' Exercise Intentions. Behavioral Sciences, 14(3), 157.
25. Xu, X. (2024). Being there and being with them: the effects of visibility affordance of online short fitness video on users' intention to cloud fitness. Frontiers in Psychology, 15, 1267502.
"""


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    start_idx = text.index(start)
    end_idx = text.index(end, start_idx)
    return text[:start_idx] + replacement.rstrip() + "\n\n" + text[end_idx:]


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    text = replace_between(text, "## 摘要", "关键词：", NEW_ABSTRACT)
    text = text.replace(
        "关键词：健身气功；平台化身体；延异；影像化规训；身体文本；短视频传播；体育新闻传播",
        "关键词：健身气功；平台化身体；延异；影像化规训；网页人工编码；身体文本；短视频传播；体育新闻传播",
    )
    text = replace_between(text, "### 4.3 人工编码与 LLM 辅助", "### 4.4 评论语境层", NEW_HUMAN_CODING)
    text = replace_between(text, "### 4.4 评论语境层", "### 4.5 典型视频身体证据层", NEW_COMMENT_SECTION)
    text = replace_between(text, "### 4.5 典型视频身体证据层", "## 5 分析框架", NEW_VIDEO_SECTION)
    text = text.replace(
        "当前版本不能报告正式经验结果。不能写入的内容包括：人工编码分布、双编码一致性、平台间差异推断、评论频率结论、姿态轨迹差异、动作节奏实测结果、SportsLabKit 身体特征结论，以及任何把 LLM 预填当成人工编码的表述。",
        "当前版本不能报告正式经验结果。不能写入的内容包括：网页学生人工编码分布、双编码一致性、平台间差异推断、评论频率结论、姿态轨迹差异、动作节奏实测结果、SportsLabKit 身体特征结论，以及任何把 LLM 预填当成人工编码的表述。",
    )
    text = text.replace(
        "可以写入的方法事实包括：真实平台样本池已经形成；HF 数据集只作为校准基线；120 条正式人工编码样本已经抽取；deepseek-chat 已形成辅助语义编码记录；评论层已有匿名语境近读材料；典型视频层已有权利确认和本地文件任务包。",
        "可以写入的方法事实包括：真实平台样本池已经形成；HF 数据集只作为校准基线；120 条正式人工编码样本已经抽取；网页学生编码系统已经建立；deepseek-chat 已形成辅助语义编码记录；评论层已有匿名语境近读材料和补采目标表；典型视频层已有权利确认和本地文件任务包。",
    )
    text = replace_between(text, "## 参考文献核验清单", "", NEW_REF_SECTION) if False else text[: text.index("## 参考文献核验清单")] + NEW_REF_SECTION.rstrip() + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
