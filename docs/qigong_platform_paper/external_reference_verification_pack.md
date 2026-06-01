# 外部理论与技术文献核验包

本文件补足目标刊题录之外的理论、体育视频 benchmark、视频分析工具与平台健康传播文献。它用于投稿前的参考文献核验和方法边界控制；正式投稿前仍需按学校/期刊格式逐条核对出版社、DOI、页码和中文译名。

## 分层覆盖

| Layer | Count | 用途 |
|---|---:|---|
| core_theory | 2 | 德里达延异、踪迹、书写等理论源头 |
| sports_video_benchmark | 3 | 体育视频动作定位/识别 benchmark 背景 |
| tool_method | 3 | SportsLabKit/OpenCV/MediaPipe 等实际或后备工具方法 |
| platform_health_communication | 5 | 短视频健身/健康传播的经验研究参照 |

## 可进入投稿准备流程的条目

1. **derrida_grammatology_1976** (core_theory, publication_metadata_ready)
   - 参考写法：Derrida, J. (1976). Of Grammatology. Translated by Gayatri Chakravorty Spivak. Baltimore: Johns Hopkins University Press.
   - 核验链接：https://jhupbooks.press.jhu.edu/title/grammatology
   - 论文用途：延异、书写与在场形而上学批判的一级理论背景；中文稿中需结合权威中译本核对译名与页码。
   - 边界提醒：只作为理论阐释来源，不直接替代体育传播经验数据。
2. **derrida_margins_1982** (core_theory, publication_metadata_ready)
   - 参考写法：Derrida, J. (1982). Margins of Philosophy. Translated by Alan Bass. Chicago: University of Chicago Press.
   - 核验链接：https://press.uchicago.edu/ucp/books/book/chicago/M/bo3633370.html
   - 论文用途：用于界定 differance、痕迹、补充等概念的英文出处；正式稿需核对中译术语。
   - 边界提醒：概念必须服务于变量化解释，避免把体育论文写成纯哲学论文。
3. **multisports_iccv_2021** (sports_video_benchmark, paper_and_code_ready)
   - 参考写法：Li, Y., Chen, L., He, R., Wang, Z., Wu, G., & Wang, L. (2021). MultiSports: A Multi-Person Video Dataset of Spatio-Temporally Localized Sports Actions. ICCV 2021.
   - 核验链接：https://arxiv.org/abs/2105.07404；项目/文档：https://github.com/MCG-NJU/MultiSports
   - 论文用途：说明多人体体育动作时空定位基准与动作边界标注逻辑；可作为技术校准/背景基准。
   - 边界提醒：不是健身气功短视频平台样本，不能用来证明平台传播延异。
4. **soccernet_v2_cvprw_2021** (sports_video_benchmark, paper_and_dataset_ready)
   - 参考写法：Deliège, A., Cioppa, A., Giancola, S., Seikavandi, M. J., Dueholm, J. V., Nasrollahi, K., Ghanem, B., Moeslund, T. B., & Van Droogenbroeck, M. (2021). SoccerNet-v2: A Dataset and Benchmarks for Holistic Understanding of Broadcast Soccer Videos. CVPR Workshops 2021.
   - 核验链接：https://arxiv.org/abs/2011.13367；项目/文档：https://www.soccer-net.org/
   - 论文用途：说明体育转播视频理解、动作 spotting、镜头切分与回放 grounding 的成熟评测范式。
   - 边界提醒：适合论证体育视频理解技术背景，不参与健身气功文化意义频率统计。
5. **p2anet_tomccap_2024** (sports_video_benchmark, paper_and_code_ready)
   - 参考写法：Bian, J., Li, X., Wang, T., Wang, Q., Huang, J., Liu, C., Zhao, J., Lu, F., Dou, D., & Xiong, H. (2024). P2ANet: A Large-Scale Benchmark for Dense Action Detection from Table Tennis Match Broadcasting Videos. ACM Transactions on Multimedia Computing, Communications, and Applications, 20(4), Article 118. https://doi.org/10.1145/3633516
   - 核验链接：https://dblp.org/rec/journals/tomccap/BianLWWHLZLDX24；项目/文档：https://github.com/Fred1991/P2ANET
   - 论文用途：说明高密度、快速体育动作检测的技术难点，可与短视频剪辑节奏对身体动作可识别性的影响形成方法参照。
   - 边界提醒：乒乓球广播视频基准，不是民族传统体育或短视频平台传播语料。
6. **sportslabkit_pypi** (tool_method, tool_metadata_ready)
   - 参考写法：SportsLabKit. Python package for sports analytics, PyPI project sportslabkit, version 0.3.1.
   - 核验链接：https://pypi.org/project/sportslabkit/；项目/文档：https://sportslabkit.readthedocs.io/en/latest/notebooks/01_get_started/introduction_to_sportslabkit.html
   - 论文用途：如 Ubuntu 环境实际跑通，可作为多目标跟踪、检测器/跟踪器组合、BoundingBoxDataFrame 输出的工具依据。
   - 边界提醒：本地 macOS 当前未跑通；正式稿只能在 Ubuntu 成功产出后写入结果层。
7. **opencv_bradski_2000** (tool_method, bibliographic_metadata_ready)
   - 参考写法：Bradski, G. (2000). The OpenCV Library. Dr. Dobb's Journal of Software Tools, 25, 120-125.
   - 核验链接：https://cir.nii.ac.jp/crid/1570009750919616256?lang=en
   - 论文用途：若最终使用 OpenCV 后备链路做帧差、光流、镜头运动或关键帧抽样，可作为工具文献。
   - 边界提醒：只能支撑实际执行的 OpenCV 指标，不能替代姿态估计或平台意义编码。
8. **blazepose_ghum_2022** (tool_method, paper_metadata_ready)
   - 参考写法：Grishchenko, I., Bazarevsky, V., Zanfir, A., Bazavan, E. G., Zanfir, M., Yee, R., Raveendran, K., Zhdanovich, M., Grundmann, M., & Sminchisescu, C. (2022). BlazePose GHUM Holistic: Real-time 3D Human Landmarks and Pose Estimation. arXiv:2206.11678.
   - 核验链接：https://arxiv.org/abs/2206.11678
   - 论文用途：若采用 MediaPipe/BlazePose 后备链路，可支撑单目视频人体关键点与姿态估计的技术依据。
   - 边界提醒：必须明确其为后备或辅助方法；不应写成 SportsLabKit 已完成结果。
9. **tiktok_fitness_covid_frontiers_2022** (platform_health_communication, peer_reviewed_ready)
   - 参考写法：Liu, Y., & Wang, X. (2022). Communication Mechanism and Optimization Strategies of Short Fitness-Based Videos on TikTok During COVID-19 Epidemic Period in China. Frontiers in Communication, 7, 778782. https://doi.org/10.3389/fcomm.2022.778782
   - 核验链接：https://www.frontiersin.org/journals/communication/articles/10.3389/fcomm.2022.778782/full
   - 论文用途：直接支撑中国语境下短健身视频传播机制、时空扩散和优化路径的文献综述。
   - 边界提醒：研究对象是疫情期间健身短视频，不等同于健身气功的身体经验与延异机制。
10. **tiktok_health_science_qca_2023** (platform_health_communication, peer_reviewed_ready)
   - 参考写法：Tian, Y., Liu, S., & Zhang, D. (2023). Clearness qualitative comparative analysis of the spread of TikTok health science knowledge popularization accounts. Digital Health, 9. https://doi.org/10.1177/20552076231219116
   - 核验链接：https://journals.sagepub.com/doi/abs/10.1177/20552076231219116
   - 论文用途：支撑健康科普账号传播条件组态、平台健康知识传播与 QCA 方法参照。
   - 边界提醒：账号层传播研究，不提供本研究视频内容编码结果。
11. **edutok_health_content_2023** (platform_health_communication, peer_reviewed_ready)
   - 参考写法：Basch, C. H., Meleo-Erwin, Z., Fera, J., Jaime, C., & Basch, C. E. (2023). Using TikTok to Educate, Influence, or Inspire? A Content Analysis of Health-Related EduTok Videos. Journal of Health Communication, 28(8). https://doi.org/10.1080/10810730.2023.2234866
   - 核验链接：https://www.tandfonline.com/doi/abs/10.1080/10810730.2023.2234866
   - 论文用途：为健康类短视频内容分析、互动指标和教育/激励/影响框架提供国际参照。
   - 边界提醒：非中国健身气功样本；只作为健康短视频内容分析参照。
12. **social_media_fitness_intention_2024** (platform_health_communication, peer_reviewed_ready)
   - 参考写法：Yin, H., Huang, X., & Zhou, G. (2024). An Empirical Investigation into the Impact of Social Media Fitness Videos on Users' Exercise Intentions. Behavioral Sciences, 14(3), 157. https://doi.org/10.3390/bs14030157
   - 核验链接：https://pubmed.ncbi.nlm.nih.gov/38540460/
   - 论文用途：支撑健身视频对用户运动意向影响的 S-O-R/信源可信度/内容质量视角。
   - 边界提醒：解释用户意向，不直接测量本研究的延异、踪迹和具身消解变量。
13. **short_fitness_video_visibility_2024** (platform_health_communication, peer_reviewed_ready)
   - 参考写法：Xu, X. (2024). Being there and being with them: the effects of visibility affordance of online short fitness video on users' intention to cloud fitness. Frontiers in Psychology, 15, 1267502. https://doi.org/10.3389/fpsyg.2024.1267502
   - 核验链接：https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1267502/full
   - 论文用途：补充“可见性 affordance”如何影响云健身/跟练意向，可与本文可视性中心和平台规训机制对话。
   - 边界提醒：该文讨论云健身意向，不直接证明健身气功符号延异，需放在综述或讨论层。

## 写入论文的边界规则

1. 德里达文献进入理论框架，但必须落到可编码变量和体育身体经验，不单独构成经验结论。
2. MultiSports、SoccerNet、P2ANet 只能说明体育视频分析技术背景或校准思路，不能替代真实短视频平台样本。
3. SportsLabKit 只有在 Ubuntu 环境实际跑通并产出可审计日志后，才能写成结果工具；否则只能写为预设工具或改写为 OpenCV/MediaPipe 后备链路。
4. 平台健康传播文献用于文献综述与讨论，不应混同为本研究对健身气功短视频的实证发现。
5. 公开稿件只写具体模型和工具名称，不写私有聚合平台、密钥、内部导出接口或 AI 工作流为作者。
