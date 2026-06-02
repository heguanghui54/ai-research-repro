# Co-Pilot AI Scientist v3 Architecture

The architecture implements **Insight-Gated Research Evolution (IGRE)**. IGRE
is a co-pilot search pattern, not a direct copy of any prior research agent. It
keeps broad executable search in the machine loop, then uses human scientific
taste and insight as explicit, logged, high-variance operators at points where
the search frontier can be reshaped.

The architecture is organized as four loops with six explicit gates. The gates
are not generic approvals: each gate receives a structured frontier and must
write a reproducible decision log.

```text
Research goal
    |
    v
Hypothesis loop  -- scientific_taste_prior gate ----------------------+
    |                                                                 |
    v                                                                 |
Experiment loop  -- evaluator_stress_test gate -----------------------+
    |                                                                 |
    v                                                                 |
Executable frontier search loop -- frontier_steering gate ------------+
    |                                      |                          |
    |                                      v                          |
    |                         verifiable_micro_evolution gate         |
    |                                      |                          |
    |                         OpenEvolve-controlled subproblem search |
    |                                      |                          |
    +--------------------------------------+--------------------------+
                                           |
                                           v
Draft manuscript and artifacts -- structured_feedback gate
                                           |
                                           v
Revised manuscript -- claim_calibration gate
                                           |
                                           v
Evidence-aligned paper package
```

## Gate Inputs and Outputs

| Gate | Input | Human action | Output artifact |
| --- | --- | --- | --- |
| `scientific_taste_prior` | candidate hypotheses, literature notes, novelty risks | select, merge, or rewrite hypotheses by taste, upside, and failure value | structured gate log plus approved topic |
| `evaluator_stress_test` | benchmark, metric, baseline, failure conditions | approve or revise evaluator design and anti-gaming checks | evaluator approval log |
| `frontier_steering` | branch frontier with metrics, code snapshots, errors, novelty notes | allocate further search budget, including to high-upside non-best branches | branch-gate log and selected snapshot |
| `verifiable_micro_evolution` | machine-gradeable subproblem and direct-edit baseline | decide whether population search is worth the cost | OpenEvolve run plan and result log |
| `structured_feedback` | draft artifact, reproducibility gaps, missing definitions, clarity issues | convert informal comments into a concrete revision plan | structured revision log |
| `claim_calibration` | draft paper, metrics, citations, experiment logs | weaken, remove, or reframe unsupported claims | claim-evidence audit |

## Long-Horizon Taste Gate

IGRE also uses a cross-gate meta-policy, the **Long-Horizon Taste Gate
(LHTG)**, to decide when human taste should override short-term metric
pressure. LHTG is not a seventh approval gate. It is a replay-and-routing rule
that looks for **Delayed-Value Review Signals (DVRS)**: comments or human
interventions that create short-term friction, such as lower immediate scores,
missing evidence, or rejection, while pointing toward a mechanism, evaluation
norm, problem framing, or failure mode that later becomes field-relevant. When
LHTG fires, the system does not blindly follow the comment. It queues the case
for Temporal Frontier Replay, routes the actionable part into one of the six
IGRE gates, and records whether the intervention harmed local quality, improved
future-frontier alignment, or did both.

## Tail-Seeking Objective

IGRE does not assume that human participation improves every metric or every
run. Human gates can hurt average short-budget benchmark performance. Their
scientific value is hypothesized to appear in the upper tail: selecting more
original questions, preserving risky but promising branches, detecting weak
evidence, and preventing overclaiming. Evaluations should therefore report both
mean task performance and signals of high-quality research upside.

## Current Implementation Status

The current repository implements the artifact schema, program-search wrappers,
branch-gate replay/continuation artifacts, paper-quality review artifacts, and
bilingual documentation. The full four-loop end-to-end system still needs a
matched-budget benchmark run where all gates operate in one continuous
trajectory.
