# Reproducibility Checklist

This checklist regenerates the current evidence package without exposing secret keys.

## Environment

```bash
cd /path/to/research
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
export DEEPSEEK_API_KEY=...
export DEEPSEEK_BASE_URL=https://api.deepseek.com
export MONICA_API_KEY=...
export MONICA_BASE_URL=https://openapi.monica.im/v1
export MONICA_VLM_MODEL=gpt-4o
PYTHONPATH=src python3 -m ai_research_repro.cli doctor --strict --require-vlm
```

The current package was assembled on macOS 26.5 arm64 with Python 3.9.6 on an Apple M4 machine with 16 GB RAM. Runtime measurements should be treated as machine-local. Main text/code calls use OpenAI-compatible chat completions through DeepSeek at `https://api.deepseek.com` with `model=deepseek-chat`, `temperature=0.2`, `timeout=45s`, and `max_retries=2`. VLM/Monica calls use `https://openapi.monica.im/v1` with `model=gpt-4o`, `temperature=0.1`, `timeout=45s`, and `max_retries=2`. The APIs do not expose immutable provider-side model snapshot IDs in the logged responses, so the exact provider snapshot is not recoverable from this package.

## Main Workflow Benchmark

```bash
bash scripts/run_ubuntu_pilot.sh
```

The current main paper package uses the merged v3 run:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli analyze-results \
  --results runs/research_pilot_deepseek_v3/research_benchmark_results.json

PYTHONPATH=src python3 -m ai_research_repro.cli audit-claims \
  --results runs/research_pilot_deepseek_v3/research_benchmark_results.json
```

Expected main-run headline:

- best raw structural score: `author_curated_reference` (deterministic calibration anchor, not an autonomous-agent result)
- best autonomous API-backed raw structural score: `multi_fixed`
- best score per call: `single_reflection`
- claim audit: `pass_with_warnings`
- quality-primary finding: among autonomous API-backed methods, `single_fixed` has the highest cross-judge mean quality under the DeepSeek/Monica judge-pair protocol

## Twenty-Task Structural Expansion

The 20-task diagnostic structural comparison is assembled from the original five-seed run plus per-seed extensions:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli extend-results \
  --workspace runs/ai_research_tasks20_primary_8seed_deepseek \
  --base-results runs/ai_research_tasks20_primary_5seed_deepseek/research_benchmark_results.json \
  --add-results \
    runs/ai_research_tasks20_primary_seed5_deepseek/research_benchmark_results.json \
    runs/ai_research_tasks20_primary_seed6_deepseek/research_benchmark_results.json \
    runs/ai_research_tasks20_primary_seed7_deepseek/research_benchmark_results.json

PYTHONPATH=src python3 -m ai_research_repro.cli extend-results \
  --workspace runs/ai_research_tasks20_primary_10seed_deepseek \
  --base-results runs/ai_research_tasks20_primary_8seed_deepseek/research_benchmark_results.json \
  --add-results \
    runs/ai_research_tasks20_primary_seed8_deepseek/research_benchmark_results.json \
    runs/ai_research_tasks20_primary_seed9_deepseek/research_benchmark_results.json

PYTHONPATH=src python3 -m ai_research_repro.cli analyze-results \
  --results runs/ai_research_tasks20_primary_10seed_deepseek/research_benchmark_results.json

PYTHONPATH=src python3 -m ai_research_repro.cli audit-claims \
  --results runs/ai_research_tasks20_primary_10seed_deepseek/research_benchmark_results.json
```

Expected 10-seed API-backed structural means:

- `single_fixed`: 336.0
- `multi_fixed`: 428.7
- paired structural delta, `multi_fixed` minus `single_fixed`: 92.7
- claim audit: `pass_with_warnings`

The 10-seed artifact-quality judge pass covers all 440 artifacts in that merged result:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli judge-artifacts \
  --results runs/ai_research_tasks20_primary_10seed_deepseek/research_benchmark_results.json \
  --output-dir runs/ai_research_tasks20_primary_10seed_deepseek \
  --model deepseek-chat \
  --batch-size 5 \
  --output-prefix artifact_quality_judge

PYTHONPATH=src python3 -m ai_research_repro.cli judge-artifacts \
  --results runs/ai_research_tasks20_primary_10seed_deepseek/research_benchmark_results.json \
  --output-dir runs/ai_research_tasks20_primary_10seed_deepseek \
  --model gpt-4o \
  --batch-size 5 \
  --multimodal \
  --output-prefix artifact_quality_judge_monica

PYTHONPATH=src python3 -m ai_research_repro.cli compare-judges \
  --judge-a runs/ai_research_tasks20_primary_10seed_deepseek/artifact_quality_judge.json \
  --judge-b runs/ai_research_tasks20_primary_10seed_deepseek/artifact_quality_judge_monica.json \
  --output-dir runs/ai_research_tasks20_primary_10seed_deepseek

PYTHONPATH=src python3 -m ai_research_repro.cli analyze-quality-primary \
  --judge-a runs/ai_research_tasks20_primary_10seed_deepseek/artifact_quality_judge.json \
  --judge-b runs/ai_research_tasks20_primary_10seed_deepseek/artifact_quality_judge_monica.json \
  --output-dir runs/ai_research_tasks20_primary_10seed_deepseek
```

Expected 10-seed quality-primary means:

- `single_fixed`: 3.5125
- `multi_fixed`: 3.19
- paired quality delta, `multi_fixed` minus `single_fixed`: -0.3225 over 200 matched comparisons
- judge comparison: Pearson 0.5948178110266141, Spearman 0.5937682647550014 over 440 artifacts

The budget-matched `single_self_consistency` control is generated as ten one-seed runs and merged with the primary 10-seed result:

```bash
for seed in 0 1 2 3 4 5 6 7 8 9; do
  PYTHONPATH=src python3 -m ai_research_repro.cli research-benchmark \
    --workspace runs/ai_research_tasks20_self_consistency_seed${seed}_deepseek \
    --model deepseek-chat \
    --methods single_self_consistency \
    --seeds ${seed} \
    --task-file research_artifacts/ai_research_tasks_20.json \
    --role-mode orchestrated
done

PYTHONPATH=src python3 -m ai_research_repro.cli extend-results \
  --workspace runs/ai_research_tasks20_self_consistency_10seed_deepseek \
  --base-results runs/ai_research_tasks20_self_consistency_seed0_deepseek/research_benchmark_results.json \
  --add-results \
    runs/ai_research_tasks20_self_consistency_seed1_deepseek/research_benchmark_results.json \
    runs/ai_research_tasks20_self_consistency_seed2_deepseek/research_benchmark_results.json \
    runs/ai_research_tasks20_self_consistency_seed3_deepseek/research_benchmark_results.json \
    runs/ai_research_tasks20_self_consistency_seed4_deepseek/research_benchmark_results.json \
    runs/ai_research_tasks20_self_consistency_seed5_deepseek/research_benchmark_results.json \
    runs/ai_research_tasks20_self_consistency_seed6_deepseek/research_benchmark_results.json \
    runs/ai_research_tasks20_self_consistency_seed7_deepseek/research_benchmark_results.json \
    runs/ai_research_tasks20_self_consistency_seed8_deepseek/research_benchmark_results.json \
    runs/ai_research_tasks20_self_consistency_seed9_deepseek/research_benchmark_results.json

PYTHONPATH=src python3 -m ai_research_repro.cli extend-results \
  --workspace runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek \
  --base-results runs/ai_research_tasks20_primary_10seed_deepseek/research_benchmark_results.json \
  --add-results runs/ai_research_tasks20_self_consistency_10seed_deepseek/research_benchmark_results.json
```

Expected combined 10-seed self-consistency findings:

- structural mean, `single_self_consistency`: 359.9
- cross-judge mean quality, `single_self_consistency`: 3.1075 over 200 artifacts
- combined quality-primary coverage: 640 artifacts
- combined judge comparison: Pearson 0.5782908896460613, Spearman 0.5738774217438741 over 640 artifacts

The paired divergence and verbosity-control diagnostic for the combined 640-artifact set is:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli analyze-divergence \
  --results runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek/research_benchmark_results.json \
  --judge-a runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek/artifact_quality_judge.json \
  --judge-b runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek/artifact_quality_judge_monica.json \
  --output-dir runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek
```

Expected divergence diagnostic:

- `multi_fixed`: mean structural delta +4.635 per task artifact, mean quality delta -0.3225, opposite-direction pairs 85/200, length-controlled quality-delta intercept -0.1302 with CI crossing zero
- `single_self_consistency`: mean structural delta +1.195, mean quality delta -0.405, opposite-direction pairs 62/200, length-controlled quality-delta intercept -1.1269

## AIRS Official-Definition Planning Runs

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli import-airs-tasks \
  --repo-dir /tmp/airs-bench \
  --output research_artifacts/airs_official_tasks_subset.json \
  --split rad \
  --limit 6 \
  --max-per-category 1

PYTHONPATH=src python3 -m ai_research_repro.cli import-airs-tasks \
  --repo-dir /tmp/airs-bench \
  --output research_artifacts/airs_official_tasks_12.json \
  --split rad \
  --limit 12 \
  --max-per-category 2

PYTHONPATH=src python3 -m ai_research_repro.cli research-benchmark \
  --workspace runs/airs_official_12_deepseek \
  --model deepseek-chat \
  --methods single_fixed,single_self_consistency,multi_fixed \
  --seeds 0 \
  --task-file research_artifacts/airs_official_tasks_12.json \
  --role-mode orchestrated
```

Expected 12-task planning-proxy scores:

- `single_fixed`: 308
- `single_self_consistency`: 295
- `multi_fixed`: 355

These are not official AIRS scores; they evaluate planning/evidence artifacts generated from official task definitions.

## AIRS SVAMP Evaluator Runs

Evaluator smoke test:

```bash
python3 scripts/run_airs_evaluator_smoke.py \
  --airs-repo /tmp/airs-bench \
  --output-dir runs/airs_evaluator_smoke_svamp
```

Expected smoke-test accuracies:

- `gold`: 1.0
- `constant_zero`: 0.0
- `shifted_gold`: 0.013333333333333334

DeepSeek-generated SVAMP submission:

```bash
python3 scripts/run_svamp_deepseek_submission.py \
  --airs-repo /tmp/airs-bench \
  --output-dir runs/airs_svamp_deepseek_submission \
  --model deepseek-chat \
  --limit 300 \
  --batch-size 10 \
  --few-shot 4
```

Expected DeepSeek SVAMP result:

- examples: 300
- LLM calls: 30
- fallback calls: 0
- accuracy: 0.9266666666666666
- output: `runs/airs_svamp_deepseek_submission/submission.csv`

This is a local task-local evaluator run, not an official AIRS leaderboard submission.

## Paper Package

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli write-paper-from-results \
  --results runs/research_pilot_deepseek_v3/research_benchmark_results.json \
  --base-draft research_artifacts/paper_draft.md \
  --output research_artifacts/paper_with_results.md

PYTHONPATH=src python3 -m ai_research_repro.cli export-paper-package \
  --paper research_artifacts/paper_with_results.md \
  --results-dir runs/research_pilot_deepseek_v3 \
  --output-dir runs/research_pilot_deepseek_v3/submission_package \
  --references research_artifacts/references.bib

python3 /Users/hgh54913/.codex/plugins/cache/openai-bundled/latex/0.2.2/scripts/compile_latex.py \
  /path/to/research/runs/research_pilot_deepseek_v3/submission_package/paper.tex \
  --compiler tectonic \
  --json
```

Expected package checks:

```bash
pdfimages -list runs/research_pilot_deepseek_v3/submission_package/paper.pdf
pdftotext runs/research_pilot_deepseek_v3/submission_package/paper.pdf - | rg "Appendix G|0.926666|References"
```

The final package should contain:

- `paper.pdf`
- `paper.md`
- `paper.tex`
- `references.bib`
- main analysis and claim audit files
- embedded figure PNGs and source SVGs
- role traces
- supplemental AIRS task files
- AIRS evaluator smoke outputs
- DeepSeek SVAMP submission outputs
- blinded human-evaluation packet, local annotation HTML, and scoring-analysis script
