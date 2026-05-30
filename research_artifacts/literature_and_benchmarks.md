# Literature And Benchmark Notes

## Anchors

- The AI Scientist v1 frames end-to-end automated research as idea generation, code, experiments, visualization, paper writing, and simulated review. It claims low-cost generated ML papers, but the key limitation for our project is quality/reproducibility control in open-ended loops.
- The AI Scientist-v2 removes human-authored code-template dependence, uses progressive agentic tree search, and includes VLM feedback for figures. This is the closest parent system and should be treated as the method baseline.
- MultiAgentBench evaluates multi-agent collaboration and reports that topology matters, including graph-style coordination in research scenarios. It is useful background, but it is not specialized to full AI research lifecycle artifacts.
- Self-evolving agents such as HexMachina show artifact-centric continual improvement in strategic environments. This motivates evolving research policies and executable artifacts rather than only prompt memories.
- AIRS-Bench is a 2026 full AI research lifecycle benchmark with 20 tasks from recent ML papers and no provided baseline code; it is the closest external benchmark to target after our pilot.
- AIRS-Bench also exposes official task definitions and evaluators in `facebookresearch/airs-bench`. We can import task metadata/project descriptions for planning-quality experiments, but official AIRS performance requires generated submissions and task-local evaluator execution.
- ScienceAgentBench is a strong cautionary baseline: it evaluates scientific data-discovery agents on 102 tasks and reports that even stronger agents solve only a minority of tasks independently.
- ResearchGym and FIRE-Bench reinforce the trend toward full-cycle research evaluation, fixed compute, and evidence-based insight rediscovery rather than paper-writing-only benchmarks.

## Candidate Benchmark Strategy

### Research Lifecycle Micro-Benchmark

Define 10 to 20 compact tasks, each containing:

- a seed research question,
- a short related-work packet,
- a toy executable environment or dataset,
- required outputs: hypothesis, experiment plan, runnable code/config, metrics table, limitations, and final short paper section.

Primary metrics:

- executable success rate,
- evidence-grounded claim rate,
- novelty calibration,
- reviewer score,
- token/cost-normalized score,
- reproducibility score from rerunning saved commands.

### External Benchmarks To Inspect Next

- AI Scientist-v2 repository tasks and generated-paper workflow.
- AIRS-Bench task definitions and evaluation code.
- ResearchGym fixed-compute tasks.
- FIRE-Bench insight rediscovery tasks.
- MultiAgentBench/MARBLE research scenarios.
- MLAgentBench, ScienceAgentBench, DiscoveryBench.

## Source Links

- AI Scientist-v2: https://arxiv.org/abs/2504.08066
- AI Scientist v1: https://arxiv.org/abs/2408.06292
- MultiAgentBench: https://huggingface.co/papers/2503.01935
- AIRS-Bench: https://arxiv.org/abs/2602.06855
- AIRS-Bench code: https://github.com/facebookresearch/airs-bench
- ScienceAgentBench: https://arxiv.org/abs/2410.05080
- ResearchGym: https://anikethh.github.io/ResearchGym/
- FIRE-Bench: https://arxiv.org/abs/2602.02905
- Agents of Change / HexMachina: https://arxiv.org/abs/2506.04651

## Baselines

- Single-agent sequential AI Scientist-style loop.
- Single-agent with reflection only.
- Multi-agent fixed roles: ideator, experiment manager, coder, reviewer, writer.
- Multi-agent with self-evolving artifact policy.

## Current Best Direction

The strongest first paper direction is **Artifact-Centric Self-Evolution for Autonomous AI Research Agents** because it is narrow, measurable, and clearly extends the AI Scientist-v2 setup without requiring massive compute.
