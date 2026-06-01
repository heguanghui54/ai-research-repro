# Literature Matrix

## AI Co-Scientist

- Role in this proposal: upstream hypothesis engine.
- Imported idea: generate, debate, refine, and rank hypotheses using multiple
  specialized agents.
- Human node: experts can steer research goals, reject unsafe or low-value
  hypotheses, and add evidence that the model missed.
- Limitation addressed here: AI Co-Scientist is strong at hypothesis formation
  but does not by itself complete a code-experiment-paper loop.
- Link: https://arxiv.org/abs/2502.18864

## AI Scientist-v2

- Role in this proposal: experiment and paper production backbone.
- Imported idea: agentic tree search over experiment trajectories, benchmark
  execution, automated writeup, and reviewer-style reflection.
- Human node: experts can intervene at idea selection, tree branch selection,
  benchmark acceptance, negative-result interpretation, and final claim audit.
- Limitation addressed here: mostly autonomous operation can miss high-level
  research taste, field-specific constraints, and creative reframing.
- Link: https://arxiv.org/abs/2504.08066

## AlphaEvolve

- Role in this proposal: deep optimizer for machine-gradeable subproblems.
- Imported idea: evolve code using LLM-generated diffs, automatic evaluators,
  program databases, and diversity-preserving search.
- Human node: experts specify evaluation functions, choose abstraction level,
  inspect surprising high-scoring programs, and approve escalation to expensive
  evaluations.
- Limitation addressed here: AlphaEvolve needs automatic evaluators and does not
  cover full scientific argumentation or paper writing.
- Link: https://arxiv.org/abs/2506.13131

## FunSearch

- Role in this proposal: predecessor for program-search discovery.
- Imported idea: LLM-guided program search can discover mathematical objects
  when correctness and quality can be scored automatically.
- Link: https://www.nature.com/articles/s41586-023-06924-6

## Coscientist

- Role in this proposal: reference point for physical-world experimental
  automation.
- Imported idea: tool-using LLM agents can plan and execute chemistry workflows
  when connected to instruments, APIs, and safety constraints.
- Human node: laboratory safety, materials feasibility, and wet-lab validation.
- Link: https://www.nature.com/articles/s41586-023-06792-0

## OpenEvolve

- Role in this proposal: the practical open-source implementation layer for
  AlphaEvolve-style experiments, because the official AlphaEvolve core system is
  not open sourced.
- Imported idea: reusable evolutionary coding loop with custom evaluator files,
  OpenAI-compatible model routing, MAP-Elites quality-diversity search,
  island-based populations, multi-objective optimization, and reproducible seeds.
- Use in experiments: local prototype for programmatic subproblem search when a
  subproblem has an executable evaluator. It should be treated as an
  AlphaEvolve-style substitute rather than evidence that the official DeepMind
  system has been reproduced.
- Candidate examples to adapt: function minimization, symbolic regression,
  circle packing, adaptive sorting, and GPU/kernel optimization tasks.
- Link: https://github.com/algorithmicsuperintelligence/openevolve
