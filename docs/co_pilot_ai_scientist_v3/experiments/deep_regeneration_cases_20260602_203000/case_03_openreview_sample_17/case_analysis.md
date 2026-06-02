# Case Analysis: Knowledge unlearning and privacy risk

- Paper ID: `openreview_sample_17`
- Case type: `strong_frontier_route_candidate`
- Title: Knowledge Unlearning for Mitigating Privacy Risks in Language Models

## Why This Case Was Selected

Review guidance surfaces baselines, metrics, and the breaking-point question for scaling unlearning, which is a concrete later-field route.

## Current Evidence Boundary

This folder is an inspectable pilot replay case. It does not prove a full deep rerun, does not reproduce the original paper's full experiments, and does not establish a validated delayed-value positive case unless the explicit frontier evidence says so.

## Deep Rerun Focus

- Run a small unlearning setup with increasing unlearning-set sizes.
- Measure forget quality, privacy leakage, retained utility, and baseline gaps.
- Compare the generated experiment design with later machine-unlearning and LLM-unlearning benchmarks.
