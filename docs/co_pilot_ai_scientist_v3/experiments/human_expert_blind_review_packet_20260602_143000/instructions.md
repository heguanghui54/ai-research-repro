# Human Expert Blind Review Instructions

You are evaluating anonymized mini-paper artifacts generated from real
OpenReview ML/AI papers. Each pair contains two artifacts for the same source
paper. One artifact was generated with paper-specific OpenReview feedback. The
other was generated with the matched-length unrelated-review context control. The order is randomized.

Please do not try to identify which condition is which. Judge only the artifact
quality.

For each pair, score Variant A and Variant B on:

- `problem_framing`: 1-5
- `method_specificity`: 1-5
- `experiment_design`: 1-5
- `limitation_honesty`: 1-5
- `claim_calibration`: 1-5
- `overall_quality`: 1-5

Use integers from 1 to 5:

- 1 = poor or unsupported
- 2 = weak
- 3 = acceptable
- 4 = strong
- 5 = excellent

Then choose `A`, `B`, or `tie` as the pair winner and add a short rationale.

Primary question:

Does one artifact better reflect expert scientific taste and insight through
clearer problem framing, more specific method design, stronger experiments,
more honest limitations, and better claim calibration?

Important boundaries:

- These are short regenerated artifacts, not complete papers.
- Do not judge whether the original paper should be accepted.
- Do not reward verbosity.
- Prefer concrete experimental and claim-calibration improvements over generic
  polish.
