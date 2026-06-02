# Focused Paper Quality Review Summary

Review date: 2026-06-03

Manuscript reviewed:

- `docs/co_pilot_ai_scientist_v3/paper_en_focused.md`

Reviewer routes:

- Monica OpenAI-compatible `gpt-4o-mini`
- Monica OpenAI-compatible `gemini-2.5-flash`
- Monica OpenAI-compatible `claude-3-7-sonnet-latest` attempted but returned
  `504 Gateway Time-out`; logged but not counted as a successful review.
- Monica OpenAI-compatible `gemini-2.0-flash` attempted earlier but returned an
  unsupported-model `412`; logged but not counted as a successful review.

## Aggregate Verdict

The refreshed focused review includes the three-case live Temporal Frontier
Replay aggregate, the deterministic TFR audit, the focused reference audit with
the Schmidhuber/OOPS/Godel Machine/POWERPLAY self-improvement lineage, and the
new research-skill/manuscript-copilot related-work line that treats
PaperOrchestra as a multi-agent paper-writing theory source for skill bundles
such as `academic-research-skills`, alongside
`Claude-Code-Skills-for-Academics`.

Both successful model reviewers recommend weak accept under conservative
framing. They agree that IGRE is most defensible as a systems-method and
measurement paper: it operationalizes human scientific taste as auditable
control signals, releases a reproducible artifact package, and reports mixed
or negative evidence rather than claiming broad superiority. The remaining
top-conference gap is still empirical, not cosmetic: independent human expert
ratings, larger matched trajectories, broader benchmarks, and stronger
delayed-value evidence are still missing.

| Reviewer | Recommendation | Novelty | Rigor | Clarity | Evidence | Reproducibility | Significance |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | Weak accept | 4 | 3 | 4 | 3 | 4 | 3 |
| `gemini-2.5-flash` | Weak accept | 4 | 5 | 5 | 4 | 5 | 4 |

## What Improved

- The related-work section now separates manuscript-copilot skill bundles from
  autonomous discovery systems, identifies PaperOrchestra as a theory source
  for `academic-research-skills`, and positions IGRE as a gate-control theory
  rather than another writing pipeline.
- The paper explicitly includes the Schmidhuber self-referential learning and
  code self-improvement lineage, including OOPS, Godel Machine, POWERPLAY,
  Darwin Godel Machine, and Huxley-Godel Machine.
- Three live four-condition TFR cases are now included. They do not provide
  strict delayed-value positives, but they demonstrate that preregistered rules
  can correct optimistic model-judge labels and expose weak gate propagation.
- The main contribution is now clearer: useful human participation is not more
  review context, but targeted routing of human taste and insight into research
  priors, evaluators, frontiers, micro-evolution tasks, feedback structures, and
  claim boundaries.
- The manuscript is more honest about high variance: human participation can
  hurt short-budget benchmark outcomes while still being worth studying for
  high-tail or long-horizon scientific-search effects.

## Remaining Blocking Issues

- The primary empirical evidence remains mixed or negative for broad
  human-gated superiority.
- The three live TFR replays produce zero strict delayed-value positives under
  preregistered deterministic rules.
- Regenerated artifact comparisons still rely mainly on model-routed scoring;
  the preregistered blind human expert packet has zero completed human rows.
- The OpenReview-derived taste/insight classifier is not yet validated against
  independent expert labels.
- Benchmark coverage and matched-budget sample size remain too narrow for a
  strong systems claim.
- The paper is now better positioned, but still needs one larger decisive
  empirical block to move from strong pilot to top-conference-ready evidence.

## Next Required Evidence

1. Collect blind human expert ratings for the prepared paired artifacts and
   report inter-rater agreement.
2. Run larger matched autonomous versus human-gated trajectories across tasks,
   seeds, and domains.
3. Validate OpenReview taste/insight routing against independent expert labels.
4. Scale TFR beyond three cases and use semantic frontier metrics plus human
   expert assessment to find or falsify delayed-value review signals.
5. Add real benchmark reruns where gate choices alter downstream experimental
   outcomes, not only regenerated text artifacts.
