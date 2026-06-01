# FML-bench Human Branch-Gate Replay

## Purpose

Use real AI Scientist-v2/FML-bench smoke-run artifacts to evaluate where a
human branch-selection gate would have changed the research trajectory.

This is a replay analysis, not a new benchmark run. It uses logged validation
steps, model analyses, editor logs, and final summaries from prior Ubuntu runs.

## Source Runs

### Causality_causalml

- Host: `ubuntu-heshi`
- Result path:
  `/home/heshi/work/fmlbench-smoke-results-fixed2/ai_scientist_v2/Causality_causalml/20260530_004241_dced73c8`
- Provider/model: DeepSeek / `deepseek-chat`
- Total steps: 4
- Baseline validation metric: `1.2962585694753708`
- Best validation metric: `0.5989426968010781`
- Test primary metric: `0.6177188971481032`

Step-level replay:

| Step | Action | Validation metric | Result |
| --- | --- | ---: | --- |
| 1 | draft | 0.5989426968 | best branch |
| 2 | draft | 0.6278368681 | worse than step 1 |
| 3 | improve | 0.6214612657 | worse than step 1 |
| 4 | improve | 0.5989426968 | ties step 1 |

Replay decision: after two drafts, keep step 1 and stop exploring step 2.

### Fairness_fairlearn

- Host: `ubuntu-heshi`
- Result path:
  `/home/heshi/work/fmlbench-fairlearn-results-fixed3/ai_scientist_v2/Fairness_fairlearn/20260530_010425_087411ff`
- Provider/model: DeepSeek / `deepseek-chat`
- Total steps: 4
- Baseline validation metric: `0.18663158848996153`
- Best validation metric: `0.3164673438990605`
- Test primary metric: `0.31600465679075357`

Step-level replay:

| Step | Action | Validation metric | Result |
| --- | --- | ---: | --- |
| 1 | draft | 0.3164673439 | worse than baseline |
| 2 | draft | null | bug: Fairlearn preprocessing/API issue |
| 3 | improve | 0.3312074117 | worse than step 1 |
| 4 | improve | null | bug: unsupported `run_linprog` argument |

Replay decision: after the first failed/worse attempts, pause the branch and
request an evaluator or algorithm reset before spending more budget.

## Interpretation

The replay supports the value of explicit human branch gates:

- In Causality, a gate would preserve the strong first branch and avoid spending
  additional budget on a worse draft/refinement.
- In Fairness, a gate would detect that the branch was both worse than baseline
  and unstable, then route the system toward compatibility repair or a new
  intervention strategy.

This is retrospective evidence. A stronger future experiment should run the
human-gated policy online, not only replay it after the fact.

