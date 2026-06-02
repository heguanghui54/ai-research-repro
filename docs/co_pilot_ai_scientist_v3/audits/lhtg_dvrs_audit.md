# Long-Horizon Taste Gate / DVRS Audit

- Audit date: `2026-06-02T11:03:53Z`
- Status: `pass_with_no_positive_dvrs`
- Method terms present: `True`
- TFR status: `pass_with_negative_delayed_value_evidence`
- Delayed-value positive cases: `0`

## Candidate Queue

- Reviews screened: `473`
- Papers screened: `160`
- Delayed-value replay candidates: `120`
- Candidate rate: `0.2537`
- Long-horizon positive candidates: `84`
- Short-term repair signals: `90`

## Candidate Frontier Validation

- Attempted reviews: `16`
- Scored reviews: `13`
- Delayed-candidate mean review signal: `0.24`
- Control mean review signal: `0.176`
- Delayed minus control mean score: `0.064`

## Validated Negative Evidence

- Citation delayed-value cases: `0`
- Citation short-term-positive/long-term-negative cases: `3`
- Review-frontier latent delayed-value candidates: `0`
- Semantic latent delayed-value candidates: `0`
- Semantic winner counts: `{'paper_context': 4, 'review_guided_artifact': 1}`

## Errors

- None

## Warnings

- No positive delayed-value review signal has been validated yet

## Claim Boundary

LHTG/DVRS is operationalized as a routing and replay policy, but the current archived evidence validates only candidate prioritization and negative/weak TFR boundaries. It does not prove that human reviews improve long-horizon discovery.
