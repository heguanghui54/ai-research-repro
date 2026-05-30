from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

from .artifact_quality_judge import _pearson, _rank


def _key(item: dict[str, Any]) -> tuple[str, int, str]:
    return (str(item.get("method", "")), int(item.get("seed", -1)), str(item.get("task_id", "")))


def compare_judges(*, judge_a_path: Path, judge_b_path: Path, output_dir: Path, output_prefix: str = "artifact_quality_judge_comparison") -> dict[str, Any]:
    judge_a = json.loads(judge_a_path.read_text(encoding="utf-8"))
    judge_b = json.loads(judge_b_path.read_text(encoding="utf-8"))
    a_map = {_key(item): item for item in judge_a.get("evaluations", [])}
    b_map = {_key(item): item for item in judge_b.get("evaluations", [])}
    keys = sorted(set(a_map) & set(b_map))
    pairs = []
    for key in keys:
        a = a_map[key]
        b = b_map[key]
        pairs.append(
            {
                "method": key[0],
                "seed": key[1],
                "task_id": key[2],
                "judge_a_quality": float(a.get("overall_quality", 0)),
                "judge_b_quality": float(b.get("overall_quality", 0)),
                "delta_b_minus_a": float(b.get("overall_quality", 0)) - float(a.get("overall_quality", 0)),
                "judge_a_risk": a.get("overclaim_risk", ""),
                "judge_b_risk": b.get("overclaim_risk", ""),
            }
        )
    a_scores = [row["judge_a_quality"] for row in pairs]
    b_scores = [row["judge_b_quality"] for row in pairs]
    by_method: dict[str, list[dict[str, Any]]] = {}
    for row in pairs:
        by_method.setdefault(row["method"], []).append(row)
    method_rows = []
    for method, rows in sorted(by_method.items()):
        deltas = [row["delta_b_minus_a"] for row in rows]
        method_rows.append(
            {
                "method": method,
                "n": len(rows),
                "mean_judge_a_quality": round(statistics.mean(row["judge_a_quality"] for row in rows), 4),
                "mean_judge_b_quality": round(statistics.mean(row["judge_b_quality"] for row in rows), 4),
                "mean_delta_b_minus_a": round(statistics.mean(deltas), 4),
            }
        )
    result = {
        "judge_a_path": str(judge_a_path),
        "judge_b_path": str(judge_b_path),
        "judge_a_model": judge_a.get("model", ""),
        "judge_b_model": judge_b.get("model", ""),
        "matched_artifact_count": len(pairs),
        "pearson_quality": _pearson(a_scores, b_scores),
        "spearman_quality": _pearson(_rank(a_scores), _rank(b_scores)),
        "mean_delta_b_minus_a": round(statistics.mean(row["delta_b_minus_a"] for row in pairs), 4) if pairs else 0.0,
        "method_summary": method_rows,
        "pairs": pairs,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{output_prefix}.json"
    md_path = output_dir / f"{output_prefix}.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_path.write_text(comparison_to_markdown(result), encoding="utf-8")
    result["paths"] = {"json": str(json_path), "markdown": str(md_path)}
    return result


def comparison_to_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Artifact Quality Judge Comparison",
        "",
        f"- Judge A: `{result.get('judge_a_model', '')}`",
        f"- Judge B: `{result.get('judge_b_model', '')}`",
        f"- Matched artifacts: {result.get('matched_artifact_count', 0)}",
        f"- Pearson quality agreement: {result.get('pearson_quality')}",
        f"- Spearman quality agreement: {result.get('spearman_quality')}",
        f"- Mean B-A quality delta: {result.get('mean_delta_b_minus_a')}",
        "",
        "## Method Summary",
        "",
        "| Method | N | Judge A Mean | Judge B Mean | B-A Delta |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in result.get("method_summary", []):
        lines.append(
            f"| `{row['method']}` | {row['n']} | {row['mean_judge_a_quality']:.3f} | "
            f"{row['mean_judge_b_quality']:.3f} | {row['mean_delta_b_minus_a']:.3f} |"
        )
    return "\n".join(lines).rstrip() + "\n"
