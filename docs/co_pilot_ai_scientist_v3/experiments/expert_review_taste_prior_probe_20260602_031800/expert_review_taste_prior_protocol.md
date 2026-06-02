# Expert-Review Taste Prior Protocol

This protocol uses public OpenReview human-review data as an offline proxy for
scientific taste and insight. It is a limited prior, not a replacement for live
human co-pilot participation.

## Dataset

- Dataset: [nhop/OpenReview](https://huggingface.co/datasets/nhop/OpenReview)
- Config/split: `default` / `train`
- Rows reported by Dataset Viewer statistics: `34638`
- Probe sample size: `160`

The useful fields are `reviews`, `decision`, `decision_text`, `mean_score`,
`mean_novelty`, `mean_correctness`, `mean_clarity`, `mean_impact`, and
`mean_reproducibility`.

## How To Use It In IGRE

1. Retrieve papers near a candidate research direction by title/abstract
   similarity or metadata filters.
2. Convert high-scoring accepted papers into positive taste exemplars:
   problem framing, novelty signals, clarity patterns, reproducibility cues,
   and reviewer-noted strengths.
3. Convert low-scoring or rejected papers into negative taste exemplars:
   weak motivation, missing ablations, unclear claims, insufficient evidence,
   and reviewer-noted weaknesses.
4. Inject the resulting exemplars into the `scientific_taste_prior` gate before
   expensive AI Scientist-v2 branch search.
5. Evaluate whether review-prior guidance improves manuscript quality under a
   matched budget against autonomous AI Scientist-v2 and unguided IGRE.

## Minimal Experiment

- Task: generate or revise manuscripts for the same archived experiment traces.
- Baselines: autonomous manuscript generation, IGRE without review prior, IGRE
  with OpenReview-derived taste prior.
- Metrics: model-review rubric, human expert review when available, claim
  calibration, clarity, novelty, reproducibility, and benchmark-result honesty.
- Leakage control: never retrieve reviews for the exact target paper; use
  temporal and topic splits when training or selecting exemplars.

## Claim Boundary

This dataset can support the claim that public expert-review corpora can be
operationalized as an offline scientific-taste prior. It cannot by itself prove
that live human co-pilot participation improves research quality.
