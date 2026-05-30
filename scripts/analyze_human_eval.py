from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


SCORE_FIELDS = [
    "overall_quality",
    "scientific_validity",
    "claim_grounding",
    "reproducibility",
    "novelty_calibration",
    "overclaim_risk",
]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if not 1 <= number <= 5:
        return None
    return number


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    x_mean = mean(xs)
    y_mean = mean(ys)
    x_den = math.sqrt(sum((x - x_mean) ** 2 for x in xs))
    y_den = math.sqrt(sum((y - y_mean) ** 2 for y in ys))
    if x_den == 0 or y_den == 0:
        return None
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / (x_den * y_den)


def _rank(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j][1] == ordered[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[ordered[k][0]] = avg_rank
        i = j
    return ranks


def _spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    return _pearson(_rank(xs), _rank(ys))


def _artifact_id(method: str, seed: int, task_id: str) -> str:
    import hashlib

    digest = hashlib.sha256(f"{method}:{seed}:{task_id}".encode("utf-8")).hexdigest()
    return digest[:12]


def _load_judge_scores(path: Path | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if "records" in data:
        rows = data["records"]
        score_key = "quality"
    else:
        rows = data.get("evaluations", [])
        score_key = "overall_quality"
    scores: dict[str, dict[str, Any]] = {}
    for row in rows:
        method = str(row.get("method", ""))
        task_id = str(row.get("task_id", ""))
        try:
            seed = int(row.get("seed", 0))
        except (TypeError, ValueError):
            continue
        artifact_id = _artifact_id(method, seed, task_id)
        score = row.get(score_key)
        if score is None:
            score = row.get("mean_quality")
        scores[artifact_id] = {
            "model_quality": score,
            "model_rubric_score": row.get("rubric_score"),
            "model_method": method,
            "model_seed": seed,
            "model_task_id": task_id,
        }
    return scores


def _summarize_values(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "mean": None, "std": None}
    return {
        "n": len(values),
        "mean": round(mean(values), 4),
        "std": round(pstdev(values), 4) if len(values) > 1 else 0.0,
    }


def analyze(
    completed_csv: Path,
    key_csv: Path,
    output_dir: Path,
    judge_json: Path | None = None,
) -> dict[str, Any]:
    completed_rows = _read_csv(completed_csv)
    key_by_id = {row["artifact_id"]: row for row in _read_csv(key_csv)}
    judge_by_id = _load_judge_scores(judge_json)

    joined: list[dict[str, Any]] = []
    missing_scores: list[str] = []
    invalid_scores: list[dict[str, str]] = []
    unknown_artifacts: list[str] = []
    for row in completed_rows:
        artifact_id = row.get("artifact_id", "").strip()
        key = key_by_id.get(artifact_id)
        if not key:
            unknown_artifacts.append(artifact_id)
            continue
        parsed: dict[str, float] = {}
        missing_or_invalid = False
        for field in SCORE_FIELDS:
            value = _to_float(row.get(field))
            if value is None:
                missing_or_invalid = True
                invalid_scores.append({"artifact_id": artifact_id, "field": field, "value": row.get(field, "")})
            else:
                parsed[field] = value
        if missing_or_invalid:
            missing_scores.append(artifact_id)
            continue
        joined_row: dict[str, Any] = {
            "artifact_id": artifact_id,
            "method": key["method"],
            "seed": int(key["seed"]),
            "task_id": key["task_id"],
            "rubric_score": float(key["rubric_score"]),
            "notes": row.get("notes", ""),
            **parsed,
        }
        joined_row.update(judge_by_id.get(artifact_id, {}))
        joined.append(joined_row)

    by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in joined:
        by_method[row["method"]].append(row)
    method_summary: list[dict[str, Any]] = []
    for method, rows in sorted(by_method.items()):
        summary: dict[str, Any] = {"method": method, "n": len(rows)}
        for field in SCORE_FIELDS:
            values = [float(row[field]) for row in rows]
            stats = _summarize_values(values)
            summary[f"mean_{field}"] = stats["mean"]
            summary[f"std_{field}"] = stats["std"]
        summary["mean_rubric_score"] = round(mean(float(row["rubric_score"]) for row in rows), 4) if rows else None
        method_summary.append(summary)

    by_pair: dict[tuple[int, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in joined:
        by_pair[(int(row["seed"]), str(row["task_id"]))][str(row["method"])] = row
    paired_deltas: list[dict[str, Any]] = []
    for (seed, task_id), methods in sorted(by_pair.items()):
        if "single_fixed" not in methods or "multi_fixed" not in methods:
            continue
        single = methods["single_fixed"]
        multi = methods["multi_fixed"]
        delta = float(multi["overall_quality"]) - float(single["overall_quality"])
        paired_deltas.append(
            {
                "seed": seed,
                "task_id": task_id,
                "single_artifact_id": single["artifact_id"],
                "multi_artifact_id": multi["artifact_id"],
                "single_overall_quality": single["overall_quality"],
                "multi_overall_quality": multi["overall_quality"],
                "delta_multi_minus_single": delta,
            }
        )
    wins = sum(1 for row in paired_deltas if row["delta_multi_minus_single"] > 0)
    ties = sum(1 for row in paired_deltas if row["delta_multi_minus_single"] == 0)
    losses = sum(1 for row in paired_deltas if row["delta_multi_minus_single"] < 0)

    human_quality = [float(row["overall_quality"]) for row in joined]
    rubric_scores = [float(row["rubric_score"]) for row in joined]
    model_pairs = [
        (float(row["overall_quality"]), float(row["model_quality"]))
        for row in joined
        if row.get("model_quality") is not None
    ]
    model_human = [item[0] for item in model_pairs]
    model_quality = [item[1] for item in model_pairs]

    result = {
        "completed_csv": str(completed_csv),
        "key_csv": str(key_csv),
        "judge_json": str(judge_json) if judge_json else None,
        "annotated_count": len(joined),
        "expected_count": len(key_by_id),
        "missing_or_invalid_count": len(set(missing_scores)),
        "unknown_artifact_count": len(unknown_artifacts),
        "invalid_scores": invalid_scores,
        "unknown_artifacts": unknown_artifacts,
        "method_summary": method_summary,
        "paired_summary": {
            "paired_count": len(paired_deltas),
            "mean_delta_multi_minus_single": round(mean(row["delta_multi_minus_single"] for row in paired_deltas), 4)
            if paired_deltas
            else None,
            "wins": wins,
            "ties": ties,
            "losses": losses,
        },
        "paired_deltas": paired_deltas,
        "correlations": {
            "human_overall_vs_structural_rubric": {
                "n": len(human_quality),
                "pearson": None if _pearson(human_quality, rubric_scores) is None else round(_pearson(human_quality, rubric_scores), 4),
                "spearman": None if _spearman(human_quality, rubric_scores) is None else round(_spearman(human_quality, rubric_scores), 4),
            },
            "human_overall_vs_model_quality": {
                "n": len(model_pairs),
                "pearson": None if _pearson(model_human, model_quality) is None else round(_pearson(model_human, model_quality), 4),
                "spearman": None if _spearman(model_human, model_quality) is None else round(_spearman(model_human, model_quality), 4),
            },
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "human_eval_summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_markdown(result, output_dir / "human_eval_summary.md")
    return result


def _write_markdown(result: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# Human Evaluation Summary",
        "",
        f"- Annotated artifacts: {result['annotated_count']} / {result['expected_count']}",
        f"- Missing or invalid artifacts: {result['missing_or_invalid_count']}",
        f"- Unknown artifact IDs: {result['unknown_artifact_count']}",
        "",
        "## Method Summary",
        "",
        "| Method | n | Overall | Scientific | Grounding | Reproducibility | Novelty | Overclaim risk | Rubric |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["method_summary"]:
        lines.append(
            "| {method} | {n} | {overall} | {validity} | {grounding} | {repro} | {novelty} | {risk} | {rubric} |".format(
                method=row["method"],
                n=row["n"],
                overall=row.get("mean_overall_quality"),
                validity=row.get("mean_scientific_validity"),
                grounding=row.get("mean_claim_grounding"),
                repro=row.get("mean_reproducibility"),
                novelty=row.get("mean_novelty_calibration"),
                risk=row.get("mean_overclaim_risk"),
                rubric=row.get("mean_rubric_score"),
            )
        )
    paired = result["paired_summary"]
    lines.extend(
        [
            "",
            "## Paired Single-vs-Multi Summary",
            "",
            f"- Paired comparisons: {paired['paired_count']}",
            f"- Mean delta, multi minus single: {paired['mean_delta_multi_minus_single']}",
            f"- Wins/ties/losses for multi_fixed: {paired['wins']} / {paired['ties']} / {paired['losses']}",
            "",
            "## Correlations",
            "",
        ]
    )
    for name, row in result["correlations"].items():
        lines.append(f"- `{name}`: n={row['n']}, Pearson={row['pearson']}, Spearman={row['spearman']}")
    lines.append("")
    if result["missing_or_invalid_count"]:
        lines.extend(["## Missing Or Invalid Rows", ""])
        seen = sorted({entry["artifact_id"] for entry in result["invalid_scores"]})
        for artifact_id in seen[:40]:
            lines.append(f"- `{artifact_id}`")
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--completed-csv", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--judge-json", type=Path)
    args = parser.parse_args()
    result = analyze(args.completed_csv, args.key, args.output_dir, args.judge_json)
    print(json.dumps({"annotated_count": result["annotated_count"], "output_dir": str(args.output_dir)}, indent=2))


if __name__ == "__main__":
    main()
