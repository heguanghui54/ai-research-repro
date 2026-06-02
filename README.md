# Co-Pilot AI Scientist v3 Research Package

This repository now hosts the **Co-Pilot AI Scientist v3** research package:
a reproducible pilot paper and Codex skill for turning AI Scientist-v2-style
automation into a human-guided research co-pilot. The method is **Insight-Gated
Research Evolution (IGRE)**: AI systems generate hypotheses, run experiments,
search machine-gradeable subproblems with OpenEvolve-style loops, and write
papers, while human scientists intervene at explicit gates for scientific
taste, evaluator stress testing, frontier steering, verifiable micro-evolution,
and claim calibration.

Start here:

- Research package README:
  [docs/co_pilot_ai_scientist_v3/README.md](docs/co_pilot_ai_scientist_v3/README.md)
- English submission card:
  [docs/co_pilot_ai_scientist_v3/submission_card_en.md](docs/co_pilot_ai_scientist_v3/submission_card_en.md)
- Chinese submission card:
  [docs/co_pilot_ai_scientist_v3/submission_card_zh.md](docs/co_pilot_ai_scientist_v3/submission_card_zh.md)
- Top-conference evidence roadmap:
  [docs/co_pilot_ai_scientist_v3/top_conference_evidence_roadmap.md](docs/co_pilot_ai_scientist_v3/top_conference_evidence_roadmap.md)
- Focused English paper:
  [docs/co_pilot_ai_scientist_v3/paper_en_focused.md](docs/co_pilot_ai_scientist_v3/paper_en_focused.md)
- Focused Chinese paper:
  [docs/co_pilot_ai_scientist_v3/paper_zh_focused.md](docs/co_pilot_ai_scientist_v3/paper_zh_focused.md)
- English focused PDF:
  [docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_focused_en.pdf](docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_focused_en.pdf)
- Chinese focused PDF:
  [docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_focused_zh.pdf](docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_focused_zh.pdf)
- Reusable Codex skill:
  [skills/co-pilot-ai-scientist-v3/SKILL.md](skills/co-pilot-ai-scientist-v3/SKILL.md)
- English usage guide:
  [docs/co_pilot_ai_scientist_v3/usage_en.md](docs/co_pilot_ai_scientist_v3/usage_en.md)
- Chinese usage guide:
  [docs/co_pilot_ai_scientist_v3/usage_zh.md](docs/co_pilot_ai_scientist_v3/usage_zh.md)

## External Verification Entry Point

```bash
python3 -m pip install -r requirements.txt
python3 scripts/audit_long_horizon_taste_gate.py
python3 scripts/audit_temporal_frontier_replay.py
python3 scripts/audit_top_conference_evidence_roadmap.py
python3 scripts/audit_human_expert_blind_review_packet.py
python3 scripts/audit_benchmark_coverage.py
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
python3 scripts/audit_objective_delivery.py
python3 scripts/audit_package_consistency.py
```

Current objective-delivery status:

- artifact pipeline: `pass_artifact_delivery_with_empirical_gaps`
- manifest coverage: `635/635`
- LHTG/DVRS audit: `pass_with_no_positive_dvrs`
- TFR audit: `pass_with_negative_delayed_value_evidence`
- roadmap audit: `pass`
- human expert blind-review packet audit: `pass_prepared_no_human_ratings`
- benchmark coverage audit: `pass`
- package consistency: `pass`

Important boundary: this package delivers the requested bilingual papers,
usage guides, reusable skill, pushed GitHub branch, and reproducibility audits.
The top-conference empirical target is not yet satisfied: this package does
**not** prove empirical superiority over autonomous AI Scientist-v2. The
remaining evidence gap is independent human expert ratings, larger matched
autonomous versus human-gated benchmark runs, and broader end-to-end research
trajectories.

## Legacy FML-bench Minimal Reproduction

This repository is a **low-cost, minimal reproduction scaffold** for the
`FML-bench` paper and GitHub workflow.

What it does:

1. Runs a tiny, deterministic NanoGPT-style benchmark locally
2. Uses the same idea -> edit -> run -> review loop described in the paper
3. Picks an LLM provider in this order: `DeepSeek` -> `Monica` -> `OpenAI`
4. Falls back to deterministic heuristics if no API key is available

What it does not do:

1. It does **not** clone or execute the full 18-task official benchmark
2. It does **not** claim the paper's reported numbers
3. It is meant to keep cost in the "few dollars" range, or zero if you skip APIs

## Why this is the right minimal path

The paper's main idea is the evaluation loop, not a single model trick:

- a baseline codebase
- candidate ideas
- validation runs
- best-run selection
- a short writeup and review

This repo keeps that loop, but shrinks the benchmark to a local toy task so
you can verify the plumbing cheaply before touching the heavy official setup.

## Install

```bash
python -m pip install -r requirements.txt
```

## Minimal run

Use `DeepSeek` first if you have it. If not, the code falls back to `Monica`,
then `OpenAI`.

```bash
export DEEPSEEK_API_KEY="your_key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"

# optional fallback
export MONICA_API_KEY="your_key"
export MONICA_BASE_URL="https://openapi.monica.im/v1"

python -m ai_research_repro.cli run \
  --workspace runs/fmlbench-minimal \
  --ideas 2
```

If you want to force a provider:

```bash
python -m ai_research_repro.cli run \
  --workspace runs/fmlbench-minimal \
  --ideas 2 \
  --provider deepseek
```

If no API keys are set, the pipeline still runs with deterministic fallback
ideas and reviews.

## Outputs

The run writes:

- `runs/fmlbench-minimal/artifacts/baseline_config.json`
- `runs/fmlbench-minimal/artifacts/ideas.json`
- `runs/fmlbench-minimal/artifacts/report.md`
- `runs/fmlbench-minimal/artifacts/review.json`
- `runs/fmlbench-minimal/artifacts/summary.json`
- `runs/fmlbench-minimal/artifacts/best_learning_curve.png`

## How this maps to the paper

The paper compares search strategies over many ML tasks. This scaffold keeps
the same structure but uses one tiny local benchmark so the setup stays cheap:

- `baseline` -> the default NanoGPT-lite config
- `ideas` -> candidate search directions
- `validation` -> repeated local training runs
- `best candidate` -> the best validation loss
- `report` -> a short markdown summary

If you later want the full benchmark, use the official repo:

- [qrzou/FML-bench](https://github.com/qrzou/FML-bench)

For a practical Ubuntu-side runbook that starts with a cheap smoke test and
then scales up, see
[docs/fmlbench_official_ubuntu_runbook.md](docs/fmlbench_official_ubuntu_runbook.md).
中文复现说明见
[docs/fmlbench_中文复现说明.md](docs/fmlbench_中文复现说明.md).
面向中学生的可视动画解释见
[visuals/fmlbench_agent_animation.html](visuals/fmlbench_agent_animation.html).
The helper script for the official repo is
[scripts/fmlbench_smoke_test.sh](scripts/fmlbench_smoke_test.sh).
If you need the Monica fallback on the official repo, use
[scripts/patch_fmlbench_monica_provider.py](scripts/patch_fmlbench_monica_provider.py).
If the installed Fairlearn API is older than the generated code expects, use
[scripts/patch_fmlbench_fairlearn_compat.py](scripts/patch_fmlbench_fairlearn_compat.py).
For the actual Ubuntu verification record, see
[docs/fmlbench_verification_log.md](docs/fmlbench_verification_log.md).

On an Ubuntu machine, the official repo still needs task repos, conda envs, and
GPU time, so it is better to validate this minimal scaffold first.

## Repro notes

1. The provider order is cost-aware by default.
2. DeepSeek is preferred because it is usually the cheapest option for this use.
3. Monica is the fallback if DeepSeek is unavailable.
4. The code stays deterministic when no API is configured.
