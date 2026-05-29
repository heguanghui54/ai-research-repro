from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .charts import save_learning_curve
from .ideas import generate_ideas, novelty_filter
from .reviewer import review_report, save_review
from .templates.nanogpt_lite import NanoGPTConfig, apply_patch, default_config, summarize_config, train_and_evaluate
from .writer import save_report, write_report


@dataclass
class PipelineConfig:
    workspace: Path
    num_ideas: int = 3
    gpt_model: str | None = None
    provider: str | None = None
    run_baseline: bool = True


def _ensure_dirs(workspace: Path) -> dict[str, Path]:
    artifacts = workspace / "artifacts"
    runs = workspace / "runs"
    baseline = runs / "baseline"
    artifacts.mkdir(parents=True, exist_ok=True)
    runs.mkdir(parents=True, exist_ok=True)
    return {"artifacts": artifacts, "runs": runs, "baseline": baseline}


def _persist_config(path: Path, cfg: NanoGPTConfig) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(summarize_config(cfg), encoding="utf-8")


def _load_run(out_dir: Path) -> dict[str, Any]:
    metrics = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    history_path = out_dir / "history.json"
    history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else {"train_loss": [], "val_loss": []}
    sample_path = out_dir / "sample.txt"
    sample = sample_path.read_text(encoding="utf-8") if sample_path.exists() else ""
    config_path = out_dir / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else asdict(default_config())
    return {"metrics": metrics, "history": history, "sample": sample, "config": config}


def run_pipeline(cfg: PipelineConfig) -> dict[str, Any]:
    dirs = _ensure_dirs(cfg.workspace)
    base_cfg = default_config()
    _persist_config(dirs["artifacts"] / "baseline_config.json", base_cfg)

    baseline_result = None
    if cfg.run_baseline:
        baseline_result = train_and_evaluate(base_cfg, out_dir=dirs["baseline"])
    else:
        baseline_result = _load_run(dirs["baseline"])

    ideas = novelty_filter(
        generate_ideas(
            num_ideas=cfg.num_ideas,
            default_cfg=asdict(base_cfg),
            model=cfg.gpt_model,
            provider=cfg.provider,
        )
    )
    ideas_path = dirs["artifacts"] / "ideas.json"
    ideas_path.write_text(json.dumps(ideas, indent=2), encoding="utf-8")

    candidate_results: list[dict[str, Any]] = []
    for idx, idea in enumerate(ideas, start=1):
        idea_dir = dirs["runs"] / f"idea_{idx:02d}"
        candidate_cfg = apply_patch(base_cfg, idea.get("patch", {}))
        _persist_config(idea_dir / "config.json", candidate_cfg)
        candidate_result = train_and_evaluate(candidate_cfg, out_dir=idea_dir)
        candidate_result["idea"] = idea
        candidate_result["run_dir"] = str(idea_dir)
        candidate_results.append(candidate_result)

    best = min(candidate_results, key=lambda item: item["metrics"]["final_val_loss"])
    save_learning_curve(best["history"], dirs["artifacts"] / "best_learning_curve.png")

    delta = best["metrics"]["final_val_loss"] - baseline_result["metrics"]["final_val_loss"]
    summary_metrics = {
        "baseline_val_loss": baseline_result["metrics"]["final_val_loss"],
        "best_val_loss": best["metrics"]["final_val_loss"],
        "delta_val_loss": delta,
        "baseline_train_loss": baseline_result["metrics"]["final_train_loss"],
        "best_train_loss": best["metrics"]["final_train_loss"],
    }
    (dirs["artifacts"] / "summary.json").write_text(json.dumps(summary_metrics, indent=2), encoding="utf-8")

    report = write_report(
        best["idea"],
        baseline_result,
        best,
        model=cfg.gpt_model,
        provider=cfg.provider,
    )
    report_path = dirs["artifacts"] / "report.md"
    save_report(report, report_path)
    review = review_report(
        report,
        metrics=summary_metrics,
        model=cfg.gpt_model,
        provider=cfg.provider,
    )
    save_review(review, dirs["artifacts"] / "review.json")

    return {
        "workspace": str(cfg.workspace),
        "baseline": baseline_result,
        "best_candidate": best,
        "summary_metrics": summary_metrics,
        "report_path": str(report_path),
        "review": review,
        "ideas": ideas,
    }
