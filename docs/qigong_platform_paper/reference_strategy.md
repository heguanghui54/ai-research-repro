# Reference Strategy For The Wuhan Sports University Journal Submission

The paper should use references in four layers. This avoids a common failure mode: citing AI/video papers heavily while under-citing the sports-humanities and traditional-sports literature that the target journal expects.

## Layer 1: Target-journal anchor references

Use nearby articles from `wuhan_catalog_reference_matrix.csv` to show direct dialogue with 《武汉体育学院学报》. Priority themes:

- 体育非遗短视频传播
- 体育媒介从符号传播回归具身传播
- 网络民族志作为体育研究方法
- 传统体育养生文化创新性发展
- 导引、八段锦、六字诀史料认知
- 中国体育学自主知识体系
- AI/数智体育的机制、风险与治理

Run:

```bash
python scripts/audit_qigong_citation_coverage.py
```

Then build the balanced target-journal shortlist:

```bash
python scripts/build_qigong_reference_shortlist.py
```

Use `citation_coverage_audit.md` to check whether the manuscript mentions the required themes, and use `reference_shortlist.md` / `reference_shortlist.csv` as the first drafting list. The shortlist deliberately reports category gaps instead of filling them with weak matches. In the current parsed catalog, Health Qigong / traditional sports health references are limited, so additional CNKI or journal-site verification may be needed before submission.

## Layer 2: Core theory references

Use Derrida/deconstruction references sparingly and functionally. The paper should not become a philosophy paper. Theory citations must support these operational concepts:

- 延异
- 踪迹
- 补充
- 可重复性
- 二元对立的解构
- 媒介时间性

The manuscript should translate each concept into coding or observation variables such as `differance_path`, `image_trace_strength`, `supplement_mode`, and `media_temporality`.

## Layer 3: Sports communication and digital platform literature

Use international and Chinese literature on:

- short fitness videos,
- TikTok/Douyin fitness communication,
- platform affordances and visibility,
- cloud fitness and social presence,
- traditional sports or Wushu short-video communication,
- health communication and rumor-debunking short videos.

These references justify why platform visibility, comments, hashtags, and recommendation logic are not neutral channels.

## Layer 4: Technical method references

Use MultiSports, P2ANet, SportsLabKit, pose estimation, and sports action-recognition surveys only for method calibration. Do not cite them as if they directly explain Health Qigong cultural meaning.

Suggested wording:

> MultiSports、P2ANet 和 SportsLabKit 为本文提供姿态可见性、动作节奏和镜头碎片化等可计算指标的技术参照，但健身气功的文化意义与身体经验仍需通过人工编码、网络民族志和体育人文解释加以把握。

## Pre-submission reference gates

- At least 8 target-journal references from the catalog matrix.
- At least 3 Health Qigong/traditional sports health references.
- At least 3 sports communication/platform references.
- At least 2 embodiment/body theory references in sports studies.
- At least 3 technical video-analysis references.
- At least 2 AI ethics/digital sport governance references.

All final references must be checked against official journal/CNKI/publisher metadata before submission.

## Current Verification Status

Run:

```bash
python scripts/build_qigong_reference_verification_pack.py
```

Current output:

- `docs/qigong_platform_paper/reference_verification_pack.md`
- `docs/qigong_platform_paper/reference_verification_pack.csv`
- `docs/qigong_platform_paper/reference_verification_pack.json`

The current target-journal shortlist contains 28 records. All 28 can be traced back to the local Wuhan journal catalog matrix with author, title, journal, year, volume, issue, pages, and DOI. They are ready for drafting, but still require final manual checking against CNKI or the journal page before submission.

For the external theory and technical layers, run:

```bash
python scripts/build_qigong_external_reference_pack.py
```

Current output:

- `docs/qigong_platform_paper/external_reference_verification_pack.md`
- `docs/qigong_platform_paper/external_reference_verification_pack.csv`
- `docs/qigong_platform_paper/external_reference_verification_pack.json`

The external pack currently contains 13 records: 2 core Derrida/deconstruction references, 3 sports video benchmark references, 3 tool-method references, and 5 short fitness / health communication references. These records close the major non-target-journal citation gap for drafting. Their use remains conditional: SportsLabKit may enter the results layer only if the Ubuntu video-analysis run actually succeeds, and benchmark datasets may enter only as method background or calibration baselines, not as substitutes for real short-video platform samples.
