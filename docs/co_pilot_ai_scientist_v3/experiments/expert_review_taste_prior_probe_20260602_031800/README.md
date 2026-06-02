# Expert-Review Taste Prior Probe

- Run ID: `expert_review_taste_prior_probe_20260602_031800`
- Timestamp UTC: `2026-06-02T05:04:13Z`
- Dataset: `nhop/OpenReview`
- Config/split: `default` / `train`
- Dataset rows from statistics: `34638`
- Sample size: `160`
- Required fields available: `True`

## Interpretation

The public OpenReview dataset exposes enough expert-review fields to build a limited offline scientific-taste prior for IGRE. It can guide hypothesis selection or manuscript revision, but it cannot replace live human co-pilot interventions or prove performance gains.

## Score Field Coverage In Sample

| Field | Available | Mean | Min | Max |
| --- | ---: | ---: | ---: | ---: |
| mean_score | 160 | 0.5349 | 0.1389 | 1.0 |
| mean_novelty | 27 | 0.6284 | 0.4375 | 0.8333 |
| mean_correctness | 106 | 0.6267 | 0.0 | 1.0 |
| mean_clarity | 71 | 0.5968 | 0.3333 | 0.8333 |
| mean_impact | 73 | 0.5459 | 0.25 | 0.8333 |
| mean_reproducibility | 0 | None | None | None |
| mean_confidence | 158 | 0.6373 | 0.0 | 0.95 |

## High-Score Examples

- `1.0` | Practical Structured Riemannian Optimization with Momentum by using Generalized Normal Coordinates | decision=True
- `1.0` | Efficient Bayesian Sampling Using Normalizing Flows to Assist Markov Chain Monte Carlo Methods | decision=True
- `0.875` | Unifying semi-supervised and robust learning by mixup | decision=True
- `0.8000000000000002` | ​​What learning algorithm is in-context learning? Investigations with linear models | decision=True
- `0.8000000000000002` | Clinical Features and Physiological Signals Fusion Network for Mechanical Circulatory Support Need Prediction in Pediatric Cardiac ICU | decision=True

## Low-Score Examples

- `0.1388888888888889` | KETG: A Knowledge Enhanced Text Generation Framework | decision=False
- `0.2` | Optimizing Data-Flow in Binary Neural Networks | decision=False
- `0.2222222222222222` | Spontaneous Symmetry Breaking in Deep Neural Networks | decision=False
- `0.25` | CausalAF: Causal Autoregressive Flow for Safety-Critical Scenes Generation | decision=False
- `0.2962962962962963` | Generating Images from Sounds Using Multimodal Features and GANs | decision=False

## Claim Boundary

This probe verifies data availability and a feasible offline taste-prior
construction. It is not yet an experiment showing that the prior improves
AI Scientist-v2 outputs.
