# Human Co-Pilot Trace Dataset Protocol

This artifact answers whether the paper needs human co-pilot usage data.
Yes: the central claim concerns human scientific taste and insight at
creative or high-leverage decision nodes, so the paper needs trace data
showing where human decisions entered the research loop and what happened
afterward.

## Public Dataset Survey

| Dataset | Useful signal | Why it is insufficient for this paper |
| --- | --- | --- |
| [CoAuthor](https://p-lambda.github.io/coauthor/) | human-AI collaborative writing interactions | not scientific co-pilot research trajectories with benchmark execution |
| [CUPID](https://cupid.kixlab.org/) | human-curated multi-turn preference interaction histories | preference inference benchmark, not human scientific taste gates |
| [neulab/agent-data-collection](https://huggingface.co/datasets/neulab/agent-data-collection) | agent trajectories across web, code, household, knowledge, and software tasks | broad agent corpus, not AI Scientist-v2-style co-pilot research logs |
| [WebChain](https://huggingface.co/datasets/webagentlab/WebChain) | human-annotated web interaction trajectories | web/GUI task trajectories, not scientific hypothesis-experiment-paper loops |

No surveyed public dataset directly provides human scientist co-pilot
interventions inside an AI Scientist-v2-style loop with linked hypotheses,
benchmark runs, code artifacts, claim audits, and manuscripts. Public
datasets should therefore be used as related work or auxiliary design
evidence, not as the primary empirical support for IGRE.

## Proposed Primary Dataset

Use the author's Codex research sessions as an author-in-the-loop trace
corpus, but only after deriving a privacy-preserving metadata layer. Raw
chat logs are not required for the public release. The released dataset
should include gate records, artifact paths, commit IDs, benchmark metrics,
manuscript revisions, and claim-audit outcomes.

## Current Derived Dataset Snapshot

- Gate records indexed: 52
- Records with attention cost: 35
- Records with taste/insight: 10
- Prospective matched packages: 4
- Git commits indexed for this package: 57

## What This Dataset Can Support

- Ecological validity: a real researcher used the co-pilot workflow while building the paper.
- Process claims: human gates can be inserted, logged, audited, and linked to artifacts.
- Case-study claims: human taste/insight can be represented as a high-variance search prior.
- Negative findings: some human-gated choices lose to autonomous baselines on short-budget metrics.

## What It Cannot Support Alone

- Population-level claims about all scientists.
- Average performance superiority over autonomous AI Scientist-v2.
- Top-conference empirical sufficiency without multi-task/multi-seed matched evaluation.
- Human attention efficiency unless timing is prospectively recorded.

## Release Rules

1. Remove credentials, private URLs, and personally identifying content.
2. Release derived event records before raw transcripts.
3. Preserve enough artifact links for reproducibility.
4. Mark operator-recorded timing separately from independent human-subject timing.
5. Treat the first release as a single-author longitudinal case study.

## Release Audit

Run:

```bash
python3 scripts/audit_human_copilot_trace_dataset.py
```

Current expected result: `pass`. The audit should find 4
public-dataset survey entries, 52 gate records,
4 prospective packages,
57 commit-index entries, 0 secret-pattern hits,
and 0 raw-log marker hits. This means the artifact is suitable as a
derived metadata case-study dataset, not as a raw chat-log release or
population-level human-subject dataset.
