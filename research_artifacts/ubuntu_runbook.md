# Ubuntu Experiment Runbook

## 1. Setup

```bash
cd /path/to/research
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` locally:

```bash
DEEPSEEK_API_KEY=...
DEEPSEEK_BASE_URL=https://api.deepseek.com
MONICA_API_KEY=...
MONICA_BASE_URL=https://openapi.monica.im/v1
MONICA_VLM_MODEL=gpt-4o
```

Do not commit `.env`.

## Codex App Environment Setup

If keys are configured in the Codex app's environment setup script, they must be exported so child processes can see them:

```bash
export DEEPSEEK_API_KEY=...
export DEEPSEEK_BASE_URL=https://api.deepseek.com
export MONICA_API_KEY=...
export MONICA_BASE_URL=https://openapi.monica.im/v1
export MONICA_VLM_MODEL=gpt-4o
```

Plain assignments such as `DEEPSEEK_API_KEY=...` are not enough for `python3 -m ai_research_repro.cli doctor`, because they are not inherited by subprocesses.

Another safe pattern is to enable auto-export before assignments:

```bash
set -a
DEEPSEEK_API_KEY=...
DEEPSEEK_BASE_URL=https://api.deepseek.com
MONICA_API_KEY=...
MONICA_BASE_URL=https://openapi.monica.im/v1
MONICA_VLM_MODEL=gpt-4o
set +a
```

You can also keep secrets outside the repository:

```bash
mkdir -p ~/.config/ai_research_repro
cp .env.example ~/.config/ai_research_repro/.env
# edit ~/.config/ai_research_repro/.env
export AI_RESEARCH_ENV_FILE=~/.config/ai_research_repro/.env
```

## 2. Pilot Run

Check provider configuration without printing secrets:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli doctor
PYTHONPATH=src python3 -m ai_research_repro.cli doctor --strict
```

`doctor --strict` exits non-zero when DeepSeek is not visible. The full pilot script uses this guard so fallback smoke tests cannot be mistaken for API-backed experiments.

```bash
bash scripts/run_ubuntu_pilot.sh
```

Equivalent explicit command:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli research-benchmark \
  --workspace runs/research_pilot_deepseek \
  --model deepseek-chat \
  --seeds 0,1,2 \
  --role-mode orchestrated
```

## 3. Expected Outputs

- `runs/research_pilot_deepseek/research_benchmark_results.json`
- `runs/research_pilot_deepseek/research_benchmark_summary.csv`
- `runs/research_pilot_deepseek/research_benchmark_summary.md`
- `runs/research_pilot_deepseek/claim_audit.md`
- `runs/research_pilot_deepseek/analysis.md`
- `runs/research_pilot_deepseek/figures/analysis_scores.svg`
- `runs/research_pilot_deepseek/figures/analysis_score_per_call.svg`
- `runs/research_pilot_deepseek/figures/analysis_delta_vs_baseline.svg`
- `runs/research_pilot_deepseek/repro_manifest.json`
- `runs/research_pilot_deepseek/role_trace_index.md`
- `runs/research_pilot_deepseek/role_traces/`
- `research_artifacts/paper_with_results.md`
- `runs/research_pilot_deepseek/submission_package/`

Manual paper update commands:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli audit-claims \
  --results runs/research_pilot_deepseek/research_benchmark_results.json

PYTHONPATH=src python3 -m ai_research_repro.cli analyze-results \
  --results runs/research_pilot_deepseek/research_benchmark_results.json

PYTHONPATH=src python3 -m ai_research_repro.cli write-paper-from-results \
  --results runs/research_pilot_deepseek/research_benchmark_results.json \
  --base-draft research_artifacts/paper_draft.md \
  --output research_artifacts/paper_with_results.md

PYTHONPATH=src python3 -m ai_research_repro.cli export-paper-package \
  --paper research_artifacts/paper_with_results.md \
  --results-dir runs/research_pilot_deepseek \
  --output-dir runs/research_pilot_deepseek/submission_package \
  --references research_artifacts/references.bib
```

## 4. Optional VLM Figure Critique

After a run produces figures, use Monica's OpenAI-compatible VLM endpoint:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli critique-figures \
  runs/some_experiment/artifacts/best_learning_curve.png \
  --claim-context "Learning curve used to support lower validation loss claim." \
  --model "${MONICA_VLM_MODEL:-gpt-4o}" \
  --output runs/some_experiment/artifacts/figure_critique.md
```

## 5. Paper-Quality Criteria Before Claiming Results

- Run at least three seeds.
- Save the exact `.env` model names without saving secret keys.
- Inspect `role_trace_index.md` for at least one task from each multi-agent method.
- Inspect generated artifacts for unsupported empirical claims.
- Rerun the best method from a clean checkout.
- Add human or independent-model spot review for a subset of outputs.
- Inspect `submission_package/package_manifest.json` before sharing or compiling the paper.

## 6. External Task Files

Create a task template:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli write-task-template \
  --output research_artifacts/external_tasks_template.json
```

Run an external task subset:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli research-benchmark \
  --workspace runs/research_external_deepseek \
  --model deepseek-chat \
  --seeds 0,1,2 \
  --task-file research_artifacts/external_tasks_template.json \
  --role-mode orchestrated
```

## 7. AIRS Official-Definition and Evaluator Runs

Clone AIRS-Bench locally:

```bash
git clone https://github.com/facebookresearch/airs-bench /tmp/airs-bench
```

Import a broader AIRS RAD official-definition subset:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli import-airs-tasks \
  --repo-dir /tmp/airs-bench \
  --output research_artifacts/airs_official_tasks_12.json \
  --split rad \
  --limit 12 \
  --max-per-category 2
```

Run the 12-task planning/evidence coverage experiment:

```bash
PYTHONPATH=src python3 -m ai_research_repro.cli research-benchmark \
  --workspace runs/airs_official_12_deepseek \
  --model deepseek-chat \
  --methods single_fixed,single_self_consistency,multi_fixed \
  --seeds 0 \
  --task-file research_artifacts/airs_official_tasks_12.json \
  --role-mode orchestrated
```

Run the SVAMP task-local evaluator smoke test:

```bash
python3 scripts/run_airs_evaluator_smoke.py \
  --airs-repo /tmp/airs-bench \
  --output-dir runs/airs_evaluator_smoke_svamp
```

Run the DeepSeek-generated SVAMP submission:

```bash
python3 scripts/run_svamp_deepseek_submission.py \
  --airs-repo /tmp/airs-bench \
  --output-dir runs/airs_svamp_deepseek_submission \
  --model deepseek-chat \
  --limit 300 \
  --batch-size 10 \
  --few-shot 4
```

Expected SVAMP result:

- `runs/airs_svamp_deepseek_submission/submission.csv`
- accuracy `0.9266666666666666`
- 30 LLM calls
- 0 fallback calls

This is a local evaluator-connected case study, not an official AIRS leaderboard result.

## 8. Final Paper Package

Regenerate the final package:

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
```

Compile `paper.tex` with Tectonic or a full TeX installation. The package includes `research_artifacts/reproducibility_checklist.md` for the exact evidence chain used by the current paper.
