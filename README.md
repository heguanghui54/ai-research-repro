# ai research 复现

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

If `OPENAI_API_KEY` is set and `openai` is installed, the pipeline uses
GPT for idea generation, review, and writeup. Otherwise it falls back to
deterministic heuristics.

## Main commands

```bash
python -m ai_research_repro.cli run --workspace runs/demo --ideas 3
python -m ai_research_repro.cli baseline --workspace runs/baseline_only
python -m ai_research_repro.cli review --report artifacts/demo/report.md
```

## Repo layout

- `src/ai_research_repro/templates/nanogpt_lite.py`: the executable toy
  NanoGPT-style benchmark
- `src/ai_research_repro/orchestrator.py`: end-to-end workflow
- `src/ai_research_repro/llm.py`: GPT wrappers and fallback logic
- `src/ai_research_repro/writer.py`: report generation
- `src/ai_research_repro/reviewer.py`: critique generation

## Notes

This is not a full reimplementation of the Sakana AI system. It is a
practical, runnable scaffold that captures the main workflow so we can
iterate toward a more faithful reproduction.

## Optional GPT support

If you want the GPT-backed steps, install the OpenAI SDK manually:

```bash
python -m pip install openai
```
