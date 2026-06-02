```markdown
# Online Insight-Gated Research Evolution: A Full-Gate Smoke Manuscript

## Abstract

This manuscript is generated from the online trajectory `online_full_gate_smoke_20260602_013612`. The trajectory exercises the proposed Insight-Gated Research Evolution (IGRE) loop, which includes idea selection, evaluator approval, branch selection, verifiable program-search escalation, and claim calibration. It runs remote FML-bench work and a small OpenEvolve-style knapsack search on `ubuntu-heshi`. The selected branch has validation MAE `n/a`, the continuation test MAE is `n/a`, and the program search best score is `0.994177`. The claim supported by this trajectory is that online orchestration and manuscript production from logged evidence is feasible, but it does not demonstrate superiority over autonomous AI Scientist-v2.

## 1. Introduction

AI Scientist-v2 style systems can move from hypotheses to experiments and paper drafts, but they typically treat human scientists as external operators rather than as integral participants in the search process. IGRE addresses this gap by representing human scientific judgment as an auditable search intervention. This approach is particularly important when scalar metrics are insufficient for decision-making, such as determining which problems are worth pursuing, assessing the informativeness of failed branches, evaluating the potential for evaluator bias, and understanding the extent to which a claim can be substantiated.

This manuscript serves as a preliminary exploration of whether a fresh online gate chain can provide sufficient structured evidence to support a complete, claim-calibrated manuscript.

## 2. Method

IGRE decomposes co-pilot automated science into gates. Automated components propose branches, run evaluators, and generate code changes. Human gates can modify the search frontier, but every intervention must record options, rationale, affected artifacts, downstream budget, attention cost (when measurable), and follow-up checks. This schema applies to idea gates, evaluator gates, branch gates, program-search escalation gates, and claim gates.

The trajectory's gate decisions are:

| Gate | Type | Decision | Attention minutes | Evidence role |
| --- | --- | --- | ---: | --- |
| `idea_gate_online_smoke_001` | `idea_selection` | `hitl-gated-tree-search` | n/a | 1 artifact |
| `evaluator_gate_online_smoke_001` | `evaluator_approval` | `fml_metric_plus_guardrails` | n/a | 2 artifacts |
| `branch_gate_online_smoke_001` | `branch_selection` | `abort_no_valid_branch` | n/a | 1 artifact |
| `program_search_gate_online_smoke_001` | `program_search_escalation` | `run_tiny_openevolve_knapsack` | n/a | 1 artifact |
| `claim_gate_online_smoke_001` | `claim_audit` | `claim_online_orchestration_feasible` | n/a | 4 artifacts |

## 3. Experimental Setup

The online run utilizes remote root `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_013502`. The FML branch frontier summary is located at `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_013502/branch_frontier/ai_scientist_v2/Fairness_fairlearn/20260602_093507_8b36a1f7/summary.json`; the selected continuation summary is `None`; and the program-search summary is at `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_013502/program_search/knapsack_openevolve_1iter/summary.json`. The branch gate selects `abort_no_valid_branch` from the online frontier. The program-search gate runs a small OpenEvolve-style knapsack search as the AlphaEvolve-inspired verifiable micro-evolution module.

## 4. Results

| Quantity | Value |
| --- | ---: |
| Selected branch validation MAE | n/a |
| Continuation test MAE | n/a |
| Program-search best score | 0.994177 |

These results serve as preliminary evidence, indicating that the online gate chain can facilitate real remote experiments and produce a manuscript from the resulting evidence. However, they do not demonstrate that the human-gated continuation outperforms a matched autonomous baseline.

## 5. Claim Audit

Supported:

- The trajectory exercises all five IGRE gate types in a single online run.
- The trajectory links gate decisions to remote FML and program-search artifacts.
- The logged evidence is sufficient to generate a complete manuscript-shaped artifact with explicit limitations.

Unsupported:

- Claims of full Co-Pilot AI Scientist v3 superiority over autonomous AI Scientist-v2.
- Human-attention efficiency, as measured active review time is absent for this online smoke run unless filled prospectively.
- Top-conference empirical strength, given that this is a small-budget smoke trajectory without a matched autonomous manuscript baseline.

## 6. Limitations

The run is intentionally small, combining a Causality FML branch task with a knapsack program-search subproblem, utilizing a limited search budget, and lacking attention-cost data for the online gates. The manuscript is generated deterministically from artifacts, focusing on evidence packaging rather than LLM writing quality. Future studies should include matched autonomous trajectories, multiple tasks and seeds, independent evaluations of paper quality, and prospective attention-cost timing.

## 7. Conclusion

This online trajectory manuscript narrows the gap between a gate-schema demonstration and an AI Scientist-v2-style paper-production loop. It illustrates that IGRE can produce a trace-bound manuscript from online evidence while highlighting the critical point that human scientific judgment must be evaluated rather than assumed to be beneficial.
```
