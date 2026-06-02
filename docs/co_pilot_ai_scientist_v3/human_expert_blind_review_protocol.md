# Human Expert Blind Review Protocol

## Purpose

This protocol turns the prepared OpenReview regeneration packet into a real
human evaluation. The goal is not to ask whether reviewers "like" the paper,
but to test whether review-guided and six-gate hybrid-review-guided artifacts
show stronger scientific taste, experimental specificity, claim calibration,
and future-frontier potential than matched controls.

## Recruitment

The preferred first cohort is 3-5 NUS-affiliated or school-affiliated ML/AI
researchers, such as faculty members, postdoctoral researchers, PhD students, or
advanced research-track students. This route is better aligned with the paper's
claim than generic crowd work because the target construct is expert scientific
taste and insight.

Participants should be recruited only after checking whether the study requires
institutional ethics review, departmental review, or an exemption
determination. The planned task is minimal-risk expert evaluation, but the
result is intended for research dissemination, so the project should not
self-declare exemption without institutional guidance. The study packet should
include an information sheet, consent language, anonymized artifact pairs, and
the scoring rubric.

## Blind Packet

Each reviewer receives six anonymized A/B pairs. The packet must not reveal
which side is a title/abstract baseline, raw human-review-guided artifact,
unrelated-review context control, or six-gate hybrid-review-guided artifact.
The order is randomized per reviewer.

The currently prepared packet includes three deep case studies, each with
viewable PDF artifacts:

1. LLM refusal and reliability.
2. Conditional graph generation and molecular design.
3. Knowledge unlearning and privacy risk.

Each case contains the original paper summary, human review snippets,
regenerated artifacts, short-term scores, future-frontier evidence, and
six-gate hybrid-review conversion.

## Scoring Rubric

For each A/B pair, reviewers score each artifact from 1 to 5 on:

- Novelty and research taste.
- Methodological soundness.
- Experiment specificity.
- Reproducibility and clarity.
- Claim calibration.
- Future-frontier potential.
- Overall preference.

Reviewers also write a short free-text rationale and identify which artifact,
if any, is more likely to lead to a publishable or future-relevant research
direction.

## Analysis Plan

The main analysis reports paired win counts, mean score deltas, reviewer-level
agreement, and qualitative themes. The paper must separate three evidence
levels:

- Prepared packet: artifacts and rubric are ready, but no human data is
  collected.
- Pilot human evaluation: 3-5 expert reviewers complete the packet.
- Submission-grade human evidence: at least 5 expert reviewers, preregistered
  exclusion rules, randomized order, anonymized artifacts, and released
  aggregate scores.

The preregistered score summarizer is
`scripts/summarize_human_expert_blind_reviews.py`. Running it on the current
empty score-sheet template produces `no_valid_rows`, which is only a smoke test
that the analysis path is ready. Once filled blind score sheets are collected,
the same script should be run with the completed CSV and the hidden condition
key. Positive evidence requires the preregistered rater and valid-row minimums,
plus either a supportive exact-binomial preference result or a bootstrap
confidence interval whose lower bound favors the target condition.

## Claim Boundary

Until the pilot is completed, this protocol supports only evaluation readiness.
It does not prove that human review guidance improves paper quality. After the
pilot, the defensible claim depends on the observed blind expert ratings and
their agreement with model-based and rule-based audits.
