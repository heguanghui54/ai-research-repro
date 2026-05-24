# ai research 复现

A compact, executable scaffold for the `The AI Scientist` style workflow.
The goal is not to clone the full Sakana AI system on day one. The goal is
to keep the loop small enough that we can actually run it end to end, then
grow it step by step.

## What is in scope

- GPT handles `idea / review / writeup`
- Codex-style local execution handles `patch / run / debug / chart`
- The first template is `NanoGPT-lite`
- The first milestone is one successful closed loop

## What the pipeline does

1. Generate a small batch of candidate research ideas
2. Filter out obvious duplicates or weak proposals
3. Run a deterministic NanoGPT-lite baseline
4. Apply a candidate patch by editing a training config
5. Re-train and compare metrics against the baseline
6. Generate a short report and review summary
7. Save charts, metrics, and artifacts in a run directory

## Quickstart

```bash
python -m pip install -r requirements.txt
python -m ai_research_repro.cli run --workspace runs/demo --ideas 3
```

If `OPENAI_API_KEY` is set and `openai` is installed, the pipeline uses GPT
for idea generation, review, and writeup. Otherwise it falls back to
deterministic heuristics so the repo stays runnable in a minimal environment.

## Main commands

```bash
python -m ai_research_repro.cli run --workspace runs/demo --ideas 3
python -m ai_research_repro.cli baseline --workspace runs/baseline_only
python -m ai_research_repro.cli review --report artifacts/demo/report.md
```

## Workflow shape

```mermaid
flowchart LR
  A["Idea generation"] --> B["Novelty filter"]
  B --> C["Baseline run"]
  C --> D["Patch + retrain"]
  D --> E["Chart + analysis"]
  E --> F["Write report"]
  F --> G["Review"]
  G --> H["Iterate if needed"]
```

## Repo layout

- `src/ai_research_repro/templates/nanogpt_lite.py`: executable toy
  NanoGPT-style benchmark
- `src/ai_research_repro/orchestrator.py`: end-to-end workflow
- `src/ai_research_repro/llm.py`: GPT wrappers and fallback logic
- `src/ai_research_repro/writer.py`: report generation
- `src/ai_research_repro/reviewer.py`: critique generation

## Design notes

- Keep the first template small and deterministic
- Prefer explicit artifacts over hidden state
- Make every stage rerunnable from the command line
- Optimize for one successful closed loop before expanding to more templates

## Optional GPT support

If you want the GPT-backed steps, install the OpenAI SDK manually:

```bash
python -m pip install openai
```
