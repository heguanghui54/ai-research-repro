from __future__ import annotations

import json
import re
import statistics
from pathlib import Path
from typing import Any

from .artifact_quality_judge import _pearson, _rank
from .quality_primary_analysis import BASELINE_METHOD


_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]+")
_RISK_TERMS = ("fallback", "simulated", "placeholder", "hypothesis", "planned", "pending", "not executed")
_HEDGE_TERMS = ("may", "might", "could", "should", "would", "likely", "possibly", "preliminary")


def _key(method: str, seed: int, task_id: str) -> tuple[str, int, str]:
    return (str(method), int(seed), str(task_id))


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text)]


def _safe_mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _safe_std(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def _answer_text(answer: Any) -> str:
    return json.dumps(answer, ensure_ascii=False, sort_keys=True)


def _feature_row(task_result: dict[str, Any]) -> dict[str, Any]:
    answer = task_result.get("answer", {})
    method_value = task_result.get("method", "")
    if isinstance(method_value, dict):
        method_value = method_value.get("name", "")
    text = _answer_text(answer)
    lower = text.lower()
    tokens = _tokens(text)
    unique_tokens = set(tokens)
    claim_rows = answer.get("claim_evidence_table", [])
    if not isinstance(claim_rows, list):
        claim_rows = []
    limitations = answer.get("limitations", [])
    if not isinstance(limitations, list):
        limitations = []
    commands = answer.get("reproducibility_commands", [])
    if not isinstance(commands, list):
        commands = []
    score = task_result.get("score", {})
    token_count = len(tokens)
    return {
        "method": str(method_value),
        "seed": int(task_result.get("seed", -1)),
        "task_id": str(task_result.get("task", {}).get("task_id", "")),
        "rubric_score": float(score.get("score", 0) or 0),
        "estimated_output_chars": float(task_result.get("estimated_output_chars", len(text)) or len(text)),
        "json_chars": float(len(text)),
        "token_count": float(token_count),
        "unique_token_ratio": round(len(unique_tokens) / token_count, 4) if token_count else 0.0,
        "claim_rows": float(len(claim_rows)),
        "limitations_count": float(len(limitations)),
        "command_count": float(len(commands)),
        "nonfinal_claim_rows": float(score.get("nonfinal_claim_rows", 0) or 0),
        "final_claim_rows": float(score.get("final_claim_rows", 0) or 0),
        "risk_mentions": float(score.get("risk_mentions", 0) or 0),
        "risk_term_count": float(sum(lower.count(term) for term in _RISK_TERMS)),
        "hedge_term_count": float(sum(1 for token in tokens if token in _HEDGE_TERMS)),
    }


def _quality_rows(judge_a_path: Path, judge_b_path: Path) -> dict[tuple[str, int, str], dict[str, Any]]:
    judge_a = json.loads(judge_a_path.read_text(encoding="utf-8"))
    judge_b = json.loads(judge_b_path.read_text(encoding="utf-8"))
    a_map = {
        _key(item.get("method", ""), item.get("seed", -1), item.get("task_id", "")): item
        for item in judge_a.get("evaluations", [])
    }
    b_map = {
        _key(item.get("method", ""), item.get("seed", -1), item.get("task_id", "")): item
        for item in judge_b.get("evaluations", [])
    }
    rows: dict[tuple[str, int, str], dict[str, Any]] = {}
    for key in sorted(set(a_map) & set(b_map)):
        a = a_map[key]
        b = b_map[key]
        qa = float(a.get("overall_quality", 0) or 0)
        qb = float(b.get("overall_quality", 0) or 0)
        rows[key] = {
            "judge_a_quality": qa,
            "judge_b_quality": qb,
            "mean_quality": round((qa + qb) / 2.0, 4),
            "judge_disagreement_abs": round(abs(qb - qa), 4),
        }
    return rows


def analyze_quality_gap(
    *,
    results_path: Path,
    judge_a_path: Path,
    judge_b_path: Path,
    output_dir: Path,
    output_prefix: str = "quality_gap_analysis",
    baseline_method: str = BASELINE_METHOD,
) -> dict[str, Any]:
    summary = json.loads(results_path.read_text(encoding="utf-8"))
    qualities = _quality_rows(judge_a_path, judge_b_path)
    records: list[dict[str, Any]] = []
    for method_result in summary.get("results", []):
        for seed_result in method_result.get("seeds", []):
            for task_result in seed_result.get("tasks", []):
                row = _feature_row(task_result)
                quality = qualities.get(_key(row["method"], row["seed"], row["task_id"]))
                if not quality:
                    continue
                records.append({**row, **quality})

    feature_names = [
        "estimated_output_chars",
        "token_count",
        "unique_token_ratio",
        "claim_rows",
        "limitations_count",
        "command_count",
        "nonfinal_claim_rows",
        "risk_mentions",
        "risk_term_count",
        "hedge_term_count",
        "rubric_score",
    ]
    api_records = [row for row in records if row["method"] not in {"fixed_template", "author_curated_reference"}]
    correlations = {}
    for name in feature_names:
        xs = [float(row[name]) for row in api_records]
        ys = [float(row["mean_quality"]) for row in api_records]
        correlations[name] = {
            "pearson_vs_quality": _pearson(xs, ys),
            "spearman_vs_quality": _pearson(_rank(xs), _rank(ys)),
        }

    by_method: dict[str, list[dict[str, Any]]] = {}
    for row in records:
        by_method.setdefault(row["method"], []).append(row)
    baseline_by_seed_task = {
        (row["seed"], row["task_id"]): row
        for row in records
        if row["method"] == baseline_method
    }
    method_summary = []
    for method, rows in sorted(by_method.items()):
        paired_quality_deltas = []
        paired_feature_deltas = {name: [] for name in feature_names}
        for row in rows:
            baseline = baseline_by_seed_task.get((row["seed"], row["task_id"]))
            if not baseline:
                continue
            paired_quality_deltas.append(float(row["mean_quality"]) - float(baseline["mean_quality"]))
            for name in feature_names:
                paired_feature_deltas[name].append(float(row[name]) - float(baseline[name]))
        item = {
            "method": method,
            "n": len(rows),
            "mean_quality": round(_safe_mean([float(row["mean_quality"]) for row in rows]), 4),
            "std_quality": round(_safe_std([float(row["mean_quality"]) for row in rows]), 4),
            "paired_mean_quality_delta_vs_baseline": round(_safe_mean(paired_quality_deltas), 4),
            "paired_count": len(paired_quality_deltas),
        }
        for name in feature_names:
            item[f"mean_{name}"] = round(_safe_mean([float(row[name]) for row in rows]), 4)
            item[f"paired_delta_{name}_vs_baseline"] = round(_safe_mean(paired_feature_deltas[name]), 4)
        method_summary.append(item)

    result = {
        "results_path": str(results_path),
        "judge_a_path": str(judge_a_path),
        "judge_b_path": str(judge_b_path),
        "baseline_method": baseline_method,
        "matched_artifact_count": len(records),
        "feature_names": feature_names,
        "correlations_api_backed_only": correlations,
        "method_summary": method_summary,
        "records": records,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{output_prefix}.json"
    md_path = output_dir / f"{output_prefix}.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_path.write_text(quality_gap_to_markdown(result), encoding="utf-8")
    result["paths"] = {"json": str(json_path), "markdown": str(md_path)}
    return result


def quality_gap_to_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Quality Gap Diagnostic Analysis",
        "",
        f"- Matched artifacts: {result.get('matched_artifact_count', 0)}",
        f"- Baseline for paired deltas: `{result.get('baseline_method', '')}`",
        "",
        "## Method Summary",
        "",
        "| Method | N | Mean Quality | Delta Q vs Baseline | Mean Chars | Delta Chars | Mean Unique Token Ratio | Delta Nonfinal Claims | Delta Risk Terms | Delta Hedges |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result.get("method_summary", []):
        lines.append(
            f"| `{row['method']}` | {row['n']} | {row['mean_quality']:.3f} | "
            f"{row['paired_mean_quality_delta_vs_baseline']:.3f} | "
            f"{row['mean_estimated_output_chars']:.1f} | "
            f"{row['paired_delta_estimated_output_chars_vs_baseline']:.1f} | "
            f"{row['mean_unique_token_ratio']:.3f} | "
            f"{row['paired_delta_nonfinal_claim_rows_vs_baseline']:.3f} | "
            f"{row['paired_delta_risk_term_count_vs_baseline']:.3f} | "
            f"{row['paired_delta_hedge_term_count_vs_baseline']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## API-Backed Feature Correlations With Cross-Judge Quality",
            "",
            "| Feature | Pearson | Spearman |",
            "| --- | ---: | ---: |",
        ]
    )
    for name, row in result.get("correlations_api_backed_only", {}).items():
        pearson = row.get("pearson_vs_quality")
        spearman = row.get("spearman_vs_quality")
        lines.append(
            f"| `{name}` | {pearson if pearson is not None else 'NA'} | {spearman if spearman is not None else 'NA'} |"
        )
    lines.extend(
        [
            "",
            "Interpretation: this diagnostic does not prove causal mechanisms. It tests whether the quality gap is associated with observable artifact features such as verbosity, lexical diversity, non-final claims, risk language, and hedging. Large paired deltas against `single_fixed` identify concrete failure modes to inspect in traces.",
            "",
        ]
    )
    return "\n".join(lines)
