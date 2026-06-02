# Migrating From `ai-scientist-v2` To Co-Pilot AI Scientist v3

Co-Pilot AI Scientist v3 is not a replacement for the base `ai-scientist-v2`
Codex skill. It is an IGRE extension of that skill. Keep the original
research-production loop intact, then insert human-insight gates only where
human taste, evaluator skepticism, or claim responsibility can change a
research-control decision.

## Base Loop Mapping

| `ai-scientist-v2` step | Keep from the base skill | IGRE extension | What to log |
| --- | --- | --- | --- |
| Frame the research problem | Concrete question, success criteria, failure criteria, venue bar | Add a `scientific_taste_prior` gate if the user changes what is worth pursuing | Why this question has depth, novelty, failure value, or asymmetric upside |
| Generate multiple candidate ideas | Diverse hypotheses, risks, minimal experiments, expected metrics | Use AI Co-Scientist-style generate/critique/rank, then let a human select, merge, or reject directions | Candidate options, human decision, rationale, expected upside, possible harm |
| Search literature and remove duplicates | Academic search, novelty checks, benchmark papers | Use reviews or expert comments to identify overlooked mechanisms or stale framing | Prior-work conflicts, review-derived insight, unresolved novelty risk |
| Discover benchmarks and evaluation targets | Benchmarks, baselines, metrics, setup feasibility | Trigger `evaluator_stress_test` before trusting any metric | Metric-gaming risks, missing baselines, leakage, robustness gaps |
| Design experiments | Baselines, ablations, robustness checks, failure analysis | Route high-uncertainty branches through `frontier_steering` | Why a non-best early branch may deserve budget |
| Run and score candidates | Logs, metrics, artifacts, failed branches | Trigger `verifiable_micro_evolution` only for machine-gradeable subproblems | Evaluator, search budget, correctness checks, best program, failure cases |
| Write the paper | Draft from actual logs and citations | Trigger `structured_feedback` before polishing | Concrete revision actions rather than generic approval |
| Review and revise | Remove unsupported claims and weak figures | Trigger `claim_calibration` before final PDF | Supported, partially supported, unsupported, and overstated claims |

## Operating Rule

Run the base AI Scientist-v2 loop first. Add an IGRE gate only when it changes
one of these control decisions:

- which candidate direction receives budget;
- whether a benchmark or evaluator is trustworthy;
- whether a branch should continue despite weak early metrics;
- whether a subproblem should escalate to OpenEvolve-style search;
- whether feedback changes the scientific artifact rather than only prose;
- whether the manuscript claim boundary should be narrowed.

If the gate does not change a control decision, record it as ordinary feedback,
not as evidence that human participation improved the research trajectory.

## What Not To Change

Do not weaken the base `ai-scientist-v2` non-negotiables:

- do not invent results, citations, or benchmark numbers;
- prefer narrow, defensible claims over broad claims;
- compare multiple candidate directions when feasible;
- keep the best direction only after evidence supports it;
- make the final paper match the experiment log.

IGRE adds human scientific taste to the loop, but it also makes human decisions
auditable. Human participation is a high-variance search operator, not a
guaranteed improvement.
