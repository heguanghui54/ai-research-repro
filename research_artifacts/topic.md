# Topic: Self-Evolving Collaborative Agents for Automated AI Research

## Keywords

AI Scientist-v2, automated scientific discovery, agentic tree search, self-evolving agents, multi-agent collaboration, research automation, paper generation, experiment planning.

## TL;DR

Study whether artifact-centric self-evolution and structured multi-agent collaboration improve the reliability and scientific quality of automated AI-research agents, using an AI Scientist-v2 style loop with executable experiment artifacts.

## Concrete Research Question

Can an autonomous AI-research agent improve its own research strategy over repeated experiment cycles, and do structured multi-agent roles improve research quality beyond a strong single-agent AI Scientist-style baseline under the same API and compute budget?

## Hypothesis

An artifact-centric multi-agent system that preserves and revises executable research plans, experiment logs, reviewer critiques, and prompt/code policies will produce more reproducible, higher-scoring research outputs than a single-agent sequential pipeline.

## Success Criteria

- Higher task success rate on a small research-lifecycle benchmark.
- Better reviewer scores for novelty, experiment validity, reproducibility, and clarity.
- Lower rate of invalid claims, missing evidence, and unreproducible experiment outputs.
- Stable improvements across at least three random seeds or task subsets.

## Failure Conditions

- Multi-agent/self-evolution gains vanish after controlling for token budget.
- Improvements come only from longer responses rather than better executable artifacts.
- The system frequently rewrites policies in ways that break reproducibility or inflate claims.
- LLM judging is too noisy to distinguish methods without human spot checks.

## Target Venue Bar

Workshop/system paper: a narrow, reproducible benchmark-and-system contribution is the realistic first target. A top-conference claim would require a larger task suite and stronger human evaluation.

