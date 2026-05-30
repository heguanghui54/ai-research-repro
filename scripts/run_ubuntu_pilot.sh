#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example. Add DEEPSEEK_API_KEY before API-backed runs."
fi

export PYTHONPATH=src
WORKSPACE="${RESEARCH_WORKSPACE:-runs/research_pilot_deepseek}"
TASK_ARGS=()
if [[ -n "${RESEARCH_TASK_FILE:-}" ]]; then
  TASK_ARGS=(--task-file "$RESEARCH_TASK_FILE")
fi

python -m ai_research_repro.cli doctor --strict

python -m ai_research_repro.cli research-benchmark \
  --workspace "$WORKSPACE" \
  --model "${DEEPSEEK_MODEL:-deepseek-chat}" \
  --seeds "${RESEARCH_SEEDS:-0,1,2}" \
  ${TASK_ARGS[@]+"${TASK_ARGS[@]}"} \
  --role-mode "${RESEARCH_ROLE_MODE:-orchestrated}"

python -m ai_research_repro.cli audit-claims \
  --results "$WORKSPACE/research_benchmark_results.json"

python -m ai_research_repro.cli analyze-results \
  --results "$WORKSPACE/research_benchmark_results.json"

python -m ai_research_repro.cli analyze-policy-updates \
  --results "$WORKSPACE/research_benchmark_results.json" \
  --output-dir "$WORKSPACE"

if [[ "${RUN_ARTIFACT_QUALITY_JUDGE:-1}" == "1" ]]; then
  python -m ai_research_repro.cli judge-artifacts \
    --results "$WORKSPACE/research_benchmark_results.json" \
    --output-dir "$WORKSPACE" \
    --model "${DEEPSEEK_MODEL:-deepseek-chat}" \
    --batch-size "${ARTIFACT_JUDGE_BATCH_SIZE:-5}"
fi

python -m ai_research_repro.cli write-paper-from-results \
  --results "$WORKSPACE/research_benchmark_results.json" \
  --base-draft research_artifacts/paper_draft.md \
  --output research_artifacts/paper_with_results.md

python -m ai_research_repro.cli export-paper-package \
  --paper research_artifacts/paper_with_results.md \
  --results-dir "$WORKSPACE" \
  --output-dir "$WORKSPACE/submission_package" \
  --references research_artifacts/references.bib

if [[ "${RUN_PAPER_QUALITY_REVIEW:-1}" == "1" ]]; then
  python -m ai_research_repro.cli review-paper-quality \
    --paper "$WORKSPACE/submission_package/paper.md" \
    --results-dir "$WORKSPACE" \
    --output-dir "$WORKSPACE" \
    --model "${DEEPSEEK_MODEL:-deepseek-chat}"

  python -m ai_research_repro.cli export-paper-package \
    --paper research_artifacts/paper_with_results.md \
    --results-dir "$WORKSPACE" \
    --output-dir "$WORKSPACE/submission_package" \
    --references research_artifacts/references.bib
fi

echo "Results:"
echo "  $WORKSPACE/research_benchmark_results.json"
echo "  $WORKSPACE/research_benchmark_summary.csv"
echo "  $WORKSPACE/research_benchmark_summary.md"
echo "  $WORKSPACE/claim_audit.md"
echo "  $WORKSPACE/analysis.md"
echo "  $WORKSPACE/artifact_quality_judge.md"
echo "  $WORKSPACE/policy_update_analysis.md"
echo "  $WORKSPACE/paper_quality_review.md"
echo "  $WORKSPACE/role_trace_index.md"
echo "  research_artifacts/paper_with_results.md"
echo "  $WORKSPACE/submission_package/"
