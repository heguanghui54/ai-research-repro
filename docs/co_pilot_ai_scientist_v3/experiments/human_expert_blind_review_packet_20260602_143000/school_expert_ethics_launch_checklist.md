# School/NUS Expert Review Ethics And Launch Checklist

This checklist is coordinator-facing. It is designed for a minimal-risk blind
expert evaluation of regenerated ML/AI mini-paper artifacts.

## Before Recruitment

- Identify whether the work is intended for publication or public research
  dissemination. If yes, treat it as human-participant research until the
  institution says otherwise.
- Ask the relevant school, department, supervisor, DERC, IRB, or ethics office
  whether the study requires review or an exemption determination.
- Prepare the reviewer information sheet, consent/privacy note, recruitment
  email, instructions, score sheet, and anonymized A/B artifacts.
- Do not self-declare exemption in the paper or repository.
- Do not recruit students over whom the author has grading, employment, or
  supervisory power.
- If compensation or gift cards are used, record the policy and amount before
  recruitment.

## During Collection

- Use anonymized reviewer IDs such as R1, R2, and R3.
- Keep the condition keys hidden until all planned ratings are collected or the
  preregistered stopping rule is reached.
- Store completed CSVs separately from the reviewer-visible packet.
- Collect only the fields needed for the study: scores, winner, rationale, and
  optional expertise category.

## After Collection

- Validate each CSV with `scripts/summarize_human_expert_blind_reviews.py`.
- Report aggregate scores only.
- If a reviewer asks to withdraw before analysis, remove their rows and record
  the exclusion without naming them.
- Do not claim independent human evidence until at least the preregistered
  minimum number of valid expert rows has been collected.
