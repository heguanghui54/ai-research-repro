# Replay Spec: Learning Weighted Representations for Generalization Across Designs

- Review ID: `paper_37_review_1`
- Domain: `causal_generalization`
- Candidate label: `long_horizon_positive_candidate`
- Triage score: `7.5753`
- Required conditions: `paper_only, raw_review_guided, six_gate_hybrid_guided, shuffled_review_control`

## Replay Question

Can human taste around causal structure and distribution shift steer an automated researcher from weighted representations toward a stronger study of treatment-effect generalization across changing designs?

## Minimal Experiment

- Generate a follow-up causal inference experiment with train/test design shift.
- Require a paper-only, review-guided, and control plan to specify covariate shift, treatment-policy shift, and outcome-model shift separately.
- Compare against later frontier descriptors around causal representation learning, domain generalization, and robust policy evaluation.

## Short-Term Metrics

- identification clarity
- baseline choice under design shift
- specificity of synthetic or semi-synthetic benchmark

## Frontier Metrics

- alignment with causal representation and domain generalization themes
- explicit handling of policy/design shift
- quality of failure-mode analysis

## Failure Modes

- confusing prediction generalization with causal identification
- using generic domain adaptation language without treatment-effect metrics
- review guidance improving prose but not the causal experiment

## Positive Delayed-Value Rule

- raw_review_guided or six_gate_hybrid_guided has lower short_term_score than paper_only
- the same guided condition has higher frontier_alignment_score than paper_only
- the same guided condition beats shuffled_review_control on frontier_alignment_score
- the responsible review signal is specific and actionable
- later-frontier evidence passes bibliographic and semantic match guards

## Claim Boundary

This is a preregistered replay specification. It is not an executed replay and must not be counted as evidence that human review improves research output.
