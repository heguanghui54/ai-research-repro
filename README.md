# ai research 复现

## Current paper output

This repository now contains a compact AI Scientist V2 style pilot study on
AI research workflows, multi-agent orchestration, artifact evolution, and
model-judged research-artifact quality.

Main generated paper:

- Markdown draft with inserted results:
  [`research_artifacts/paper_with_results.md`](research_artifacts/paper_with_results.md)
- Final compiled PDF from the local run:
  [`runs/research_pilot_deepseek_v3/submission_package/paper.pdf`](runs/research_pilot_deepseek_v3/submission_package/paper.pdf)
- Detailed Chinese process report:
  [`docs/AI_SCIENTIST_V2_RESEARCH_PROCESS.zh.md`](docs/AI_SCIENTIST_V2_RESEARCH_PROCESS.zh.md)
- Reproducibility checklist:
  [`research_artifacts/reproducibility_checklist.md`](research_artifacts/reproducibility_checklist.md)

The current paper is best understood as a workshop draft / pilot diagnostic
study. It intentionally does not claim full scientific autonomy, cross-model
generality, or human-validated quality calibration.

This project is a compact, executable reproduction scaffold for the
`The AI Scientist` style workflow:

- GPT handles `idea / review / writeup`
- Codex-style local editing and execution handles `patch / run / debug / chart`
- The first template is `NanoGPT-lite`
- The first milestone is one successful closed loop

It is intentionally small, deterministic, and easy to extend.

## What this repo does

The pipeline:

1. Generates candidate research ideas
2. Filters obvious duplicates / weak ideas
3. Runs a NanoGPT-lite baseline
4. Applies a candidate patch by editing a training config
5. Re-trains and compares metrics
6. Generates a report and a review summary
7. Saves charts and artifacts in a run directory

## Interactive explainer

There is also a browser demo at [`site/index.html`](site/index.html).
It turns the AI Scientist-v2 workflow into a kid-friendly visual explanation and includes a clickable simulated experiment.

To preview it locally:

```bash
python3 -m http.server 8000 --directory site
```

Then open `http://localhost:8000` in a browser.

## Quickstart

```bash
python -m pip install -r requirements.txt
python -m ai_research_repro.cli run --workspace runs/demo --ideas 3
```

If `DEEPSEEK_API_KEY` is set, the pipeline uses DeepSeek first through its
OpenAI-compatible API. Optional VLM calls can use Monica by setting
`MONICA_API_KEY` and `MONICA_BASE_URL`. If no API key is configured, the code
falls back to deterministic heuristics for smoke tests.

```bash
cp .env.example .env
# edit .env with local secrets
bash scripts/run_ubuntu_pilot.sh
```

In the Codex app environment setup script, use `export DEEPSEEK_API_KEY=...`
and `export MONICA_API_KEY=...`; plain shell assignments are not visible to
Python subprocesses.
Monica's OpenAI-compatible base URL is `https://openapi.monica.im/v1`.

## Main commands

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli doctor
PYTHONPATH=src python3 -m ai_research_repro.cli doctor --strict
python -m ai_research_repro.cli run --workspace runs/demo --ideas 3
python -m ai_research_repro.cli baseline --workspace runs/baseline_only
python -m ai_research_repro.cli review --report artifacts/demo/report.md
PYTHONPATH=src python3 -m ai_research_repro.cli research-benchmark --workspace runs/research_pilot
PYTHONPATH=src python3 -m ai_research_repro.cli research-benchmark --workspace runs/research_pilot --seeds 0,1,2 --role-mode orchestrated
PYTHONPATH=src python3 -m ai_research_repro.cli write-task-template --output research_artifacts/external_tasks_template.json
PYTHONPATH=src python3 -m ai_research_repro.cli research-benchmark --workspace runs/research_external --task-file research_artifacts/external_tasks_template.json --seeds 0,1,2 --role-mode orchestrated
PYTHONPATH=src python3 -m ai_research_repro.cli audit-claims --results runs/research_pilot/research_benchmark_results.json
PYTHONPATH=src python3 -m ai_research_repro.cli analyze-results --results runs/research_pilot/research_benchmark_results.json
PYTHONPATH=src python3 -m ai_research_repro.cli write-paper-from-results --results runs/research_pilot/research_benchmark_results.json
PYTHONPATH=src python3 -m ai_research_repro.cli export-paper-package --paper research_artifacts/paper_with_results.md --results-dir runs/research_pilot --output-dir runs/research_pilot/submission_package
```

## Repo layout

- `src/ai_research_repro/templates/nanogpt_lite.py`: the executable toy
  NanoGPT-style benchmark
- `src/ai_research_repro/orchestrator.py`: end-to-end workflow
- `src/ai_research_repro/llm.py`: GPT wrappers and fallback logic
- `src/ai_research_repro/writer.py`: report generation
- `src/ai_research_repro/reviewer.py`: critique generation
- `src/ai_research_repro/research_benchmark.py`: micro-benchmark for
  automated research agents and self-evolution ablations
- `src/ai_research_repro/benchmark_tasks.py`: default task set and external
  benchmark task import schema
- `src/ai_research_repro/claim_audit.py`: claim/evidence audit before paper
  writing
- `src/ai_research_repro/paper_builder.py`: result-to-paper aggregation
- `src/ai_research_repro/paper_export.py`: paper package and LaTeX export
- `src/ai_research_repro/result_analysis.py`: paired-seed and cost-normalized
  result analysis
- `research_artifacts/`: topic, literature notes, experiment plan, and paper
  draft artifacts

## Notes

This is not a full reimplementation of the Sakana AI system. It is a
practical, runnable scaffold that captures the main workflow so we can
iterate toward a more faithful reproduction.

## Optional GPT support

If you want the GPT-backed steps, install the OpenAI SDK manually:

```bash
python -m pip install openai
```
