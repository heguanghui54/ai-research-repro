# Prospective Matched-Budget Micro-Pilot Manuscript

Run ID: `prospective_matched_micro_pilot_20260602_000001`

## Question

Can Co-Pilot AI Scientist v3 produce a complete prospective matched-budget
evidence package with human gate logs, matched baseline metrics, a claim audit,
and a manuscript artifact?

## Method

We ran a controlled weighted Max-Cut micro-task on the SSH Ubuntu host. The
autonomous baseline used an alternating partition policy. The co-pilot variant
used a human-gated frontier-steering decision to select an inspectable
local-search repair policy. Both variants used the same generated graph
instances and the same brute-force optimum evaluator.

## Results

| Variant | Mean normalized score | Minimum normalized score |
| --- | ---: | ---: |
| Autonomous alternating baseline | 0.596214 | 0.290323 |
| Co-pilot selected local search | 0.984419 | 0.904762 |

Mean delta (co-pilot minus autonomous): `0.388205`.

## Claim

This micro-pilot supports only a narrow engineering claim: the repository can
now produce a non-synthetic prospective matched-budget package that passes the
package-shape audit. It does not prove that human gates improve paper quality
or that Co-Pilot AI Scientist v3 outperforms autonomous AI Scientist-v2.
