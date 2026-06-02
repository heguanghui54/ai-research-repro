# Online Form Builder Specification

This file describes how to turn the blind review packet into a Qualtrics,
Google Forms, Microsoft Forms, or REDCap-style form. It is coordinator-facing.

## Recommended Sections

1. Information and consent screen.
2. Reviewer metadata:
   - anonymized reviewer ID,
   - expertise category: faculty, postdoc, PhD student, master's student,
     advanced undergraduate researcher, other,
   - years reading ML/AI papers: 0-1, 2-4, 5+.
3. Main six text A/B pairs.
4. Optional three deep-case PDF A/B pairs.
5. Final free-text comment.

## Per-Pair Fields

For each pair, include:

- `winner`: A, B, tie.
- `A_problem_framing`: integer 1-5.
- `A_method_specificity`: integer 1-5.
- `A_experiment_design`: integer 1-5.
- `A_limitation_honesty`: integer 1-5.
- `A_claim_calibration`: integer 1-5.
- `A_overall_quality`: integer 1-5.
- The same six fields for B.
- `rationale`: short free text.

## Blinding Requirements

- Do not include `condition_key.json` or `deep_pdf_condition_key.json` in the
  form.
- Use only pair IDs and neutral Variant A/B labels.
- Randomize pair order if the form system allows it, but keep A/B labels fixed
  within each pair so the hidden key remains valid.
