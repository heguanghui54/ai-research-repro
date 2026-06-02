# Human Expert Rating Collection Protocol

## Goal

Collect blind human expert ratings for the six OpenReview regeneration pairs.
This is intended to replace model-routed review as the strongest evidence for
whether paper-specific expert review text improves regenerated research
artifacts beyond equal amounts of unrelated review context.

## Target Raters

- 3 to 5 raters with ML/AI paper-reading experience.
- Raters should not see `condition_key.json`.
- Raters should be asked to spend about 20 to 40 minutes total.

## Materials

Send each rater only:

- `reviewer_index.md`
- `instructions.md`
- `pairs/pair_01.md` through `pairs/pair_06.md`
- `score_sheet_template.csv`

Do not send:

- `condition_key.json`
- `pairs.json`
- any model-review summaries.

## Collection Steps

1. Assign each rater an anonymized ID such as `R1`, `R2`, or `R3`.
2. Ask the rater to fill every score column with integers from 1 to 5.
3. Ask the rater to set each `winner` to `A`, `B`, or `tie`.
4. Store completed CSVs outside the reviewer-visible packet until all are
   collected.
5. Concatenate all completed rows into one CSV.
6. Run:

```bash
python3 scripts/summarize_human_expert_blind_reviews.py \
  --packet-dir docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000 \
  --score-csv path/to/completed_human_scores.csv
```

## Required Reporting

Report:

- number of raters,
- number of valid rows,
- condition win counts,
- condition mean scores,
- review-guided minus comparator mean delta with bootstrap CI,
- Fleiss' kappa over A/B/tie winner choices when at least two raters completed
  the same pairs,
- short qualitative themes from rationales.

## Claim Boundary

The packet itself is not evidence. Only completed independent ratings can be
reported as human expert evaluation.
