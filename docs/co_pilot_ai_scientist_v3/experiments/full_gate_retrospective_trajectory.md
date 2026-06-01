# Retrospective Full-Gate Trajectory

This artifact connects the currently archived Co-Pilot AI Scientist v3 human
gate logs into one auditable trajectory. It is **retrospective**: the gates were
not all executed inside a single online orchestrator run. The purpose is to show
that each proposed human intervention type can be represented with the shared
schema and linked to downstream evidence.

## Gate Chain

| Order | Gate | Decision | Evidence |
| ---: | --- | --- | --- |
| 1 | `idea_gate_001` | Select `hitl-gated-tree-search` as the narrow core contribution while retaining Co-Scientist and OpenEvolve modules as supporting layers. | `candidates.json`, `problem_statement.md` |
| 2 | `evaluator_gate_fairness_metric_guardrail` | Reject fairness primary-metric-only acceptance; require executable code plus a utility floor. | `fml_fairness_evaluator_gate_repair.md` |
| 3 | `branch_gate_causality_online_two_drafts` | Select the second live Causality draft with validation MAE 0.621262 and prune the first draft with validation MAE 1.149610. | `fml_online_branch_gate_drafts/summary.json` |
| 4 | `program_search_gate_001` | Run OpenEvolve smoke test as the AlphaEvolve-style substrate check. | `openevolve_smoke/summary.json` |
| 5 | `claim_gate_001` | Use a conservative pilot-architecture claim and demote full superiority claims to future work. | `claim_evidence_audit.md`, `paper_quality_review_summary.md` |

## What This Proves

- The proposed human intervention points can be serialized as reproducible
  decision artifacts.
- Human gates can reference concrete branch metrics, evaluator failures, program
  search results, and claim audits.
- The current manuscript's conservative claim discipline is itself a logged
  gate decision rather than an informal afterthought.

## What This Does Not Prove

- It does not prove that human gates improve final paper quality.
- It does not prove that a full online Co-Pilot AI Scientist v3 run outperforms
  autonomous AI Scientist-v2.
- It does not replace the remaining requirement for a single online four-loop
  run with all gates active.

## Next Required Online Version

The next version should run the same gate chain in one orchestrated experiment:

1. generate multiple hypotheses;
2. apply `idea_gate`;
3. approve evaluator and guardrails through `evaluator_gate`;
4. run AI Scientist-v2 branch search and apply `branch_gate`;
5. optionally escalate a machine-gradeable subproblem through
   `program_search_gate`;
6. write the paper and apply `claim_gate`;
7. compare against an autonomous AI Scientist-v2 baseline under a matched budget.
