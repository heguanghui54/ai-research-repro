# Co-Pilot AI Scientist v3 Submission Card

## Identity

- Title: Co-Pilot AI Scientist v3: Insight-Gated Research Evolution for Collaborative Automated Science
- Author record: He Shi, School of Computing, National University of Singapore
- Package status: reproducible artifact pipeline delivered; top-conference empirical sufficiency not yet reached
- Primary method: Insight-Gated Research Evolution (IGRE)
- Long-horizon extension: Long-Horizon Taste Gate (LHTG) with Delayed-Value Review Signal (DVRS)

## One-Sentence Contribution

Co-Pilot AI Scientist v3 turns human participation in automated science into logged, auditable gates that use scientific taste and insight to steer AI Scientist-v2-style generation, AI Co-Scientist-style debate, and OpenEvolve-style verifiable search toward better-calibrated research trajectories.

## What Is New Here

This package is not a direct combination of prior co-scientist, autonomous-paper, or program-search systems. IGRE names and evaluates a participation pattern designed for this paper: human scientists do not simply approve or edit outputs, but intervene at five explicit gates.

1. Scientific taste prior: decide which research directions deserve scarce compute even when short-term metrics are uncertain.
2. Evaluator stress gate: test whether a benchmark or reward can be gamed before trusting it.
3. Frontier steering gate: redirect search toward later-field relevance and neglected high-upside questions.
4. Verifiable micro-evolution gate: use OpenEvolve-style loops only on machine-gradeable subproblems.
5. Claim calibration gate: prevent the paper from claiming more than the evidence supports.

LHTG/DVRS adds a retrospective version of this idea: some review comments may look weak under short-term paper scores but become valuable if they align old research trajectories with later frontier developments.

## Evidence Snapshot

- Review utility map: 473 OpenReview snippets screened; 398 contain actionable gate signals.
- Gate-structure ablation: full gate pattern scores 1.000 versus best single gate 0.369 and random 0.199.
- Held-out gate validation: full pattern 1.000 versus best single gate 0.374.
- Gate-outcome attribution: full 75.17 versus best single gate 37.25.
- OpenReview regeneration: review-guided artifacts win 5/6 under one model scorer; cross-model review gives 3/6 wins, 1/6 baseline win, and 2 ties.
- Equal-context ablation: review-specific context wins 8 pairs versus 1 unrelated-review win and 3 ties.
- Candidate-frontier validation: 13/16 delayed-value candidates scored; delayed-control mean delta is +0.064.
- Boundary evidence: LHTG/DVRS has 0 positive delayed-value cases in the current small sample, and FML short-budget evidence remains mixed or negative.

## What Not To Claim Yet

- Do not claim that Co-Pilot AI Scientist v3 empirically outperforms autonomous AI Scientist-v2.
- Do not claim that human participation always improves paper quality.
- Do not claim that OpenReview feedback is live co-pilot interaction data.
- Do not claim that DVRS has already found positive high-tail delayed-value cases.

The defensible current claim is narrower: human taste and insight can be operationalized as auditable participation modes, historical review data can be used to design and stress-test these modes, and the present package identifies which evidence is still missing.

## External Verification

Run from the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/audit_long_horizon_taste_gate.py
python3 scripts/audit_temporal_frontier_replay.py
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 scripts/audit_objective_delivery.py
python3 scripts/audit_package_consistency.py
```

## Reviewer Reading Order

1. `docs/co_pilot_ai_scientist_v3/paper_en_focused.md`
2. `docs/co_pilot_ai_scientist_v3/audits/top_conference_readiness_audit.md`
3. `docs/co_pilot_ai_scientist_v3/audits/claim_evidence_audit.md`
4. `docs/co_pilot_ai_scientist_v3/audits/lhtg_dvrs_audit.md`
5. `skills/co-pilot-ai-scientist-v3/SKILL.md`

