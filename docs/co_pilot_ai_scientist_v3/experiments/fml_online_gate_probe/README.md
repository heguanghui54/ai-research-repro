# FML Online Gate Probe

This live probe ran AI Scientist-v2 on `Causality_causalml` for two steps with
the default stage-budget ratios. Because the small `max_steps=2` budget rounded
the early stage budgets to zero, the agent executed one creative draft and one
ablation refinement rather than two independent drafts.

## Results

- baseline validation MAE: `1.2962585694753708`
- step 1 draft validation MAE: `0.6260980338444772`
- step 2 improve validation MAE: `0.6260980338444772`
- final test MAE: `0.525773779316556`
- total steps: `2`
- total ideas: `1`

## Interpretation

This run is useful as a live plumbing check, but the cleaner branch-selection
evidence is stored in `../fml_online_branch_gate_drafts/`, where the temporary
agent config forces two first-stage draft branches.
