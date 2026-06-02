# Original Paper: Forked Diffusion for Conditional Graph Generation

- Paper ID: `openreview_sample_2`
- Venue/source: `ICLR_cc_2024_Conference`
- arXiv: `not available`
- Decision: `False`
- Mean score: `0.3`

## Abstract Excerpt

We introduce a novel score-based diffusion framework that incorporates forking for conditional generation. In this framework, a single  parent diffusion process is associated with a primary variable (e.g., structure), while multiple child diffusion processes are employed, each dedicated to a dependent variable (e.g., property). The parent process guides the co-evolution of its child processes towards segregated representation spaces. This approach allows our models to manage conditional information flow effectively, uncover intricate interactions and dependencies, and ultimately unlock new generative capabilities. Our experimental results demonstrate the significant superiority of our method over contemporary baselines in the context of conditional graph generation, highlighting the potential of forking diffusion for enhancing conditional generation tasks and inverse molecular design tas

## Decision Excerpt

The paper proposes a conditional generative model with a parent diffusion process for the graph structure and child processes for propertis. The intention is allowing better control over conditional generation. The method is evaluated on tasks like molecular graph generation and the paper shows improved performance over baselines.

Strengths:
- A rigorous matematical framework based on stochastic differential equations.
- It demonstrates versatility through evaluations on multiple graph generation tasks.

Weaknesses:
- In problem formulation the motivation, assumptions,  and comparison to related works are a little unclear. It does not clearly highlight shortcomings of existing methods to co
