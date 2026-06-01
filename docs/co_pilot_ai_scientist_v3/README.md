# Co-Pilot AI Scientist v3 Research Package

This package tracks the paper and reproducibility artifacts for a proposed
human-in-the-loop upgrade to AI Scientist-v2.

## Working Title

Co-Pilot AI Scientist v3: Human-Guided Hypothesis Evolution and Programmatic
Search for Collaborative Automated Research

## Target Claim

AI Scientist-v2 can be converted from a mostly autonomous paper-generation
pipeline into a collaborative research co-pilot by adding structured human
intervention nodes at high-leverage creative and decision points, and by
delegating machine-gradeable subproblems to AlphaEvolve-style code evolution.

## Artifact Map

- `problem_statement.md`: precise research framing, success criteria, and risks.
- `literature_matrix.md`: how AI Co-Scientist, AI Scientist-v2, AlphaEvolve,
  Coscientist, and related systems map into this proposal.
- `benchmark_selection.md`: tiered benchmark strategy beyond FML-bench.
- `candidates.json`: candidate research directions and a scoring rubric.
- `experiment_protocol.md`: minimal benchmark and ablation plan.
- `paper_en.md`: English manuscript draft.
- `paper_zh.md`: Chinese manuscript draft.
- `references.bib`: citation seed file for later LaTeX/PDF generation.
- `RUNBOOK_EN.md`: English reproduction and continuation runbook.
- `RUNBOOK_ZH.md`: Chinese reproduction and continuation runbook.
- `build/`: generated PDFs and other render outputs.

## Build PDFs

The local machine does not need LaTeX. Install the Python dependencies and run:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_copilot_v3_pdfs.py --language both
```

Expected outputs:

- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_en.pdf`
- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_zh.pdf`

## Current Status

This is a working research-production scaffold with preliminary Ubuntu-host
evidence. It includes OpenEvolve-based program search, direct LLM rewrite
baselines, a richer knapsack heuristic task, and retrospective branch-gate
replay over prior AI Scientist-v2/FML-bench runs. It now also includes a live
two-draft FML-bench branch-gate probe and a snapshot-seeded selected-branch
continuation run. To avoid overfitting the project to FML-bench, the package
also includes a non-FML MLAgentBench `vectorization` comparison: direct DeepSeek
rewrite failed the correctness gate, while a three-iteration OpenEvolve-style
search found a correct vectorized program with median runtime `0.051882` seconds
versus `3.261186` seconds for the controlled starter program. Two additional
OpenEvolve seeds produced one failed speedup and one stronger speedup, so the
paper now reports this as promising but seed-sensitive pilot evidence. Claims
remain intentionally conservative until the evidence is expanded across more
tasks/seeds and independently reviewed for paper quality. A Monica-routed claim
audit is archived under `audits/` and is reflected in the manuscript's
claim-audit section.
