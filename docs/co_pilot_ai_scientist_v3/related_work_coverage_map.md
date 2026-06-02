# Related Work Coverage Map

This map records the major research lines that the Co-Pilot AI Scientist v3
paper must cover, the role each line plays in the argument, and the boundary
that prevents IGRE from reading like a collage of prior systems.

## Coverage Summary

| Line | Representative works | Role in IGRE | Distinction made in this paper |
| --- | --- | --- | --- |
| End-to-end automated scientists | The AI Scientist; AI Scientist-v2; AI Co-Scientist | Defines the automated research loop: idea generation, experiment execution, paper writing, hypothesis debate, and evidence organization | IGRE does not remove the scientist; it turns human scientific taste into logged search-control gates |
| Scientific discovery agents beyond ML | Coscientist; ChemCrow; LLMatDesign; materials-discovery and chemistry agents | Shows that agentic science extends beyond ML paper writing into tool use, lab planning, and domain workflows | IGRE is a participation-mode layer, not a chemistry, materials, or wet-lab automation stack |
| Program search and algorithm discovery | AlphaTensor; AlphaDev; FunSearch; AlphaEvolve; OpenEvolve | Provides the machine-gradeable deep-search operator used in the verifiable micro-evolution gate | IGRE uses program evolution only when the subproblem has a reliable evaluator and a direct-edit baseline is insufficient |
| Schmidhuber self-referential learning line | 1987 self-referential learning; OOPS; Gödel Machine; POWERPLAY; Darwin Gödel Machine; Huxley-Gödel Machine | Supplies the older self-improvement discipline of ordered program search, self-modification, verification, archive growth, and competence preservation | IGRE does not optimize the agent's whole source code; it evolves bounded research artifacts, evaluators, subproblem programs, and claim policies under human-insight gates |
| LLM-guided evolution and reflection | PromptBreeder; EvoPrompting; LLMs as evolution strategies; Evolution of Heuristics; ReEvo; multi-objective heuristic evolution; Reflexion; Self-Refine; Voyager; AutoGen | Shows that LLMs can act as mutation operators, reflective critics, skill-library builders, and multi-agent coordinators | IGRE evolves the research trajectory and participation policy, not only prompts, heuristics, or the agent scaffold |
| Research-agent benchmarks | MLAgentBench; MLE-bench; FML-bench; PaperBench; AIRS-Bench; RExBench; ReplicationBench; SciVisAgentBench | Defines the external evaluation landscape for ML experimentation, research engineering, paper replication, research extensions, and scientific data analysis | IGRE argues that co-pilot claims need matched trajectories and paper-quality review, not only average benchmark score |
| Human feedback and peer review | OpenReview dataset; blind expert review protocol; review-utility map | Provides a public proxy for human scientific taste, insight, and claim-boundary judgement | OpenReview is offline asynchronous review data, not a live co-pilot trace; it supports participation-mode design, not population-level claims |

## Why This Matters

The paper's method is not "AI Co-Scientist plus AI Scientist-v2 plus
AlphaEvolve." Those systems inspire separate pressures, but IGRE renames and
reorganizes the workflow around a different research question: when should
human taste reshape automated scientific search, and how can that intervention
be audited?

The important abstraction is the gate, not the borrowed component. A gate is a
typed intervention that can change the research prior, evaluator, frontier,
subproblem search, feedback structure, or claim boundary. Each gate records
attention cost, rationale, affected artifact, and downstream outcome. This is
what separates IGRE from generic co-pilot approval, autonomous paper generation,
and whole-agent self-modification.

## Benchmark Implications

Recent research-agent benchmarks strengthen the paper's conservative claim
boundary. PaperBench evaluates whether agents can replicate ICML papers from
scratch and reports that frontier agents remain far below full human
replication competence. AIRS-Bench covers the full ML research lifecycle with
tasks sourced from SOTA papers. RExBench evaluates whether coding agents can
implement realistic research extensions. ReplicationBench and SciVisAgentBench
extend the evaluation picture to astrophysics replication and scientific
visualization workflows. These benchmarks imply that a top-conference claim
about co-pilot automated science should eventually be tested on realistic
research-engineering and replication tasks, not only on small paper-generation
or program-search probes.

The current package therefore keeps a strict boundary: it demonstrates a
reproducible workflow, gate routing, OpenReview-derived taste proxies,
OpenEvolve-style micro-search, and pilot matched trajectories. It does not yet
prove top-conference-level empirical superiority over autonomous AI Scientist-v2.

## Citation Seed Links

- The AI Scientist: https://arxiv.org/abs/2408.06292
- AI Scientist-v2: https://arxiv.org/abs/2504.08066
- AI Co-Scientist: https://arxiv.org/abs/2502.18864
- AlphaEvolve: https://arxiv.org/abs/2506.13131
- OpenEvolve: https://github.com/algorithmicsuperintelligence/openevolve
- Schmidhuber 1987 self-referential learning: https://people.idsia.ch/~juergen/diploma1987ocr.pdf
- Gödel Machine: https://arxiv.org/abs/cs/0309048
- POWERPLAY: https://arxiv.org/abs/1112.5309
- Darwin Gödel Machine: https://arxiv.org/abs/2505.22954
- Huxley-Gödel Machine: https://arxiv.org/abs/2510.21614
- PaperBench: https://arxiv.org/abs/2504.01848
- AIRS-Bench: https://arxiv.org/abs/2602.06855
- RExBench: https://huggingface.co/papers/2506.22598
- ReplicationBench: https://arxiv.org/abs/2510.24591
- SciVisAgentBench: https://arxiv.org/abs/2603.29139
