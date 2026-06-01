# Problem Statement

## One-Sentence Problem

Current autonomous research systems can generate ideas, run experiments, and
write papers, but they still provide weak support for timely human intervention
at the creative and strategic nodes where expert judgment most improves paper
quality.

## One-Sentence Hypothesis

A human-in-the-loop AI Scientist-v3 architecture that combines AI
Co-Scientist-style hypothesis evolution, AI Scientist-v2-style experiment and
writeup automation, and AlphaEvolve-style programmatic search will produce more
novel, credible, and useful research papers than a fully autonomous baseline
under the same compute budget.

## Success Metrics

- Higher expert-rated paper quality on novelty, methodological rigor, clarity,
  reproducibility, and significance.
- Higher benchmark performance or robustness for tasks with executable metrics.
- Lower rate of unsupported claims in the generated manuscript.
- Better alignment between human research intent and final paper contribution.
- Lower wasted experiment budget on unpromising directions after human gates.

## Failure Conditions

- Human intervention nodes add latency but do not improve paper quality.
- The system overfits to human preferences and reduces exploration diversity.
- AlphaEvolve-style search improves local code metrics but not paper-level
  scientific contribution.
- Human gates become ad hoc comments rather than structured, reproducible
  decisions.
- The workflow cannot be reproduced from logs, prompts, code, and artifacts.

## Target Venue Bar

The first defensible target is a workshop/system paper at a machine learning or
AI-for-science venue. A top-conference claim requires stronger evidence:
multi-task evaluation, external expert review, ablations of human intervention
placement, and transparent reproducibility artifacts.

## Core Research Question

Where should humans be inserted into an automated research loop so that their
limited attention most improves scientific quality without collapsing the
benefits of autonomous search?

