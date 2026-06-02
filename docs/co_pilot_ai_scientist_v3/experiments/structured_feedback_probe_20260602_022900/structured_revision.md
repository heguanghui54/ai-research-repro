```markdown
# Online Insight-Gated Research Evolution: A Full-Gate Smoke Manuscript

## Abstract

This manuscript is generated from the online trajectory `online_full_gate_smoke_20260602_013612`. The trajectory exercises the proposed Insight-Gated Research Evolution (IGRE) loop: idea selection, evaluator approval, branch selection, verifiable program-search escalation, and claim calibration. It runs remote FML-bench work and a small OpenEvolve-style knapsack search on `ubuntu-heshi`. The selected branch has validation MAE `n/a`, the continuation test MAE is `n/a`, and the program search best score is `0.994177`. The claim supported by this trajectory is online orchestration and manuscript production from logged evidence, not superiority over autonomous AI Scientist-v2.

## 1. Introduction

AI Scientist-v2 style systems can move from hypotheses to experiments and paper drafts, but they usually treat human scientists as outside operators rather than explicit search participants. IGRE instead represents human scientific taste as an auditable search intervention. This is particularly important when scalar metrics are insufficient: deciding which problem is worth pursuing, whether a failed branch is informative, whether an evaluator can be gamed, and how far a claim may be carried.

This manuscript is not a polished conference submission. It is a trace-bound paper artifact that tests whether a fresh online gate chain contains enough structured evidence to support a complete, claim-calibrated manuscript.

## 2. Method

IGRE decomposes co-pilot automated science into gates. Automated components propose branches, run evaluators, and generate code changes. Human gates can change the search frontier, but every intervention must record options, rationale, affected artifacts, downstream budget, and attention cost when measured. The same schema is used for idea gates, evaluator gates, branch gates, program-search escalation gates, and claim gates.

The trajectory's gate decisions are:

| Gate | Type | Decision | Attention minutes | Evidence role |
| --- | --- | --- | ---: | --- |
| `idea_gate_online_smoke_001` | `idea_selection` | `hitl-gated-tree-search` | n/a | 1 artifacts |
| `evaluator_gate_online_smoke_001` | `evaluator_approval` | `fml_metric_plus_guardrails` | n/a | 2 artifacts |
| `branch_gate_online_smoke_001` | `branch_selection` | `abort_no_valid_branch` | n/a | 1 artifacts |
| `program_search_gate_online_smoke_001` | `program_search_escalation` | `run_tiny_openevolve_knapsack` | n/a | 1 artifacts |
| `claim_gate_online_smoke_001` | `claim_audit` | `claim_online_orchestration_feasible` | n/a | 4 artifacts |

## 3. Experimental Setup

The online run uses remote root `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_013502`. The FML branch frontier summary is `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_013502/branch_frontier/ai_scientist_v2/Fairness_fairlearn/20260602_093507_8b36a1f7/summary.json`; the selected continuation summary is `None`; and the program-search summary is `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_013502/program_search/knapsack_openevolve_1iter/summary.json`. The branch gate selects `abort_no_valid_branch` from the online frontier. The program-search gate runs a small OpenEvolve-style knapsack search as the AlphaEvolve-inspired verifiable micro-evolution module.

## 4. Results

| Quantity | Value |
| --- | ---: |
| Selected branch validation MAE | n/a |
| Continuation test MAE | n/a |
| Program-search best score | 0.994177 |

These results are smoke-test evidence. They show that the online gate chain can drive real remote experiments and produce a manuscript from the resulting evidence. However, they do not demonstrate that the human-gated continuation outperforms a matched autonomous baseline.

## 5. Claim Audit

Supported:

- The trajectory exercises all five IGRE gate types in a single online run.
- The trajectory links gate decisions to remote FML and program-search artifacts.
- The logged evidence is sufficient to generate a complete manuscript-shaped artifact with explicit limitations.

Unsupported:

- Claims of full Co-Pilot AI Scientist v3 superiority over autonomous AI Scientist-v2.
- Claims regarding human-attention efficiency, as measured active review time is missing for this online smoke run unless filled prospectively.
- Claims of top-conference empirical strength, as this is one small-budget smoke trajectory without a matched autonomous manuscript baseline.

## 6. Limitations

The run is intentionally small, mixing a Causality FML branch task with a knapsack program-search subproblem, using a tiny search budget, and lacking attention-cost fields for the online gates. The manuscript is generated deterministically from artifacts, testing evidence packaging rather than LLM writing quality. A stronger study would require matched autonomous trajectories, multiple tasks and seeds, independent paper-quality evaluation, and prospective attention-cost timing.

## 7. Conclusion

This online trajectory manuscript narrows the gap between a gate-schema demo and an AI Scientist-v2-style paper-production loop. It demonstrates that IGRE can produce a trace-bound manuscript from online evidence, while emphasizing that human scientific taste must be evaluated, not assumed to enhance performance.
```
