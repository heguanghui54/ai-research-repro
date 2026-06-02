# Frontier Alignment Vector Graph Protocol

## Purpose

Frontier Alignment Vector Graph (FAVG) is the frontier-aware evaluation layer
used by IGRE. It quantifies how a human-guided or review-guided regeneration
changes the relationship between an original research artifact and later or
current frontier evidence. The goal is not to prove that a regenerated artifact
already equals a frontier paper. The goal is to measure whether the intervention
changes the research trajectory in a direction that is worth further testing.

FAVG is motivated by the delayed-value setting: a human review or taste gate can
hurt immediate benchmark or manuscript scores while still moving the work
toward a later important direction. A single short-term score cannot reveal this
case.

## Objects

For each replay or regeneration case, FAVG defines:

- `o`: the original paper or starting research artifact.
- `r`: a raw review-guided regeneration.
- `g`: a gate-optimized regeneration, such as a six-gate IGRE artifact.
- `f`: a frontier centroid built from later field evidence or a current
  frontier taxonomy.

All objects are mapped into the same interpretable frontier-coordinate space.
The current pilot uses six dimensions:

1. alignment, safety, and reliability;
2. mechanistic or theoretical insight;
3. efficient systems and inference;
4. adaptive long-horizon search;
5. evaluation or benchmark shift;
6. deployment and social value.

## Metrics

FAVG reports complementary metrics rather than a single scalar:

- Direct frontier similarity gain: `cos(a, f) - cos(o, f)`.
- Frontier-direction projection: `dot(a - o, f - o) / ||f - o||`.
- Movement-direction cosine: `cos(a - o, f - o)`.
- Orthogonal novelty norm, or orthogonal novelty: the norm of the component of `a - o` orthogonal to
  `f - o`.

Here `a` can be any candidate artifact such as `r` or `g`.

These quantities answer different questions. Direct cosine asks whether the
artifact resembles the frontier centroid. Projection asks whether the
intervention moved the original work along the original-to-frontier direction.
Orthogonal novelty asks whether the intervention moved sideways into a
potentially novel but not-yet-frontier-aligned direction.

## Interpretation

FAVG separates four cases that are usually collapsed by ordinary manuscript
scores:

- short-term and frontier positive: the artifact improves local quality and
  moves toward frontier evidence;
- short-term positive but frontier ambiguous: the artifact reads better but
  changes the research direction in a mixed way;
- delayed-value candidate: the artifact may score worse locally but moves
  toward later or current frontier evidence;
- harmful intervention: the artifact scores worse and moves away from useful
  frontier directions.

Only the third case supports the paper's strongest claim about human scientific
taste as a long-horizon search signal, and even then it requires later evidence
or human expert validation.

## Current Pilot Instantiation

The current package implements FAVG in
`scripts/build_frontier_vector_graph.py`. The pilot builds the frontier centroid
from official ICLR, ICML, and ACL 2025 award-paper seed pages and applies the
metric to three deep OpenReview regeneration cases.

The current result is intentionally mixed. Six-gate artifacts have mean
projection gain `+0.1668` relative to raw review-guided artifacts, but mean
cosine gain `-0.0641`. This supports a diagnostic claim: vector evaluation
reveals directional ambiguity that internal review and lexical frontier scores
hide. It does not prove that six-gate regeneration is generally better than
raw review guidance.

## Reproduction

```bash
python3 scripts/build_frontier_alignment_taxonomy.py
python3 scripts/build_frontier_vector_graph.py
python3 scripts/build_frontier_metric_disagreement.py
python3 scripts/audit_frontier_alignment_vector_graph.py
```

## Claim Boundary

FAVG is a measurement protocol for trajectory movement. It is not a reward
model, not a replacement for expert review, and not a claim that a generated
paper has achieved SOTA. Strong claims require either successful temporal
frontier replay against later field evidence or independent expert judgement
that the vector movement reflects a genuinely promising research direction.
