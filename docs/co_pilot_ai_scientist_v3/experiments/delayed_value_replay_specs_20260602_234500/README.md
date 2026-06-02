# Delayed-Value Replay Specs

- Run ID: `delayed_value_replay_specs_20260602_234500`
- Timestamp UTC: `2026-06-02T15:19:22Z`
- Source triage: `docs/co_pilot_ai_scientist_v3/experiments/delayed_value_deep_case_triage_20260602_232000`
- Case count: `3`
- Conditions: `paper_only, raw_review_guided, six_gate_hybrid_guided, shuffled_review_control`

## Cases

| Case | Domain | Triage | Required conditions |
| --- | --- | ---: | --- |
| `paper_132_review_2` Optimal Rates for Averaged Stochastic Gradient Descent under Neural Tangent Kernel Regime | `deep_learning_theory` | 9.1377 | `paper_only, raw_review_guided, six_gate_hybrid_guided, shuffled_review_control` |
| `paper_105_review_1` E2ENet: Dynamic Sparse Feature Fusion for Accurate and Efficient 3D Medical Image Segmentation | `medical_image_segmentation` | 7.946 | `paper_only, raw_review_guided, six_gate_hybrid_guided, shuffled_review_control` |
| `paper_37_review_1` Learning Weighted Representations for Generalization Across Designs | `causal_generalization` | 7.5753 | `paper_only, raw_review_guided, six_gate_hybrid_guided, shuffled_review_control` |

## Execution Boundary

The specs make the next delayed-value replay executable and auditable. They do not contain generated papers, benchmark results, or human expert ratings.

## Required Per-Case Files

Each case folder contains `replay_spec.json`, `replay_spec.md`, and one prompt per condition. After execution, the folder should be extended with condition plans, condition scores, frontier judgements, and case analysis.
