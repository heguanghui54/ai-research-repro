# Contributing

Thank you for improving Co-Pilot AI Scientist v3.

This project welcomes contributions that make the IGRE six-gate workflow more
usable, auditable, and transferable.

## Good Contributions

- New task examples with complete gate logs.
- Better templates for gate records, claim audits, or evaluator-stress tests.
- Small benchmark examples that can be run cheaply.
- Documentation that makes installation easier.
- Validation scripts that catch unsupported claims or malformed gate logs.

## Contribution Rules

1. Do not add fabricated benchmark numbers.
2. Do not present model-only reviews as human expert evidence.
3. Keep scientific claims narrower than the evidence.
4. Preserve the six gate names unless proposing a clearly justified extension.
5. Include at least one reproducible example or validation command for new
   workflow features.

## Suggested Pull Request Checklist

- [ ] The change keeps the engineering/science evidence boundary clear.
- [ ] `python3 scripts/validate_release.py` passes.
- [ ] Any new gate example includes `attention_cost` and `taste_insight`.
- [ ] Any benchmark result includes logs or a reproducible evaluator.
- [ ] Any paper-quality claim says whether the reviewer was human or model-only.

## Adding A New Gate Example

Add a file under `examples/` and include:

- task ID;
- gate type;
- options considered;
- decision and rationale;
- attention cost;
- taste/insight record;
- downstream check.

## Adding A New Benchmark Example

Keep it small and honest. The preferred shape is:

- starter artifact;
- evaluator;
- direct baseline;
- gate decision;
- result summary;
- claim boundary.
