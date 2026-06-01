# Result insertion map for manuscript v0.8

This map prevents the paper from drifting away from the experiment log. Do not convert a design claim into an empirical finding unless the corresponding artifact exists and the audit does not mark it as `fail`.

## Manuscript claim gates

| Manuscript location | Claim type | Required artifact | Minimum evidence before writing as finding |
|---|---|---|---|
| 2.3.1 Data-source hierarchy | HF baseline role | `hf_dataset_inventory.csv` | HF datasets are inventoried with license/modality/status and are described only as calibration baselines |
| 2.3.1 Data-source hierarchy | Real platform evidence | `metadata_validation.csv`, `audit/sampling_coverage_audit.json`, `audit/formal_input_audit.json` | Real platform sample exists; `sampling_coverage_audit` and `real_platform_sample` gates are pass before dissemination claims |
| Abstract, Results sentence | Overall sample claim | `tables/table_1_sample_distribution.csv` | 300-500 metadata rows; platform, keyword, author type, and duration available |
| 2.3 / 4.3 Method path | Student web coding credibility | `formal_merge/web_coding_submissions_export_summary.json`, `formal_merge/web_coding_ingest_audit.json`, `formal_merge/qigong_human_coding_from_web.csv`, `formal_merge/web_human_coding_values_audit.json` | 120 primary tasks complete; merged formal coding has 120 complete rows; value audit has no fail; coder IDs are human web IDs rather than LLM/prefill IDs |
| 2.3 Method path | Double coding credibility | `formal_merge/qigong_double_coding_from_web.csv`, `analysis/coding_reliability.csv`, `analysis/coding_reliability_report.md`, optional reconciliation workbook | Double-coded subset completed; agreement, Cohen's kappa, and nominal Krippendorff's alpha reported for `dominant_frame` and key v0.8 variables |
| 2.3 Method path | LLM coding credibility | `llm/llm_semantic_coding.csv`, `analysis/llm_coding_quality.csv`, `analysis/llm_human_agreement.csv`, `analysis/llm_review_workbook.csv` | Concrete model name, image_count, prompt_version, unknown-rate, low-confidence queue, review workbook, and human spot-check agreement reported |
| 2.3 Method path / Results | Mechanism modeling | `modeling/meaning_frame_model_audit.json`, `modeling/meaning_frame_model_metrics.csv`, `modeling/meaning_frame_feature_importance.csv` | Cross-validated prediction and permutation importance run only after enough human-coded rows and class diversity exist; results framed as predictive association, not causality |
| 2.3.4 Typical-case body evidence | SportsLabKit/fallback evidence | `audit/video_manifest_audit.json`, `audit/sportslabkit_environment_audit.json`, `features/video_features.csv` | SportsLabKit or OpenCV/MediaPipe/OpenCV-only fallback reported honestly; 3-5 typical videos available; official/platform case roles and rights status are auditable; pose/body-visibility claims require MediaPipe/SportsLabKit, while OpenCV-only evidence can support motion, smoothness, tempo-change, and shot-change claims |
| 2.3.4 Typical-case body evidence | Post-upload video gate | `formal_merge/video_file_preflight.json`, `formal_merge/sportslabkit_environment_audit.json`, `formal_merge/video_features_from_typical_cases.csv` | `ready_local_rights >= 3`; at least one standard reference and two platform variants; features extracted only after rights confirmation; tool name in manuscript matches actual extractor |
| 3 Dual-axis model | Theoretical model | `figures/fig_0_differance_image_trace_model.png` | Model figure generated; text explains both axes without treating model as result |
| 4.1 Visibility center | 可视性中心 finding | `formal_merge/qigong_human_coding_from_web.csv`, `formal_merge/tables_from_web_coding/table_1_sample_distribution.csv`, optional `llm_semantic_coding.csv` | `visibility_centrality` filled for 120 human-coded sample rows; distribution supports the claim |
| 4.2 Tempo discipline | 节奏规训 finding | `formal_merge/qigong_human_coding_from_web.csv`, `features/video_features.csv`, `table_2_features_by_meaning_frame.csv` | `tempo_discipline` filled; 3-5 typical video feature rows show rhythm, `motion_smoothness`, `tempo_change_rate`, and shot-change evidence |
| 4.3 Efficacy tagging | 功效化标签 finding | `formal_merge/qigong_human_coding_from_web.csv`, `table_3_llm_semantic_distribution.csv`, `comments/comment_signal_by_video.csv` | `efficacy_tagging`, modern pain-point tags, and comment health-anxiety signals available |
| 4.3 Comment psychology | “收藏等于练过” and psychological offset as frequency finding | `audit/comment_audit.json`, `comments/comment_signal_overall.csv`, `comments/comment_top_terms.csv` | Comment rows collected legally and anonymized; comment audit passes row-count, coverage, and per-video gates; embodiment-deferral signal is nontrivial |
| 4.3 Comment psychology | Comment-layer contextual close reading | `comments_formal_current/comment_evidence_brief.md`, `comments_formal_current/comment_close_reading_cases.md`, `audit/comment_audit.json` | Privacy/anonymization gates pass; comment audit limitations are stated; selected excerpts are used only as qualitative/contextual examples, not prevalence evidence |
| 4 Mechanism analysis | Typical mechanism cases | `tables/table_6_typical_case_selection.csv`, `tables/table_6_typical_case_selection.md` | Cases selected for at least three mechanisms and manually verified before any prose description or quotation |
| 5 Path construction | Strategy recommendations | Tables 1-5 plus theory figures | Recommendations must be tied to observed bottlenecks, not merely normative preference |
| Limitations | AI failure modes | `features/video_features.csv`, audit report | Pose/tracking missingness or failures reported honestly |

## Post-web-coding sequence

After STU01-STU10 finish web coding, run:

```bash
python3 scripts/run_qigong_post_web_coding_pipeline.py
```

The command requires the private `QIGONG_CODING_ADMIN_CODE` environment variable. Do not write that code into the manuscript, GitHub, or public docs. If the command reports `ready_for_formal_audit: False`, keep the manuscript as the current-evidence v0.8 draft.

After TC0001-TC0003 local videos are uploaded and rights-reviewed, run:

```bash
python3 scripts/run_qigong_post_video_upload_pipeline.py
```

Use `--mark-rights-confirmed` only after human rights review confirms local computational analysis permission. If `video_file_preflight.json` is not ready, keep video analysis as method design only.

## Wording rules

- If an artifact is missing, write `本文拟` or `研究设计` language only.
- If the artifact exists but comes from smoke data, write nothing as a real finding.
- If `web_coding_submissions_export_summary.json` reports fewer than 120 complete primary submissions, do not write any human coding distribution as a finding.
- If `web_coding_ingest_audit.json` reports `ready_for_formal_audit: False`, do not generate manuscript result paragraphs from `qigong_human_coding_from_web.csv`.
- If `audit/coding_values_audit.json` has failed value or completion gates, fix the human coding sheet before generating result tables or comparing LLM and human labels.
- If `analysis/coding_reliability.csv` marks a key variable as `poor` or `insufficient`, revise the coding instructions and reconcile disagreements before writing formal findings from that variable.
- If LLM semantic coding has more than 25% `unknown` in `differance_path`, describe it as an exploratory coding aid and add human spot-checking before making distribution claims.
- If `analysis/llm_review_workbook.csv` is absent, do not present LLM coding as formally quality-controlled.
- If `llm_human_agreement.csv` has low agreement on `dominant_frame`/`semantic_frame`, use LLM results only as qualitative assistance and let human coding drive the quantitative results.
- If `modeling/meaning_frame_model_audit.json` is non-pass, do not report feature importance or predictive accuracy as a substantive result.
- If `formal_merge/video_file_preflight.json` reports fewer than three ready rights-confirmed local files, do not report any video feature or pose result.
- If `formal_merge/video_features_from_typical_cases.csv` was produced by OpenCV-only fallback, restrict claims to motion energy, smoothness, tempo-change, and shot-change.
- If pose/video features are absent, do not mention trajectory deviation, center instability, or rhythm disorder as empirical findings. If only OpenCV motion features exist, restrict claims to motion energy, smoothness, tempo-change, and shot-change; do not claim pose keypoint completeness, body visibility area, or body-center jitter.
- If `source_dataset`, `video_id`, `local_video_path`, or notes contain `synthetic` or `smoke`, treat the feature rows as pipeline tests only. They may verify code execution but must not support any manuscript finding.
- If `audit/video_manifest_audit.json` is non-pass, use typical videos only as method preparation or exploratory examples, not as embodied evidence.
- If `tables/table_6_typical_case_selection.csv` is absent or unverified, keep the mechanism discussion at the aggregate level and do not describe individual cases.
- If comments are sparse, use them for qualitative illustration only, not frequency claims.
- If `audit/comment_audit.json` has non-pass privacy/anonymization gates, do not quote or publish comment examples until the issue is fixed.

## Ubuntu completion sequence

1. Run full pipeline with real metadata, comments, LLM semantic coding, and local typical videos.
2. Run `scripts/audit_qigong_research_package.py --root runs/qigong_platform --profile formal`.
3. Open `runs/qigong_platform/audit/research_package_audit.md`.
4. Replace manuscript placeholders only for gates marked `pass`.
5. Move `warn` items into limitations or method cautions.
6. Leave `fail` items out of the results section.
