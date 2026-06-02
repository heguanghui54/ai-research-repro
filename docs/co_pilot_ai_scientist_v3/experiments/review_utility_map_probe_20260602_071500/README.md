# OpenReview Review Utility Map Probe

- Run ID: `review_utility_map_probe_20260602_071500`
- Timestamp UTC: `2026-06-02T05:33:47Z`
- Input sample: `docs/co_pilot_ai_scientist_v3/experiments/expert_review_taste_prior_probe_20260602_031800/sample_rows_compact.json`
- Papers covered: `160`
- Review snippets covered: `473`
- Reviews with actionable signal: `398`
- Reviews with noisy signal: `64`
- Mean utility score: `8.3404`

## Category Utility Ranking

| Category | Count | Low-score count | Actionability | IGRE gate | Useful signal |
| --- | ---: | ---: | ---: | --- | --- |
| evaluation_metric | 205 | 137 | 5 | evaluator_stress_test | which tests, baselines, metrics, or ablations the agent must add. |
| limitations_claim_boundary | 140 | 103 | 5 | claim_calibration | which claims should be narrowed before paper writing. |
| novelty_positioning | 111 | 71 | 5 | scientific_taste_prior | whether the direction is worth pursuing or is too incremental. |
| actionable_suggestion | 111 | 70 | 4 | structured_feedback | direct edit or experiment requests that can become tasks. |
| reproducibility_detail | 79 | 52 | 4 | structured_feedback | which missing details prevent independent verification. |
| method_correctness | 71 | 49 | 5 | evaluator_stress_test | which assumptions or implementation details require verification. |
| clarity_presentation | 86 | 47 | 4 | structured_feedback | where manuscript structure or explanation blocks progress. |
| frontier_continuation | 102 | 74 | 3 | frontier_steering | which branch has enough upside to continue, if evidence can catch up. |
| generic_praise | 32 | 19 | 1 | none | usually weak unless paired with a concrete reason. |
| vague_reaction | 32 | 17 | 2 | triage_before_gate | requires decomposition before it can guide an automated step. |

## Gate Pressure

| Gate | Actionable review count |
| --- | ---: |
| evaluator_stress_test | 245 |
| structured_feedback | 210 |
| claim_calibration | 140 |
| scientific_taste_prior | 111 |

## Top Utility Review Examples

- `paper_140_review_1` score=0.32 gates=claim_calibration, evaluator_stress_test, scientific_taste_prior, structured_feedback categories=actionable_suggestion, evaluation_metric, limitations_claim_boundary, method_correctness, novelty_positioning, reproducibility_detail: The paper is mostly well-written. Some details mentioned above could be improved. Unfortunately, its main result is a proof in a six page appendix, which I did not carefully check for correctness. The authors propose a novel method for obstacle avoidance by using online learning theory and provide regret bounds on this. The proposed method is claimed to be efficient, provides instance-optimalty to perturbations and compares favorably to baseline open-loo
- `paper_91_review_0` score=0.6000000000000001 gates=claim_calibration, evaluator_stress_test, scientific_taste_prior, structured_feedback categories=actionable_suggestion, clarity_presentation, evaluation_metric, limitations_claim_boundary, novelty_positioning, reproducibility_detail: Quality - Novel idea that improves self-play through a simple modification. - Empirical results show the effectiveness. Experimental evaluations are extensive. Clarify - Mostly clear. Claims are well supported. Some details missing that could be helpful for reproducibility Paper propose a method for multi-agent reinforcement learning in non-cooperative partially observable environments with communication. The proposed method, TSP, adds imaginary rewards using
- `paper_12_review_2` score=0.5 gates=claim_calibration, evaluator_stress_test, structured_feedback categories=actionable_suggestion, evaluation_metric, limitations_claim_boundary, method_correctness, reproducibility_detail: This work proposes an invariance learning framework by using a training dataset of a single domain and additional data with coarser annotations. Two cross-validation methods are further proposed for the hyperparameter selection. The authors provide theoretical analyses of the proposed methods, and experiments on several datasets show the effecti The authors have discussed and addressed some potential limitations in the paper.
- `paper_71_review_0` score=0.44000000000000006 gates=claim_calibration, evaluator_stress_test, scientific_taste_prior, structured_feedback categories=actionable_suggestion, clarity_presentation, evaluation_metric, limitations_claim_boundary, novelty_positioning: Strengths: - Novel formalization of objective function for finding analogies and feature attribution for BB similarity learners - Diverse evaluation of approach using both objective metrics and a user study Weaknesses/questions: - On objective 1: how can one compare doing LIME over the concatenated (x,z) to having A be diagonal? - On objective 2: Optimization over $\\lambda_1, \\lambda_2$ is unclear, how can one systematically search over them to get intuitive analogies? Fu -
- `paper_16_review_1` score=0.4444444444444444 gates=evaluator_stress_test, structured_feedback categories=actionable_suggestion, clarity_presentation, evaluation_metric, method_correctness, reproducibility_detail: The authors present a method to build knowledge-distilled saliency models from previously published models, and they aim to release the toolbox as a user-friendly platform. The methodology is correct, and I only suggest better explaining why only CC and KL metrics are reported, and not NSS or AUC. I understand that for the general public an easy-to-use platform with several available models is useful. But I wonder if this should be recommended, as the authors show that the st
- `paper_106_review_2` score=0.6111111111111112 gates=claim_calibration, evaluator_stress_test, scientific_taste_prior, structured_feedback categories=actionable_suggestion, evaluation_metric, limitations_claim_boundary, method_correctness, novelty_positioning: (1) Extensive and meaningful experiments with new observations can inform the design of future algorithms. Insightful empirical analyses are a strong plus of the proposed work. Include error bars in Figure 2. (2) Description of the novel box embedding method in section 3 lacks some information. Please describe the complete algorithm using the algorithmic environmen Limitations of the work are described. This work does not seem to introduce any new potential for negative socie
- `paper_140_review_2` score=0.32 gates=claim_calibration, evaluator_stress_test, scientific_taste_prior, structured_feedback categories=clarity_presentation, evaluation_metric, limitations_claim_boundary, novelty_positioning, reproducibility_detail: The author is well-organized with a clear structure. The related work is well-written, especially for readers (like me), who are not very familiar with the field of robust planning. One issue is that the experimental analysis is not enough to support the low-regret claim. And it seems that the major contribution (the non-convex memory FPL algorithm) mainly comes from previous work. The reviewer believes that the results of the experiment are reproducible.
- `paper_44_review_2` score=0.45000000000000007 gates=evaluator_stress_test, structured_feedback categories=actionable_suggestion, clarity_presentation, evaluation_metric, method_correctness, reproducibility_detail: This paper does a good experimental analysis for few-shot NAS. However, the motivation and contributions should be addressed more clearly and the writing also needs to be improved. Existing questions are listed in the above. To resolve the unreasonable cost issue of typical NAS methods, this paper introduces a few-shot NAS setting. They verify several assumptions in the few-show / one-shot NAS setting: 1. supern

## Interpretation

Across the sampled OpenReview snippets, the strongest useful signals are not generic approval. They are review patterns that can be routed to concrete IGRE gates: novelty/positioning to scientific taste priors, evaluation and correctness concerns to evaluator stress tests, limitations to claim calibration, and clarity/reproducibility requests to structured feedback. Generic praise and vague reactions are recorded as low-utility unless they co-occur with actionable details.

## Claim Boundary

This deterministic map shows how real human reviews can be converted into workflow control signals and which categories are more actionable. It does not prove causal improvement in final papers; that requires matched regeneration or prospective co-pilot experiments.
