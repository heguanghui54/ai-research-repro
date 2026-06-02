# IGRE Skill Engineering And Open-Source Release Strategy

## Motivation

The engineering objective of Co-Pilot AI Scientist v3 is not only to write a
paper. A successful outcome should also be a reusable research skill that other
researchers can install, run, audit, and adapt. The public success of
`academic-research-skills` shows that research-agent skills can become
community infrastructure when they are easy to install, clearly scoped, and
useful across many academic workflows.

`academic-research-skills` is an important reference point because it packages
literature review, writing, review, revision, citation checking, and integrity
checks into reusable modules. It also explicitly cites PaperOrchestra as one of
the inspirations for multi-agent paper-writing workflows. Co-Pilot AI
Scientist v3 should learn from that engineering model while keeping a distinct
scientific contribution: IGRE is a six-gate control theory for deciding when
human scientific taste should change the automated research search process.

This is a separate engineering task from the research-paper task. The paper may
mention the public skill as a reproducibility and transfer artifact, but the
paper's scientific claims should still be judged by experiments, blind review,
and benchmark evidence. Conversely, the GitHub skill should be optimized for
installability, usability, and community adoption even when those goals do not
directly add new scientific evidence.

## Product Claim

The public skill should be positioned as:

> A Codex skill for collaborative automated science: it turns human scientific
> taste, evaluator stress tests, frontier steering, micro-evolution decisions,
> structured feedback, and claim calibration into auditable gates inside an AI
> Scientist-v2-style research loop.

It should not be positioned as:

- a generic academic writing assistant;
- a humanizer;
- a fully autonomous AI scientist;
- proof that human intervention always improves paper quality;
- a replacement for `academic-research-skills`.

## Distinctive Features

1. **Six-gate workflow**
   - scientific-taste prior;
   - evaluator stress test;
   - frontier steering;
   - verifiable micro-evolution;
   - structured feedback;
   - claim calibration.

2. **Gate logs as research artifacts**
   - each intervention records gate type, rationale, evidence, expected upside,
     possible harm, attention cost, and downstream outcome.

3. **Evaluator-gaming protection**
   - the evaluator-stress gate can reject branches that win a primary metric
     through degenerate shortcuts.

4. **OpenEvolve-style escalation**
   - program search is triggered only for machine-gradeable subproblems where
     direct editing is insufficient or risky.

5. **Temporal Frontier Replay**
   - historical peer review can be replayed against later field evidence to
     study delayed-value human insight.

6. **Claim calibration**
   - the skill treats narrowing claims as a scientific contribution, not a
     cosmetic writing pass.

## Minimum GitHub Release Shape

The first public release should include:

- `skills/co-pilot-ai-scientist-v3/SKILL.md`;
- task-spec, gate-log, and claim-audit templates;
- a one-command validation script;
- a short quickstart with one toy task;
- an example gate trajectory;
- a warning that model reviews and model dry-runs are not human expert
  evidence;
- a paper package link;
- a roadmap for human expert blind review and matched benchmark runs.

## Repository Design Targets

To be competitive with high-adoption academic skill repositories, the project
should optimize for:

- **installability**: a researcher can copy or install the skill without
  reading the whole paper;
- **visible value in 10 minutes**: the first run should produce a gate log and
  claim audit quickly;
- **trust**: every output has provenance, claim boundaries, and explicit
  unsupported-claim warnings;
- **modularity**: users can run only the gate they need;
- **community extension**: new gates, benchmarks, and review rubrics can be
  contributed without rewriting the whole system;
- **bilingual documentation**: English for the research artifact, Chinese for
  author-side review and adoption support.

## Release Milestones

| Milestone | Deliverable | Evidence |
| --- | --- | --- |
| R0 internal skill | Current Codex skill in this repository | `skills/co-pilot-ai-scientist-v3/SKILL.md` and smoke audit |
| R1 reproducible package | README, quickstart, templates, validator, example trajectory | clean clone and skill reuse smoke |
| R2 public GitHub skill repo | Standalone repo with install instructions and examples | pushed release branch or public repo |
| R3 community validation | external users run the skill on new topics | issue/PR/example logs, with privacy protection |
| R4 paper-grade engineering evidence | multiple researchers' anonymized gate traces | consented multi-user trace dataset |

## First Public README Outline

1. What problem this skill solves.
2. Why human-in-the-loop is not enough; why gates are needed.
3. Install.
4. Quickstart.
5. The six gates.
6. Example run.
7. Evidence and limitations.
8. Relation to AI Scientist, AI Co-Scientist, AlphaEvolve/OpenEvolve,
   PaperOrchestra, and academic-research-skills.
9. Contributing new gates or benchmarks.

## Evidence Boundary

GitHub stars or community adoption would be engineering-impact evidence, not
scientific proof of co-pilot superiority. The paper should treat a successful
public skill release as evidence that IGRE is usable and transferable, while
matched benchmark runs and blind expert review remain necessary for scientific
performance claims.
