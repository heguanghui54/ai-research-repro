#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}/co-pilot-ai-scientist-v3"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$(dirname "$TARGET_DIR")"
rm -rf "$TARGET_DIR"
cp -R "$SOURCE_DIR" "$TARGET_DIR"

echo "Installed Co-Pilot AI Scientist v3 skill to: $TARGET_DIR"
echo "Start a new Codex session and ask to use the co-pilot-ai-scientist-v3 skill."
