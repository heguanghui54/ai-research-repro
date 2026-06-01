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
- `architecture.md`: data-flow view of the four loops and five human gates.
- `benchmark_selection.md`: tiered benchmark strategy beyond FML-bench.
- `benchmark_claim_matrix.md`: claim-to-benchmark matrix recording what each
  benchmark can and cannot prove.
- `candidates.json`: candidate research directions and a scoring rubric.
- `experiment_protocol.md`: minimal benchmark and ablation plan.
- `paper_en.md`: English manuscript draft.
- `paper_zh.md`: Chinese manuscript draft.
- `references.bib`: citation seed file for later LaTeX/PDF generation.
- `RUNBOOK_EN.md`: English reproduction and continuation runbook.
- `RUNBOOK_ZH.md`: Chinese reproduction and continuation runbook.
- `experiments/full_gate_retrospective_trajectory.md`: auditable
  retrospective chain linking idea, evaluator, branch, program-search, and
  claim gates.
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
replay over prior AI Scientist-v2/FML-bench runs. It now also includes live
two-draft FML-bench branch-gate probes, snapshot-seeded selected-branch
continuation runs, and two matched-budget four-step autonomous baselines on the
Causality task. The first pair weakly favors human-gated continuation on held
out test MAE (`0.402170` vs. `0.421474`), while the second pair favors the
autonomous baseline (`0.646224` vs. `0.595685`). The two-pair mean slightly
favors autonomous, so the manuscript now treats FML as mixed feasibility
evidence rather than a proof of human-gate superiority. To avoid overfitting the
project to FML-bench, the package also includes a non-FML MLAgentBench
`vectorization` comparison: direct DeepSeek rewrite failed the correctness gate, while
three-iteration OpenEvolve-style search over eight random seeds retained a
correct best program in every seed and achieved median best runtime `0.024581`
seconds versus `3.261186` seconds for the controlled starter program. The result
is stronger than the earlier three-seed probe, but still seed-sensitive because
individual best runtimes range from `0.009210` to `2.984610` seconds. A second
controlled non-FML sklearn diabetes tabular regression probe starts from a
rudimentary mean predictor (`78.572189` RMSE); direct DeepSeek rewrite and three
OpenEvolve seeds all improve to roughly Ridge-level performance, with direct
editing matching the median OpenEvolve RMSE (`55.895460`). This adds a useful
boundary condition: program search should be gated, not automatic. A first
online `Fairness_fairlearn` branch-gate extension was attempted and archived as
`fml_fairness_gated_drafts_failed/`; both drafts failed validation, so it is a
failure-mode/evaluator-gate artifact rather than performance evidence. A
follow-up Fairness evaluator-gate repair probe is archived in
`fml_fairness_evaluator_gate_repair.md`: the API-repaired branch runs but is
worse on the target fairness metric, while an all-negative predictor gets
perfect demographic parity by collapsing balanced accuracy to `0.500000`.
Claims remain intentionally conservative until the evidence is expanded across
more tasks and independently reviewed for paper quality. A Monica-routed claim
audit is archived under `audits/` and is reflected in the manuscript's
claim-audit section. A second paper-quality review pass through Monica-routed
`gpt-4o-mini` and `claude-3-7-sonnet-latest` is also archived; it now treats the
two matched-budget FML pairs as useful but mixed first evidence while still
identifying multi-task matched comparisons and a full four-loop trajectory as
the main blockers before a strong venue submission.

The latest benchmark-expansion probes are deliberately recorded as setup
evidence rather than inflated results. A second official MLAgentBench
`debug`/CIFAR10 attempt repaired the missing `torchvision` dependency but was
stopped when the 170 MB CIFAR10 archive downloaded at only a few hundred KB over
half a minute. A ScienceAgentBench metadata probe confirmed the code repository
and the April 2026 verified-artifact requirement, but HuggingFace metadata was
not reachable from the Ubuntu host. Neither probe is reported as a benchmark
score.

The package now also includes a retrospective full-gate trajectory. It links
the selected research direction, Fairness evaluator guardrail, live Causality
branch gate, OpenEvolve program-search escalation, and claim-audit decision into
one auditable chain. This is evidence that the schema covers all proposed human
gate types, but it is not yet a single online end-to-end co-pilot run.
