# Delayed-Value Replay Multicase Audit

- Audit date: `2026-06-02T19:08:06Z`
- Status: `pass_with_no_strict_positive_dvrs`
- Replay cases: `3`
- Same-model positive labels: `3`
- Strict positive DVRS cases: `0`
- Cross-model strict positive labels: `0`
- Cross-model frontier winner counts: `{'six_gate_hybrid_guided': 3}`

## Case Table

| Case | Same-model label | Strict label | Short-term winner | Frontier winner | Cross-model strict labels | Cross-model frontier winners |
| --- | --- | --- | --- | --- | --- | --- |
| `paper_105_review_1` | `positive` | `mixed_or_inconclusive` | `tie` | `tie` | `{'mixed_or_inconclusive': 1}` | `{'six_gate_hybrid_guided': 1}` |
| `paper_132_review_2` | `positive` | `mixed_or_inconclusive` | `tie` | `six_gate_hybrid_guided` | `{'mixed_or_inconclusive': 1}` | `{'six_gate_hybrid_guided': 1}` |
| `paper_37_review_1` | `positive` | `mixed_or_inconclusive` | `tie` | `six_gate_hybrid_guided` | `{'mixed_or_inconclusive': 1}` | `{'six_gate_hybrid_guided': 1}` |

## Strict Rule Diagnostics

### `paper_105_review_1`
- `{'condition': 'raw_review_guided', 'short_term_penalty': False, 'beats_paper_frontier': True, 'beats_shuffled_frontier': True, 'actionable': True, 'specific': True}`
- `{'condition': 'six_gate_hybrid_guided', 'short_term_penalty': False, 'beats_paper_frontier': True, 'beats_shuffled_frontier': True, 'actionable': True, 'specific': True}`
### `paper_132_review_2`
- `{'condition': 'raw_review_guided', 'short_term_penalty': False, 'beats_paper_frontier': True, 'beats_shuffled_frontier': True, 'actionable': True, 'specific': True}`
- `{'condition': 'six_gate_hybrid_guided', 'short_term_penalty': False, 'beats_paper_frontier': True, 'beats_shuffled_frontier': True, 'actionable': True, 'specific': True}`
### `paper_37_review_1`
- `{'condition': 'raw_review_guided', 'short_term_penalty': False, 'beats_paper_frontier': True, 'beats_shuffled_frontier': True, 'actionable': True, 'specific': True}`
- `{'condition': 'six_gate_hybrid_guided', 'short_term_penalty': True, 'beats_paper_frontier': True, 'beats_shuffled_frontier': True, 'actionable': False, 'specific': False}`

## Interpretation

The replay cases show useful frontier-routing diagnostics, especially six-gate frontier wins under Claude judges, but the strict preregistered DVRS rule finds no positive delayed-value case because the required short-term penalty/actionability/specificity pattern is not satisfied.

## Errors

- None

## Warnings

- paper_105_review_1 same-model judge positive but strict rule is mixed_or_inconclusive
- paper_132_review_2 same-model judge positive but strict rule is mixed_or_inconclusive
- paper_37_review_1 same-model judge positive but strict rule is mixed_or_inconclusive

## Claim Boundary

A pass means multiple four-condition replay cases and cross-model judges were aggregated under the strict delayed-value rule. It is model-scored replay evidence, not benchmark execution or human expert validation.
