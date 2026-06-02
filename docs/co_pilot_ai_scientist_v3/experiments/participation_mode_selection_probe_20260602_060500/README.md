# Participation-Mode Selection Probe

- Run ID: `participation_mode_selection_probe_20260602_060500`
- Timestamp UTC: `2026-06-02T05:18:03Z`
- Model: `gpt-4o-mini`
- Live model calls: `2`
- Expert-review proxy: `nhop/OpenReview sampled high/low examples from expert_review_taste_prior_probe_20260602_031800`
- Best mode: `structured_feedback_gate`
- Worst mode: `no_human_gate`

## Scope

Same-task offline comparison of five human-participation modes. Scores are model-routed and OpenReview-conditioned; they are not independent human expert review or downstream benchmark evidence.

## Score Table

| Mode | Novelty | Correctness | Clarity | Impact | Confidence | Claim calibration | Workflow utility | Overall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_human_gate | 3 | 2 | 2 | 3 | 2 | 2 | 2 | 2 |
| taste_prior_gate | 4 | 3 | 3 | 4 | 3 | 3 | 4 | 3 |
| evaluator_stress_gate | 4 | 4 | 3 | 4 | 4 | 3 | 4 | 4 |
| structured_feedback_gate | 4 | 4 | 4 | 5 | 4 | 4 | 5 | 5 |
| claim_calibration_gate | 4 | 4 | 4 | 4 | 4 | 5 | 4 | 5 |

## Ranking

`claim_calibration_gate`, `structured_feedback_gate`, `evaluator_stress_gate`, `taste_prior_gate`, `no_human_gate`

## Why The Best Mode Wins

The structured feedback mode provides a systematic approach to improving AI-generated manuscripts, leading to higher clarity and methodological rigor, which are essential for impactful research outputs.

## Mode Design Lessons

- Incorporating structured feedback significantly enhances clarity and rigor in AI-generated manuscripts.
- Human calibration of claims can improve the credibility of research outputs.
- Balancing human input with AI autonomy is crucial to avoid overfitting to preferences.

## Claim Boundary

The effectiveness of structured feedback is contingent on the alignment of feedback criteria with the research objectives and the ability of reviewers to provide constructive insights.

This is an offline, model-routed participation-mode selection probe
conditioned on sampled OpenReview review examples. It is not live
human peer review and does not prove final paper-quality gains.
