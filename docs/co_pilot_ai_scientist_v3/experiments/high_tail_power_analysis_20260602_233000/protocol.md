# High-Tail Human-Participation Power Analysis

Run date: 2026-06-02T09:48:26Z

## Purpose

This protocol operationalizes the high-tail hypothesis in IGRE: human
scientific taste may increase the probability of rare frontier-quality
outputs even when average short-budget benchmark scores are mixed or
negative. The hypothesis is not that every human gate improves every
run. It is that a selected participation mode can increase the tail
probability of outcomes that pass a strict quality/frontier threshold.

## Tail Outcome Definition

A run is counted as a high-tail success only if it satisfies all of the
following preregistered conditions:

1. A blinded reviewer or fixed external evaluator marks the artifact as
   top-tier on the primary quality dimension.
2. The artifact passes the claim-calibration gate: its claims are supported
   by the evidence actually produced in the run.
3. The artifact is not a metric-gaming result under the evaluator-stress
   gate.
4. For TFR studies, the artifact is also closer to later field-frontier
   evidence than both paper-only and shuffled-review controls.

For the current paper package, no positive delayed-value high-tail cases
have been found. This analysis is therefore a planning artifact, not a
positive result.

## Statistical Test

The planned primary test is a one-sided Fisher exact test comparing the
high-tail success rate of human-gated/co-pilot runs against autonomous
runs under matched budgets. Ties and invalid runs are reported separately
and are not silently converted into wins.

## Monte Carlo Power Table

| Autonomous tail rate | Co-pilot tail rate | n per arm | Estimated power | Mean co-pilot successes | Mean autonomous successes |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.020 | 0.050 | 10 | 0.001 | 0.51 | 0.20 |
| 0.020 | 0.050 | 20 | 0.003 | 1.02 | 0.41 |
| 0.020 | 0.050 | 30 | 0.006 | 1.50 | 0.59 |
| 0.020 | 0.050 | 50 | 0.046 | 2.52 | 1.01 |
| 0.020 | 0.050 | 75 | 0.111 | 3.77 | 1.51 |
| 0.020 | 0.050 | 100 | 0.159 | 5.01 | 2.01 |
| 0.020 | 0.050 | 150 | 0.280 | 7.53 | 2.99 |
| 0.020 | 0.050 | 200 | 0.393 | 10.03 | 4.02 |
| 0.020 | 0.050 | 300 | 0.566 | 14.98 | 5.98 |
| 0.020 | 0.050 | 500 | 0.788 | 24.93 | 10.08 |
| 0.050 | 0.100 | 10 | 0.007 | 0.99 | 0.52 |
| 0.050 | 0.100 | 20 | 0.018 | 1.97 | 1.00 |
| 0.050 | 0.100 | 30 | 0.048 | 2.98 | 1.51 |
| 0.050 | 0.100 | 50 | 0.120 | 4.94 | 2.52 |
| 0.050 | 0.100 | 75 | 0.225 | 7.47 | 3.77 |
| 0.050 | 0.100 | 100 | 0.266 | 9.99 | 5.07 |
| 0.050 | 0.100 | 150 | 0.413 | 14.99 | 7.50 |
| 0.050 | 0.100 | 200 | 0.540 | 20.01 | 9.97 |
| 0.050 | 0.100 | 300 | 0.703 | 30.03 | 15.07 |
| 0.050 | 0.100 | 500 | 0.904 | 50.07 | 24.90 |
| 0.050 | 0.150 | 10 | 0.032 | 1.50 | 0.50 |
| 0.050 | 0.150 | 20 | 0.089 | 3.01 | 1.03 |
| 0.050 | 0.150 | 30 | 0.172 | 4.53 | 1.49 |
| 0.050 | 0.150 | 50 | 0.380 | 7.48 | 2.54 |
| 0.050 | 0.150 | 75 | 0.579 | 11.17 | 3.76 |
| 0.050 | 0.150 | 100 | 0.710 | 15.05 | 5.03 |
| 0.050 | 0.150 | 150 | 0.872 | 22.49 | 7.49 |
| 0.050 | 0.150 | 200 | 0.944 | 29.88 | 10.08 |
| 0.050 | 0.150 | 300 | 0.995 | 45.01 | 14.97 |
| 0.050 | 0.150 | 500 | 1.000 | 74.99 | 24.96 |
| 0.100 | 0.150 | 10 | 0.020 | 1.50 | 1.01 |
| 0.100 | 0.150 | 20 | 0.039 | 3.00 | 2.01 |
| 0.100 | 0.150 | 30 | 0.058 | 4.52 | 3.02 |
| 0.100 | 0.150 | 50 | 0.121 | 7.51 | 5.00 |
| 0.100 | 0.150 | 75 | 0.175 | 11.26 | 7.47 |
| 0.100 | 0.150 | 100 | 0.217 | 14.98 | 9.94 |
| 0.100 | 0.150 | 150 | 0.310 | 22.48 | 14.90 |
| 0.100 | 0.150 | 200 | 0.383 | 29.92 | 20.05 |
| 0.100 | 0.150 | 300 | 0.536 | 44.92 | 29.97 |
| 0.100 | 0.150 | 500 | 0.742 | 74.96 | 49.90 |
| 0.100 | 0.200 | 10 | 0.050 | 2.05 | 1.01 |
| 0.100 | 0.200 | 20 | 0.114 | 4.00 | 2.00 |
| 0.100 | 0.200 | 30 | 0.161 | 5.98 | 2.99 |
| 0.100 | 0.200 | 50 | 0.293 | 10.01 | 5.06 |
| 0.100 | 0.200 | 75 | 0.449 | 15.00 | 7.48 |
| 0.100 | 0.200 | 100 | 0.569 | 19.96 | 10.04 |
| 0.100 | 0.200 | 150 | 0.742 | 29.94 | 15.08 |
| 0.100 | 0.200 | 200 | 0.860 | 40.08 | 19.97 |
| 0.100 | 0.200 | 300 | 0.955 | 60.01 | 29.98 |
| 0.100 | 0.200 | 500 | 0.997 | 99.95 | 49.96 |

## Design Implication

Small six-paper OpenReview probes are useful for pipeline debugging but
are underpowered for a rare breakthrough-probability claim. If the
autonomous tail rate is 5% and human-gated participation raises it to
10%, the estimated sample size needed for roughly 80% power is recorded
in `summary.json` and is far larger than the current pilot. This is why
the focused paper must present high-tail participation as a future
study design unless independent large-scale data are collected.
