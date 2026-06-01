#!/usr/bin/env python3
"""Run OpenEvolve on an arbitrary Python program/evaluator pair."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from openevolve import Config, run_evolution
from openevolve.config import LLMModelConfig


def _provider_config(provider: str, model: str | None) -> tuple[str, str, str]:
    provider = provider.lower()
    if provider == "monica":
        return (
            os.environ.get("MONICA_BASE_URL", "https://openapi.monica.im/v1"),
            os.environ["MONICA_API_KEY"],
            model or "gpt-4o-mini",
        )
    if provider == "deepseek":
        return (
            os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            os.environ["DEEPSEEK_API_KEY"],
            model or "deepseek-chat",
        )
    return (
        os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        os.environ["OPENAI_API_KEY"],
        model or "gpt-4o-mini",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run OpenEvolve program search.")
    parser.add_argument("--initial-program", required=True)
    parser.add_argument("--evaluator", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--provider", default="deepseek", choices=["deepseek", "monica", "openai"])
    parser.add_argument("--model", default=None)
    parser.add_argument("--population-size", type=int, default=16)
    parser.add_argument("--archive-size", type=int, default=16)
    parser.add_argument("--num-islands", type=int, default=2)
    parser.add_argument("--random-seed", type=int, default=42)
    args = parser.parse_args()

    api_base, api_key, model = _provider_config(args.provider, args.model)

    cfg = Config(
        max_iterations=args.iterations,
        checkpoint_interval=1,
        random_seed=args.random_seed,
        log_level="INFO",
    )
    cfg.llm.api_base = api_base
    cfg.llm.api_key = api_key
    cfg.llm.models = [
        LLMModelConfig(
            name=model,
            weight=1.0,
            api_base=api_base,
            api_key=api_key,
            temperature=0.2,
            max_tokens=3072,
            timeout=120,
        )
    ]
    cfg.database.population_size = args.population_size
    cfg.database.archive_size = args.archive_size
    cfg.database.num_islands = args.num_islands
    cfg.evaluator.timeout = 120
    cfg.evaluator.cascade_evaluation = False

    output_dir = Path(args.output_dir)
    result = run_evolution(
        initial_program=Path(args.initial_program),
        evaluator=Path(args.evaluator),
        config=cfg,
        iterations=args.iterations,
        output_dir=str(output_dir),
        cleanup=False,
    )
    summary = {
        "status": "completed",
        "iterations": args.iterations,
        "random_seed": args.random_seed,
        "provider": args.provider,
        "model": model,
        "api_base_host": api_base.split("//")[-1].split("/")[0],
        "initial_program": args.initial_program,
        "evaluator": args.evaluator,
        "best_score": getattr(result, "best_score", None),
        "output_dir": str(output_dir),
    }
    (output_dir.parent / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
