# OpenEvolve Five-Iteration Experiment

## Purpose

Test whether a slightly larger OpenEvolve budget overtakes the one-shot direct
LLM-edit baseline on the same smoke evaluator.

## Setup

- Host: `ubuntu-heshi`
- Remote path: `/home/heshi/work/co-pilot-ai-scientist-v3/openevolve_5iter`
- OpenEvolve: `0.2.27`
- Provider: DeepSeek through OpenAI-compatible API
- Model: `deepseek-chat`
- Iterations: 5
- Random seed: 42
- Islands: 2

## Result

- Initial random-search score: `0.0345`
- Best score after 1 OpenEvolve iteration in this run: approximately `0.0380`
- Best score after 5 OpenEvolve iterations: `0.038007149562376566`
- Best program ID: `8a9805f6-9e74-4658-85cc-d66fd6b73092`
- Best `x`: `1.317145687606326`
- Best objective value: `-0.038007149562376566`

The five-iteration OpenEvolve run substantially improved over the initial
random-search program, but it did not exceed the direct LLM-edit baseline score
of `0.03802139712357032`.

## Interpretation

This result strengthens the design argument for an explicit
`program_search_gate`. OpenEvolve provided a population trace, checkpoints, and
multiple candidates, but on this tiny evaluator the extra iterations did not
beat direct editing. Future experiments should test larger, more rugged search
spaces where population-level exploration is more likely to matter.

