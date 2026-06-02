# Replay Spec: Optimal Rates for Averaged Stochastic Gradient Descent under Neural Tangent Kernel Regime

- Review ID: `paper_132_review_2`
- Domain: `deep_learning_theory`
- Candidate label: `long_horizon_positive_candidate`
- Triage score: `9.1377`
- Required conditions: `paper_only, raw_review_guided, six_gate_hybrid_guided, shuffled_review_control`

## Replay Question

Can human review emphasizing generalization and theory steer an automated researcher from a narrow NTK-rate result toward a more frontier-aligned study of averaged SGD, finite-width effects, and generalization mechanisms?

## Minimal Experiment

- Generate a follow-up theorem-or-experiment plan for averaged SGD under NTK-like assumptions.
- Require at least one stress test outside the exact assumptions of the original proof.
- Compare the generated plan against later frontier descriptors around generalization, finite-width behavior, and optimization dynamics.

## Short-Term Metrics

- technical correctness of proposed theorem/experiment
- clarity of assumptions
- baseline and prior-work calibration

## Frontier Metrics

- alignment with later generalization and finite-width NTK themes
- mechanistic depth beyond restating the original rate result
- specificity of testable predictions

## Failure Modes

- generic theory praise without a new stress test
- overclaiming beyond the original assumptions
- frontier alignment driven only by title terms such as neural or generalization

## Positive Delayed-Value Rule

- raw_review_guided or six_gate_hybrid_guided has lower short_term_score than paper_only
- the same guided condition has higher frontier_alignment_score than paper_only
- the same guided condition beats shuffled_review_control on frontier_alignment_score
- the responsible review signal is specific and actionable
- later-frontier evidence passes bibliographic and semantic match guards

## Claim Boundary

This is a preregistered replay specification. It is not an executed replay and must not be counted as evidence that human review improves research output.
