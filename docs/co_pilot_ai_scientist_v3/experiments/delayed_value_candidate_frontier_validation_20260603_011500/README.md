# Delayed-Value Candidate Frontier Validation

- Run ID: `delayed_value_candidate_frontier_validation_20260603_011500`
- Timestamp UTC: `2026-06-02T10:21:21Z`
- Candidate source: `docs/co_pilot_ai_scientist_v3/experiments/delayed_value_review_candidate_mining_20260603_001500/candidate_reviews.json`
- Attempted reviews: `16`
- Scored reviews: `13`
- Delayed minus control mean score: `0.064`

## Label Results

| Label | Scored | Mean review signal | Mean frontier alignment | Mean review-title delta | Review beats title |
| --- | ---: | ---: | ---: | ---: | ---: |
| delayed_value_replay_candidate | 3 | 0.24 | 0.2833 | 0.04 | 2 |
| generic_or_unrouted | 3 | 0.1867 | 0.2 | 0.0667 | 2 |
| long_horizon_positive_candidate | 3 | 0.28 | 0.3 | 0.1867 | 3 |
| short_term_repair_signal | 4 | 0.09 | 0.1 | 0.03 | 2 |

## Scored Items

- `paper_105_review_1` `delayed_value_replay_candidate` score `0.24` title-delta `0.08` citations `3`: E2ENet: Dynamic Sparse Feature Fusion for Accurate and Efficient 3D Medical Image Segmentation
- `paper_86_review_1` `delayed_value_replay_candidate` score `0.4` title-delta `0.0` citations `1`: Interpretable Relational Representations for Food Ingredient Recommendation Systems
- `paper_147_review_1` `delayed_value_replay_candidate` score `0.08` title-delta `0.04` citations `15`: Prometheus: Inducing Fine-Grained Evaluation Capability in Language Models
- `paper_132_review_2` `long_horizon_positive_candidate` score `0.44` title-delta `0.28` citations `11`: Optimal Rates for Averaged Stochastic Gradient Descent under Neural Tangent Kernel Regime
- `paper_37_review_1` `long_horizon_positive_candidate` score `0.28` title-delta `0.2` citations `15`: Learning Weighted Representations for Generalization Across Designs
- `paper_137_review_0` `long_horizon_positive_candidate` score `0.12` title-delta `0.08` citations `2`: GITA: Graph to Visual and Textual Integration for Vision-Language Graph Reasoning
- `paper_99_review_2` `short_term_repair_signal` score `0.0` title-delta `-0.04` citations `1`: CLASS-INCREMENTAL LEARNING USING GENERATIVE EXPERIENCE REPLAY BASED ON TIME-AWARE REGULARIZATION
- `paper_56_review_1` `short_term_repair_signal` score `0.0` title-delta `0.0` citations `3`: CBOW Is Not All You Need: Combining CBOW with the Compositional Matrix Space Model
- `paper_3_review_2` `short_term_repair_signal` score `0.16` title-delta `0.08` citations `2`: Online Limited Memory Neural-Linear Bandits
- `paper_8_review_1` `short_term_repair_signal` score `0.2` title-delta `0.08` citations `1`: Generating Images from Sounds Using Multimodal Features and GANs
- `paper_52_review_1` `generic_or_unrouted` score `0.12` title-delta `0.0` citations `4`: Robust Constrained Reinforcement Learning for Continuous Control with Model Misspecification
- `paper_3_review_0` `generic_or_unrouted` score `0.12` title-delta `0.04` citations `2`: Online Limited Memory Neural-Linear Bandits
- `paper_33_review_1` `generic_or_unrouted` score `0.32` title-delta `0.16` citations `14`: Machine Learning by Two-Dimensional Hierarchical Tensor Networks: A Quantum Information Theoretic Perspective on Deep Architectures

## Claim Boundary

This is an OpenAlex lexical validation of candidate ranking. It does not prove that a review caused or would have caused a future frontier trajectory; positive candidates still require full TFR replay and semantic or human future-frontier judgement.
