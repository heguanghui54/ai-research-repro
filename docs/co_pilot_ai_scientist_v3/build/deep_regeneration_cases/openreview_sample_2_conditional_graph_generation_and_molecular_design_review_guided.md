# Review-Guided Mini-Paper: Forked Diffusion for Conditional Graph Generation

## Source Paper

- Paper ID: `openreview_sample_2`
- Venue/source: `ICLR_cc_2024_Conference`
- arXiv: `not available`
- Original mean score: `0.3`

## Human Review Guidance Used

- The proposed method introduces forking as a new technique for conditional generation.
- The paper demonstrates versatility through evaluations on multiple graph generation tasks.

## Review Evidence Excerpts

### Review 1

{"clarity": 0.6666666666666666, "confidence": 0.75, "correctness": 0.3333333333333333, "ethics": null, "impact": 0.0, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper works on conditional graph generation via score-based generative model. Instead of directly input conditional properties as context to model inside generation, the paper proposes to use a separate variable to model each conditional property and jointly model them inside the score-based diffusion framework. The author tested it over many real-world datasets, including molecular datasets and generic graphs. The proposed method shows better p

### Review 2

{"clarity": 0.3333333333333333, "confidence": 0.5, "correctness": 0.3333333333333333, "ethics": null, "impact": 0.3333333333333333, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This paper proposes a forked diffusion model for conditional graph generation that introduces parent process and child processes to learn and generate graphs with desired properties. The contributions of this paper include introducing forking as a new technique for conditional generation, providing a rigorous mathematical framework using SDE, and demonstrating the versatility of the proposed forked diffusion with empirical evidence.", "

### Review 3

{"clarity": 0.3333333333333333, "confidence": 0.5, "correctness": 0.6666666666666666, "ethics": null, "impact": 0.3333333333333333, "novelty": null, "reproducibility": null, "review": {"limitations": null, "main_review": null, "paper_summary": "paper_summary: This work presents conditional diffusion framework for graph generation by proposing forked diffusion processes, that models the graph diffusion process as a single parent process over a primary variable (i.e., structure) and multiple child processes over dependent variables, further including additional context. This work provide experimental results on diverse graph generation tasks showing improved generation performance over continu

## Paper-Only Baseline Artifact

**Core contribution:** This paper introduces a novel score-based diffusion framework that employs forking for conditional graph generation.

**Experiment plan:** We will evaluate the proposed method on various graph generation tasks, comparing its performance against contemporary baselines to assess its effectiveness.

In this paper, we present a novel score-based diffusion framework that incorporates forking for conditional graph generation. Our approach utilizes a parent diffusion process associated with a primary variable, while multiple child processes are dedicated to dependent variables. This structure allows for effective management of conditional information flow and uncovers intricate interactions. We plan to evaluate our method across various graph generation tasks, comparing its performance against contemporary baselines. However, we acknowledge that the clarity of our problem formulation and underlying assumptions may affect the understanding of our approach. The claims made are specifically relevant to conditional graph generation and may not extend to other domains.

## Human-Review-Guided Artifact

**Core contribution:** This work proposes a forked diffusion model that enhances conditional graph generation by introducing parent and child processes to learn and generate graphs with desired properties.

**Method sketch:** The forked diffusion model uses a parent process for the primary variable and child processes for dependent variables, leveraging a rigorous mathematical framework based on stochastic differential equations.

**Experiment plan:** We will conduct experiments on diverse graph generation tasks, including molecular datasets, to validate the effectiveness of the forked diffusion model against existing methods.

**Limitations:** The motivation and comparison to related works are not clearly articulated, which may hinder the understanding of the proposed method's advantages.

**Claim boundary:** The findings are primarily relevant to conditional graph generation and may not generalize to other types of generative models.

In this work, we introduce a forked diffusion model for conditional graph generation, which enhances the learning and generation of graphs with desired properties. Our approach employs a parent diffusion process for the primary variable and multiple child processes for dependent variables, providing a rigorous mathematical framework based on stochastic differential equations. We plan to validate our method through experiments on diverse graph generation tasks, including molecular datasets, comparing its performance against existing methods. However, we recognize that the motivation and comparison to related works could be articulated more clearly. The claims made in this paper are primarily relevant to conditional graph generation and may not extend to other generative modeling contexts.

## Short-Term Review Scores

### gpt-4o-mini

- Winner: `review_guided`
- Context-control overall: `3`
- Review-guided overall: `4`
- Specific review value: The review-guided version introduces a novel technique and emphasizes the versatility of the method across multiple tasks, improving the framing.

### claude-3-7-sonnet-latest

- Winner: `review_guided`
- Context-control overall: `3`
- Review-guided overall: `3`
- Specific review value: The review insight about unclear motivation and comparison to related works surfaces a genuine limitation that the context_control misses entirely. This improves limitation honesty marginally. The SDE mathematical framework mention adds some methodological specificity.

## Later-Frontier Evidence

- Citation-frontier winner: `not_scored_no_frontier_terms`
- Citation temporal pattern: `mixed_or_tie`
- Semantic-frontier winner: `None`
- Latent delayed-value candidate: `None`
- Frontier terms: ``

## Evidence Boundary

This PDF displays a concrete human-review-guided mini-paper artifact from the current pilot. It is not yet a full benchmark-executed deep reproduction.
