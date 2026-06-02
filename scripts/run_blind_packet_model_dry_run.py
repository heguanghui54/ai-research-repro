#!/usr/bin/env python3
"""Run a model-only dry run of the human-expert blind review packet.

This script validates the blind-review collection and summarization pipeline
before real experts are recruited. It must not be reported as human evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3" / "experiments" / "human_expert_blind_review_packet_20260602_143000"
DEFAULT_OUT = PACKET_DIR / "model_blind_review_dry_run_20260603"

RUBRIC_FIELDS = [
    "problem_framing",
    "method_specificity",
    "experiment_design",
    "limitation_honesty",
    "claim_calibration",
    "overall_quality",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _call_model(model: str, prompt: str, max_tokens: int) -> dict[str, Any]:
    base_url = os.environ.get("MONICA_BASE_URL", "https://openapi.monica.im/v1").rstrip("/")
    api_key = os.environ["MONICA_API_KEY"]
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are simulating an ML/AI expert reviewer for a blind A/B packet dry run. "
                        "Return strict JSON only. Do not infer hidden condition names."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens,
        },
        timeout=180,
    )
    try:
        payload = response.json()
    except ValueError:
        payload = {"error": "non_json_response", "text_excerpt": response.text[:2000]}
    return {"model": model, "status_code": response.status_code, "response": payload}


def _content(payload: dict[str, Any]) -> str:
    try:
        return str(payload["response"]["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError):
        return json.dumps(payload.get("response"), ensure_ascii=False)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def _prompt(pair_text: str) -> str:
    return f"""Score the following anonymized A/B mini-paper pair.

You must not guess which side is produced by which condition. Judge only the
visible text. Use integer scores from 1 to 5, where 5 is best.

Rubric fields:
- problem_framing: clarity and scientific importance of the problem framing
- method_specificity: specificity and plausibility of the proposed method
- experiment_design: concreteness and informativeness of the experiment plan
- limitation_honesty: honesty and usefulness of limitations
- claim_calibration: whether claims are bounded by evidence
- overall_quality: overall value as a research artifact

Return JSON with exactly this schema:
{{
  "winner": "A" | "B" | "tie",
  "A_problem_framing": 1,
  "A_method_specificity": 1,
  "A_experiment_design": 1,
  "A_limitation_honesty": 1,
  "A_claim_calibration": 1,
  "A_overall_quality": 1,
  "B_problem_framing": 1,
  "B_method_specificity": 1,
  "B_experiment_design": 1,
  "B_limitation_honesty": 1,
  "B_claim_calibration": 1,
  "B_overall_quality": 1,
  "rationale": "one or two sentences"
}}

Blind pair:

{pair_text}
"""


def _coerce_score(value: Any) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        return 3
    return max(1, min(5, score))


def _row_from_result(reviewer_id: str, pair_id: str, result: dict[str, Any]) -> dict[str, str]:
    winner = str(result.get("winner", "tie")).strip()
    if winner not in {"A", "B", "tie"}:
        winner = "tie"
    row: dict[str, str] = {"reviewer_id": reviewer_id, "pair_id": pair_id, "winner": winner}
    for side in ("A", "B"):
        for field in RUBRIC_FIELDS:
            row[f"{side}_{field}"] = str(_coerce_score(result.get(f"{side}_{field}")))
    row["rationale"] = str(result.get("rationale", "")).replace("\n", " ").strip()
    return row


def _write_manifest_update(out_dir: Path, summary: dict[str, Any], generated: list[Path]) -> None:
    manifest_path = ROOT / "docs" / "co_pilot_ai_scientist_v3" / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    manifest["model_blind_review_dry_run"] = {
        "status": summary["status"],
        "output_dir": _rel(out_dir),
        "score_csv": _rel(out_dir / "model_score_sheet.csv"),
        "analysis_json": _rel(out_dir / "analysis" / "summary.json"),
        "analysis_markdown": _rel(out_dir / "analysis" / "summary.md"),
        "claim_boundary": "Model-only dry run; not independent human expert evidence.",
    }
    for path in [Path(__file__), *generated]:
        rel = _rel(path)
        if rel not in manifest["current_artifacts"]:
            manifest["current_artifacts"].append(rel)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", default=["gpt-4o-mini", "gemini-2.5-flash"])
    parser.add_argument("--packet-dir", type=Path, default=PACKET_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--max-tokens", type=int, default=2000)
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    packet_dir = args.packet_dir if args.packet_dir.is_absolute() else ROOT / args.packet_dir
    out_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "raw_model_outputs"
    raw_dir.mkdir(parents=True, exist_ok=True)

    pair_paths = sorted((packet_dir / "pairs").glob("pair_*.md"))
    fieldnames = [
        "reviewer_id",
        "pair_id",
        "winner",
        *[f"{side}_{field}" for side in ("A", "B") for field in RUBRIC_FIELDS],
        "rationale",
    ]
    rows: list[dict[str, str]] = []
    raw_records: list[dict[str, Any]] = []

    for model in args.models:
        reviewer_id = f"model_{model.replace('-', '_').replace('.', '_')}"
        for pair_path in pair_paths:
            pair_id = pair_path.stem
            payload = _call_model(model, _prompt(_read(pair_path)), args.max_tokens)
            raw_path = raw_dir / f"{reviewer_id}_{pair_id}.json"
            raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            try:
                result = _extract_json(_content(payload))
                rows.append(_row_from_result(reviewer_id, pair_id, result))
                parse_status = "parsed"
            except Exception as exc:  # noqa: BLE001 - archive parse failures for auditability.
                parse_status = f"parse_failed:{type(exc).__name__}:{exc}"
            raw_records.append(
                {
                    "reviewer_id": reviewer_id,
                    "model": model,
                    "pair_id": pair_id,
                    "status_code": payload["status_code"],
                    "parse_status": parse_status,
                    "raw_path": _rel(raw_path),
                }
            )

    score_csv = out_dir / "model_score_sheet.csv"
    with score_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    analysis_dir = out_dir / "analysis"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "summarize_human_expert_blind_reviews.py"),
            "--score-csv",
            str(score_csv),
            "--condition-key",
            str(packet_dir / "condition_key.json"),
            "--output-dir",
            str(analysis_dir),
        ],
        cwd=ROOT,
        check=True,
    )
    analysis = _load_json(analysis_dir / "summary.json")
    analysis["status"] = "model_only_dry_run_not_human_evidence"
    analysis["claim_boundary"] = (
        "This is a model-only blind packet dry run that validates the collection "
        "and summarization pipeline. It is not independent human expert evidence."
    )
    (analysis_dir / "summary.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = (analysis_dir / "summary.md").read_text(encoding="utf-8")
    md = md.replace("Human Expert Blind Review Summary", "Model-Only Blind Packet Dry-Run Summary")
    md = md.replace("- Status: `human_scores_summarized`", "- Status: `model_only_dry_run_not_human_evidence`")
    md = md.replace("- Status: `no_valid_rows`", "- Status: `model_only_dry_run_not_human_evidence`")
    md += "\n## Model-Only Boundary\n\nThis dry run is not independent human expert evidence.\n"
    (analysis_dir / "summary.md").write_text(md, encoding="utf-8")

    run_summary = {
        "created_at": _utc_now(),
        "status": "model_only_dry_run_not_human_evidence",
        "packet_dir": _rel(packet_dir),
        "output_dir": _rel(out_dir),
        "models": args.models,
        "pair_count": len(pair_paths),
        "parsed_rows": len(rows),
        "raw_records": raw_records,
        "analysis": {
            "json": _rel(analysis_dir / "summary.json"),
            "markdown": _rel(analysis_dir / "summary.md"),
            "win_counts": analysis.get("win_counts"),
            "mean_delta": analysis.get("mean_delta"),
            "positive_evidence_threshold_met": analysis.get("positive_evidence_threshold_met"),
        },
        "claim_boundary": "Model-only dry run; not independent human expert evidence.",
    }
    summary_path = out_dir / "README.md"
    summary_json = out_dir / "run_summary.json"
    summary_json.write_text(json.dumps(run_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(
        "\n".join(
            [
                "# Model-Only Blind Packet Dry Run",
                "",
                f"- Status: `{run_summary['status']}`",
                f"- Models: `{', '.join(args.models)}`",
                f"- Pair count: `{len(pair_paths)}`",
                f"- Parsed score rows: `{len(rows)}`",
                f"- Score CSV: `{_rel(score_csv)}`",
                f"- Analysis JSON: `{_rel(analysis_dir / 'summary.json')}`",
                f"- Analysis Markdown: `{_rel(analysis_dir / 'summary.md')}`",
                "",
                "## Boundary",
                "",
                "This run validates the blind packet and summarization pipeline only. It is not independent human expert evidence.",
                "",
                "## Aggregate",
                "",
                f"- Win counts: `{json.dumps(analysis.get('win_counts'), ensure_ascii=False)}`",
                f"- Mean delta: `{json.dumps(analysis.get('mean_delta'), ensure_ascii=False)}`",
                f"- Positive evidence threshold met: `{analysis.get('positive_evidence_threshold_met')}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    generated = [score_csv, summary_json, summary_path, analysis_dir / "summary.json", analysis_dir / "summary.md"]
    generated.extend(raw_dir.glob("*.json"))
    if args.update_manifest:
        _write_manifest_update(out_dir, run_summary, generated)

    print(json.dumps({"status": run_summary["status"], "output_dir": _rel(out_dir), "rows": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
