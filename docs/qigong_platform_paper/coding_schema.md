# Health Qigong short-video coding schema

This file defines the variables for the human coding sheet and later model training.

## Unit of analysis

One public Health Qigong short-video record. If a platform page contains a long video with multiple chapters, code the visible item as one record unless the platform separates clips.

## Metadata variables

| Field | Type | Description |
|---|---|---|
| video_id | string | Local anonymous ID, e.g. QG0001 |
| platform | category | douyin / bilibili / xiaohongshu / kuaishou / other |
| url_hash | string | Hash or non-identifying URL key |
| collection_date | date | Date collected |
| keyword | category | 健身气功 / 八段锦 / 易筋经 / 五禽戏 / 六字诀 / 站桩 / 导引养生功 / other |
| duration_sec | number | Video duration |
| title | text | Title or visible caption, if legally collectable |
| hashtags | text | Hashtags, separated by semicolon |
| author_type | category | individual / institution / coach / media / commerce / unclear |
| like_count | number | Public metric if available |
| comment_count | number | Public metric if available |
| share_count | number | Public metric if available |

## Meaning-frame labels

Code the dominant frame and optional secondary frames.

| Label | Chinese name | Criteria |
|---|---|---|
| instructional_body | 教学身体 | Movement breakdown, standardization, follow-along teaching, correction |
| therapeutic_body | 疗愈身体 | Health preservation, rehabilitation, emotion/sleep/chronic disease, body repair |
| cultural_body | 文化身体 | Traditional culture, heritage, ritual, costume, classical music, national identity |
| spectacular_body | 景观身体 | Visual beauty, performance, trend, music editing, influencer charisma |
| social_body | 社交身体 | Group practice, check-in, comments, duet/remix, companionship |
| commercial_body | 商业身体 | Course selling, institution traffic, paid training, brand/product conversion |
| unclear | 无法判断 | Evidence is insufficient after opening the video |

## Body-experience variables

| Field | Values | Notes |
|---|---|---|
| body_visibility | full_body / upper_body / partial / close_up / unclear | Dominant visual presentation |
| body_count | single / two_three / group / unclear | Visible practitioners |
| movement_tempo | slow_continuous / segmented_teaching / fast_montage / mixed / unclear | Overall rhythm |
| camera_relation | frontal_teaching / side_demo / group_panorama / cinematic / talking_head / mixed / unclear |
| text_occlusion | none / low / medium / high / unclear | Whether captions block body |
| breath_cue | 0/1 | Mentions breathing, inhale/exhale, 调息 |
| mind_cue | 0/1 | Mentions 意念, 放松, 入静, 调心 |
| qi_meridian_cue | 0/1 | Mentions 气, 经络, 丹田, 脏腑 |
| risk_cue | 0/1 | Mentions contraindications or safe practice |
| call_to_action | none / follow_along / check_in / buy_course / share_collect / unclear |
| platform_trace | none / hashtag / hot_music / bullet_comment / duet_remix / live_stream / unclear |

## Deconstruction / differance variables

These variables operationalize the Derridean theory base.

| Field | Values | Notes |
|---|---|---|
| origin_reference | none / official_routine / master_teacher / ancient_tradition / medical_health / national_culture / unclear | What "origin" or authority the video invokes |
| supplement_mode | caption / slow_motion / split_screen / comment_checkin / hashtag_topic / commercial_link / ai_filter / music_edit / mixed / none / unclear | How platform writing supplements body practice |
| binary_reversal | inner_outer / tradition_modern / teaching_performance / health_traffic / master_influencer / slow_fast / none / unclear | Main binary tension or reversal |
| trace_markers | free text | Visible or textual traces: 调息, 经络, 古风, 官方, 打卡, 变瘦, 肩颈等 |
| recontextualization_scene | home_fitness / public_square / scenic_spot / classroom / studio / commerce / challenge / unclear | New context in which the practice is repeated |
| visibility_centrality | low / medium / high / unclear | Whether the video privileges visually obvious external form over inward breath/mind experience |
| tempo_discipline | slow_media / balanced / accelerated / montage / unclear | How platform time reshapes practice rhythm: sustained learning, ordinary teaching, acceleration, or montage |
| efficacy_tagging | none / mild_health / strong_health / medicalized / anxiety_marketing / unclear | Degree to which nonverbal body experience is translated into explicit efficacy labels |
| image_trace_strength | none / weak / moderate / strong / unclear | Whether breath, qi, mind, stillness, continuity, or correction remain visible/audible as traces inside the platform text |
| media_temporality | continuous / fragmented / looped / hot_trend / live_stream / mixed / unclear | Dominant media time structure |
| cyber_wellness_symbol | 0/1 | Whether the video frames Qigong as cyber wellness, office-worker survival, anti-fatigue, or guilt offset |
| meme_density | none / low / medium / high / unclear | Degree of meme/playful framing, including 鬼畜, 保命, 功德+1, 收藏等于练过 |
| embodied_dissolution | none / weak / moderate / strong / unclear | Whether practice is displaced by watching, collecting, joking, or psychological compensation |

## Quality and reliability

Two coders should independently code at least 20% of the sample before full coding. Report percent agreement, Cohen's kappa, and nominal Krippendorff's alpha for the dominant frame and key body/temporal variables. Revise ambiguous categories if reliability is weak, poor, or insufficient.
