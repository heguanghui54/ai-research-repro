# Human Evaluation Protocol

This packet supports a blinded human calibration study for the 20-task, three-seed AI-research workflow artifacts.

## Scope

- Sample size: 40 artifacts.
- Methods: `single_fixed` and `multi_fixed`.
- Task source: `research_artifacts/ai_research_tasks_20.json`.
- The annotation packet hides method and seed in the CSV shown to annotators.
- The key file maps blinded artifact IDs back to method, seed, task, and structural-rubric score.

## Annotation Task

For each artifact, read the task prompt and generated answer. Score the answer on 1-5 scales:

- `overall_quality`: research usefulness of the artifact.
- `scientific_validity`: whether claims are appropriately cautious and evidence-grounded.
- `claim_grounding`: whether claims are tied to concrete evidence or planned checks.
- `reproducibility`: whether another researcher could execute the proposed check.
- `novelty_calibration`: whether novelty and related-work risks are handled honestly.
- `overclaim_risk`: 1 means low overclaim risk; 5 means high overclaim risk.

Use `notes` for one concise reason. Annotators should not infer method identity from length alone; judge whether the content would actually help a researcher.

## Suggested Analysis

After annotation, join the completed CSV with `human_eval_key.csv`, then compute:

- mean human quality by method,
- paired single-vs-multi deltas by task and seed where both methods are present,
- human/model-judge correlation using `quality_primary_analysis.json`,
- disagreement cases for qualitative failure analysis.

## Local Annotation App

The packet includes a self-contained browser annotator. Generate or refresh it with:

```bash
python3 scripts/build_human_eval_app.py \
  --packet research_artifacts/human_eval_20task_packet/human_eval_blinded_packet.csv \
  --output research_artifacts/human_eval_20task_packet/human_eval_annotation_app.html
```

Open `human_eval_annotation_app.html` locally, score all artifacts, and download `human_eval_completed.csv`. Browser progress is stored in localStorage on the annotation machine.

Analyze a completed rating file with:

```bash
python3 scripts/analyze_human_eval.py \
  --completed-csv human_eval_completed.csv \
  --key research_artifacts/human_eval_20task_packet/human_eval_key.csv \
  --judge-json runs/ai_research_tasks20_primary_3seed_deepseek/quality_primary_analysis.json \
  --output-dir research_artifacts/human_eval_20task_packet/completed_analysis
```

No human ratings are included in this packet yet; it is a ready-to-run calibration protocol.
