# ai research 复现

A compact, executable scaffold for the `The AI Scientist` style workflow.
The goal is not to clone the full Sakana AI system on day one. The goal is
to keep the loop small enough that we can actually run it end to end, then
grow it step by step.

## AI Scientist-v2 reproduction snapshot

This repository also records a low-cost reproduction pass for
`SakanaAI/AI-Scientist-v2`.

- Goal: run the paper-generation loop end to end and produce a paper PDF
- Execution: remote Ubuntu host over SSH
- Cost strategy: prefer cheaper models first, including `gpt-4o-mini`
- Result: a paper PDF was generated successfully
- Reference PR: [heguanghui54/AI-Scientist#1](https://github.com/heguanghui54/AI-Scientist/pull/1)

What had to be stabilized:

- LaTeX compilation on the remote host was switched to `tectonic`
- The writeup step was made resilient when VLM reflection is unavailable
- The expected figure files were supplied so the manuscript could compile

The reproduction note is kept in
[AI-Scientist-v2-reproduction-note.md](AI-Scientist-v2-reproduction-note.md).

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

## Web Workspace

The repository now also ships a FastAPI-based research workspace that wraps
the AI Scientist-v2 style loop into a browser UI:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli web
```

Then open `http://127.0.0.1:8000` and:

1. Register or log in.
2. Create a project with your own topic and OpenAI-compatible API key.
3. Start a run and watch the live timeline.
4. Pause at ideation, benchmark, planning, execution, or writing checkpoints.
5. Save notes, resume, rewind, and revisit the file library or run history.

The web app persists runs, events, artifacts, generated papers, and PDFs in
`data/` for per-user replay and review.

The project form now also supports an `HF streaming benchmark` template. That
path uses a real Hugging Face benchmark adapter with `datasets.load_dataset(...,
streaming=True, trust_remote_code=True)` so the dataset stays remote until the
loop materializes a bounded sample locally.

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
