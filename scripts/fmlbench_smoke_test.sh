#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${FMLBENCH_REPO_DIR:-$PWD}"
TASK="${FMLBENCH_TASK:-Causality_causalml}"
AGENT_CONFIG="${FMLBENCH_AGENT_CONFIG:-configs/agents/ai_scientist_v2.yaml}"
TASK_CONFIG="${FMLBENCH_TASK_CONFIG:-configs/tasks/causality_causalml.yaml}"
MODEL="${FMLBENCH_MODEL:-deepseek-v4-flash}"
PROVIDER="${FMLBENCH_PROVIDER:-DeepSeek}"
OUTPUT_DIR="${FMLBENCH_OUTPUT_DIR:-results}"
MAX_STEPS="${FMLBENCH_MAX_STEPS:-20}"
DO_SETUP="${FMLBENCH_DO_SETUP:-0}"

cd "$REPO_DIR"

if [[ ! -f "run_agent_benchmark.py" ]]; then
  echo "This script expects the official FML-bench repo root." >&2
  echo "Set FMLBENCH_REPO_DIR to the cloned official repository." >&2
  exit 1
fi

if [[ "$DO_SETUP" == "1" ]]; then
  python setup.py --task "$TASK"
fi

if [[ "$PROVIDER" == "Monica" ]]; then
  python "$SCRIPT_DIR/patch_fmlbench_monica_provider.py" --repo "$REPO_DIR"
  export MONICA_API_KEY="${MONICA_API_KEY:-}"
  export MONICA_BASE_URL="${MONICA_BASE_URL:-https://openapi.monica.im/v1}"
elif [[ "$PROVIDER" == "DeepSeek" ]]; then
  export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"
  export DEEPSEEK_BASE_URL="${DEEPSEEK_BASE_URL:-https://api.deepseek.com}"
else
  echo "Unsupported PROVIDER=$PROVIDER. Use DeepSeek or Monica." >&2
  exit 1
fi

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

python run_agent_benchmark.py \
  --agent-config "$AGENT_CONFIG" \
  --task-config "$TASK_CONFIG" \
  --model "$MODEL" \
  --provider "$PROVIDER" \
  --output-dir "$OUTPUT_DIR" \
  "agent.ai_scientist_v2.max_steps=$MAX_STEPS"
