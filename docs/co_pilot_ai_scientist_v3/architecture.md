# Co-Pilot AI Scientist v3 Architecture

The architecture is organized as four loops with five explicit human gates. The
gates are not generic approvals: each gate receives a structured frontier and
must write a reproducible decision log.

```text
Research goal
    |
    v
Hypothesis loop  -- idea_selection gate ------------------------------+
    |                                                                 |
    v                                                                 |
Experiment loop  -- evaluator_approval gate --------------------------+
    |                                                                 |
    v                                                                 |
AI Scientist-v2 search loop -- branch_selection gate -----------------+
    |                                      |                          |
    |                                      v                          |
    |                         program_search_escalation gate          |
    |                                      |                          |
    |                         OpenEvolve-controlled subproblem search |
    |                                      |                          |
    +--------------------------------------+--------------------------+
                                           |
                                           v
Draft manuscript and artifacts -- claim_audit gate
                                           |
                                           v
Evidence-aligned paper package
```

## Gate Inputs and Outputs

| Gate | Input | Human action | Output artifact |
| --- | --- | --- | --- |
| `idea_selection` | candidate hypotheses, literature notes, novelty risks | select, merge, or rewrite hypotheses | structured gate log plus approved topic |
| `evaluator_approval` | benchmark, metric, baseline, failure conditions | approve or revise evaluator design | evaluator approval log |
| `branch_selection` | branch frontier with metrics, code snapshots, errors | allocate further search budget | branch-gate log and selected snapshot |
| `program_search_escalation` | machine-gradeable subproblem and direct-edit baseline | decide whether population search is worth the cost | OpenEvolve run plan and result log |
| `claim_audit` | draft paper, metrics, citations, experiment logs | weaken or remove unsupported claims | claim-evidence audit |

## Current Implementation Status

The current repository implements the artifact schema, program-search wrappers,
branch-gate replay/continuation artifacts, paper-quality review artifacts, and
bilingual documentation. The full four-loop end-to-end system still needs a
matched-budget benchmark run where all gates operate in one continuous
trajectory.
