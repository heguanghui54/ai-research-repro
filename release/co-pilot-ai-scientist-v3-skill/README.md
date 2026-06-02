# Co-Pilot AI Scientist v3 Skill

Insight-Gated Research Evolution (IGRE) for collaborative automated science.

This is a standalone release scaffold for the Co-Pilot AI Scientist v3 skill.
It is designed for researchers who want an AI research co-pilot rather than a
fully autonomous paper generator. The skill turns human scientific taste and
expert judgment into six auditable workflow gates inside an AI
Scientist-v2-style research loop.

## What It Does

- Helps frame a research question and success/failure criteria.
- Logs human scientific taste as a structured research-control signal.
- Stress-tests evaluators before expensive runs.
- Steers hypothesis and experiment frontiers at budget checkpoints.
- Escalates machine-gradeable subproblems to OpenEvolve-style program search
  only when warranted.
- Converts feedback into concrete revision actions.
- Calibrates claims before paper drafting or submission.

## The Six IGRE Gates

| Gate | Purpose |
| --- | --- |
| `scientific_taste_prior` | Select or reweight research directions using taste, insight, and high-tail upside. |
| `evaluator_stress_test` | Reject weak, gameable, or invalid metrics before the agent optimizes them. |
| `frontier_steering` | Decide which branch deserves more budget, including non-metric high-upside branches. |
| `verifiable_micro_evolution` | Trigger code/program search for narrow machine-gradeable subproblems. |
| `structured_feedback` | Convert review comments into concrete, auditable revision actions. |
| `claim_calibration` | Remove, weaken, or reframe unsupported claims. |

## Install

For a local Codex skill installation, copy this folder into your Codex skills
directory:

```bash
mkdir -p ~/.codex/skills
cp -R release/co-pilot-ai-scientist-v3-skill ~/.codex/skills/co-pilot-ai-scientist-v3
```

Then start a new Codex session and invoke:

```text
Use the co-pilot-ai-scientist-v3 skill to plan a human-gated research run on ...
```

## Quickstart

1. Open `examples/toy_task_spec.md`.
2. Edit the topic, success criteria, failure criteria, and candidate gates.
3. Ask Codex to run the skill on that task.
4. Save any human decision as a gate log using
   `templates/human_gate_log_template.json`.
5. Run:

```bash
python3 scripts/validate_release.py
```

The validator checks that the release has the required files, gate names, and
example artifacts. It does not evaluate scientific quality.

## What This Is Not

- It is not a humanizer.
- It is not a replacement for expert judgment.
- It is not proof that human-gated agents outperform autonomous agents.
- It is not a generic manuscript-writing pipeline.

The skill is an engineering artifact. It is not scientific superiority
evidence. Scientific claims still require matched benchmarks, blind expert
review, and honest claim calibration.

## Relation To Prior Work

This release is inspired by automated-science and research-skill systems such
as AI Scientist, AI Scientist-v2, AI Co-Scientist, AlphaEvolve/OpenEvolve,
PaperOrchestra, and high-adoption academic skill repositories such as
`academic-research-skills`. Its distinct contribution is the IGRE six-gate
control loop: human input is treated as a typed, auditable search-control
operator rather than generic approval or extra context.

## Evidence Boundary

Community adoption, GitHub stars, forks, and external reuse would be engineering
impact evidence. They do not prove scientific superiority. Use this skill to
create auditable traces, then evaluate those traces with matched autonomous
baselines and expert review.
