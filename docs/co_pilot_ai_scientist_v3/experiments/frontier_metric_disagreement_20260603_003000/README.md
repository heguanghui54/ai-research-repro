# Frontier Metric Disagreement

This diagnostic compares short-term/internal review wins with lexical and vector-frontier wins on the three deep regeneration cases.

- Case count: `3`
- Disagreement cases: `2`
- Disagreement rate: `0.6667`

## Metric Win Counts

| Metric | Six-gate wins | Raw wins | Ties |
| --- | ---: | ---: | ---: |
| `internal_review` | 3 | 0 | 0 |
| `lexical_frontier` | 3 | 0 | 0 |
| `vector_projection` | 2 | 1 | 0 |
| `frontier_cosine` | 1 | 2 | 0 |

## Per-Case Matrix

| Case | Internal delta | Lexical delta | Projection delta | Cosine delta | Disagreement |
| --- | ---: | ---: | ---: | ---: | --- |
| `openreview_sample_1` | 1.6 | 4.65 | -2.0466 | -0.0671 | `True` |
| `openreview_sample_17` | 0.2 | 3.45 | 0.2644 | 0.0258 | `False` |
| `openreview_sample_2` | 1.6 | 2.3 | 2.2825 | -0.1511 | `True` |

## Boundary

This is a three-case diagnostic over regenerated mini-artifacts. It supports the need for multi-metric frontier-aware evaluation, not a general claim that six-gate regeneration is superior.
