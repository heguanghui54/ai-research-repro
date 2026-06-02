#!/usr/bin/env python3
"""Probe OpenReview human-review data as an offline scientific-taste prior.

This script uses the Hugging Face Dataset Viewer API, not a full local dataset
download. It checks that a public expert-review dataset exposes the fields
needed to build a limited human scientific taste proxy: review text, acceptance
decision, and normalized review dimensions such as novelty, clarity, impact,
correctness, reproducibility, and mean score.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib import parse, request


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
DATASET = "nhop/OpenReview"
CONFIG = "default"
SPLIT = "train"
BASE_URL = "https://datasets-server.huggingface.co"
SCORE_FIELDS = [
    "mean_score",
    "mean_novelty",
    "mean_correctness",
    "mean_clarity",
    "mean_impact",
    "mean_reproducibility",
    "mean_confidence",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _get(endpoint: str, **params: str | int) -> dict[str, Any]:
    query = parse.urlencode(params)
    url = f"{BASE_URL}/{endpoint}?{query}"
    last_error: str | None = None
    for attempt in range(3):
        try:
            with request.urlopen(url, timeout=20) as resp:  # noqa: S310 - fixed HTTPS endpoint.
                data = json.loads(resp.read().decode("utf-8"))
            data["_url"] = url
            return data
        except (HTTPError, URLError) as exc:
            last_error = repr(exc)
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Dataset Viewer request failed after retries: {url} :: {last_error}")


def _stream_rows(dataset: str, config: str, split: str, limit: int) -> list[dict[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError as exc:  # pragma: no cover - dependency availability varies.
        raise RuntimeError("datasets is required for --streaming mode") from exc

    stream = load_dataset(dataset, config, split=split, streaming=True)
    rows = []
    for row in stream:
        rows.append(dict(row))
        if len(rows) >= limit:
            break
    return rows


def _review_text(review: Any) -> str:
    if isinstance(review, str):
        return review
    if isinstance(review, dict):
        for key in ["main_review", "review", "summary", "paper_summary", "strengths", "weaknesses"]:
            value = review.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return json.dumps(review, ensure_ascii=False)[:800]
    return ""


def _compact_row(row: dict[str, Any]) -> dict[str, Any]:
    reviews = row.get("reviews") or []
    review_snippets = []
    for review in reviews[:3]:
        text = _review_text(review)
        if text:
            review_snippets.append(text[:700])
    compact = {
        "title": row.get("title"),
        "venue": row.get("venue"),
        "arxiv_id": row.get("arxiv_id"),
        "decision": row.get("decision"),
        "decision_text_excerpt": (row.get("decision_text") or "")[:700],
        "abstract_excerpt": (row.get("abstract") or "")[:900],
        "review_snippets": review_snippets,
    }
    for field in SCORE_FIELDS:
        compact[field] = row.get(field)
    return compact


def _numeric(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _mean(values: list[float]) -> float | None:
    return round(statistics.fmean(values), 4) if values else None


def _score_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {}
    for field in SCORE_FIELDS:
        values = [_numeric(row.get(field)) for row in rows]
        clean = [value for value in values if value is not None]
        summary[field] = {
            "available": len(clean),
            "mean": _mean(clean),
            "min": round(min(clean), 4) if clean else None,
            "max": round(max(clean), 4) if clean else None,
        }
    return summary


def _protocol_markdown(summary: dict[str, Any]) -> str:
    return f"""# Expert-Review Taste Prior Protocol

This protocol uses public OpenReview human-review data as an offline proxy for
scientific taste and insight. It is a limited prior, not a replacement for live
human co-pilot participation.

## Dataset

- Dataset: [{summary['dataset']}](https://huggingface.co/datasets/{summary['dataset']})
- Config/split: `{summary['config']}` / `{summary['split']}`
- Rows reported by Dataset Viewer statistics: `{summary['num_examples']}`
- Probe sample size: `{summary['sample_size']}`

The useful fields are `reviews`, `decision`, `decision_text`, `mean_score`,
`mean_novelty`, `mean_correctness`, `mean_clarity`, `mean_impact`, and
`mean_reproducibility`.

## How To Use It In IGRE

1. Retrieve papers near a candidate research direction by title/abstract
   similarity or metadata filters.
2. Convert high-scoring accepted papers into positive taste exemplars:
   problem framing, novelty signals, clarity patterns, reproducibility cues,
   and reviewer-noted strengths.
3. Convert low-scoring or rejected papers into negative taste exemplars:
   weak motivation, missing ablations, unclear claims, insufficient evidence,
   and reviewer-noted weaknesses.
4. Inject the resulting exemplars into the `scientific_taste_prior` gate before
   expensive AI Scientist-v2 branch search.
5. Evaluate whether review-prior guidance improves manuscript quality under a
   matched budget against autonomous AI Scientist-v2 and unguided IGRE.

## Minimal Experiment

- Task: generate or revise manuscripts for the same archived experiment traces.
- Baselines: autonomous manuscript generation, IGRE without review prior, IGRE
  with OpenReview-derived taste prior.
- Metrics: model-review rubric, human expert review when available, claim
  calibration, clarity, novelty, reproducibility, and benchmark-result honesty.
- Leakage control: never retrieve reviews for the exact target paper; use
  temporal and topic splits when training or selecting exemplars.

## Claim Boundary

This dataset can support the claim that public expert-review corpora can be
operationalized as an offline scientific-taste prior. It cannot by itself prove
that live human co-pilot participation improves research quality.
"""


def _markdown(summary: dict[str, Any]) -> str:
    high = summary["high_score_examples"]
    low = summary["low_score_examples"]
    lines = [
        "# Expert-Review Taste Prior Probe",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Dataset: `{summary['dataset']}`",
        f"- Config/split: `{summary['config']}` / `{summary['split']}`",
        f"- Dataset rows from statistics: `{summary['num_examples']}`",
        f"- Sample size: `{summary['sample_size']}`",
        f"- Required fields available: `{summary['required_fields_available']}`",
        "",
        "## Interpretation",
        "",
        summary["interpretation"],
        "",
        "## Score Field Coverage In Sample",
        "",
        "| Field | Available | Mean | Min | Max |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for field, stats in summary["score_summary"].items():
        lines.append(
            f"| {field} | {stats['available']} | {stats['mean']} | {stats['min']} | {stats['max']} |"
        )
    lines.extend(["", "## High-Score Examples", ""])
    for row in high:
        lines.append(f"- `{row.get('mean_score')}` | {row.get('title')} | decision={row.get('decision')}")
    lines.extend(["", "## Low-Score Examples", ""])
    for row in low:
        lines.append(f"- `{row.get('mean_score')}` | {row.get('title')} | decision={row.get('decision')}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This probe verifies data availability and a feasible offline taste-prior",
            "construction. It is not yet an experiment showing that the prior improves",
            "AI Scientist-v2 outputs.",
        ]
    )
    return "\n".join(lines) + "\n"


def _write(path: Path, text: str) -> str:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return _rel(path)


def _update_manifest(paths: list[str], summary: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        if path not in artifacts:
            artifacts.append(path)
    manifest["status"] = "pilot_package_with_expert_review_taste_prior_probe"
    manifest["expert_review_taste_prior_probe"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "dataset": summary["dataset"],
        "sample_size": summary["sample_size"],
        "required_fields_available": summary["required_fields_available"],
        "claim_boundary": "Offline expert-review taste proxy only; not proof of live human co-pilot improvement.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=f"expert_review_taste_prior_probe_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--dataset", default=DATASET)
    parser.add_argument("--config", default=CONFIG)
    parser.add_argument("--split", default=SPLIT)
    parser.add_argument("--offsets", nargs="+", type=int, default=[0, 100, 500])
    parser.add_argument("--length", type=int, default=40)
    parser.add_argument("--streaming", action="store_true")
    parser.add_argument("--stream-limit", type=int, default=160)
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    out_dir = Path(args.output_dir) if args.output_dir else DOC_DIR / "experiments" / args.run_id
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    is_valid = _get("is-valid", dataset=args.dataset)
    splits = _get("splits", dataset=args.dataset)
    first_rows = _get("first-rows", dataset=args.dataset, config=args.config, split=args.split)
    statistics_payload = _get("statistics", dataset=args.dataset, config=args.config, split=args.split)

    rows: list[dict[str, Any]] = []
    row_pages = []
    sampling_mode = "streaming" if args.streaming else "dataset_viewer_rows"
    if args.streaming:
        try:
            rows = _stream_rows(args.dataset, args.config, args.split, args.stream_limit)
            row_pages.append({"mode": "streaming", "num_rows": len(rows), "stream_limit": args.stream_limit})
        except RuntimeError as exc:
            row_pages.append({"mode": "streaming", "num_rows": 0, "error": str(exc)})
    if not rows:
        sampling_mode = "dataset_viewer_rows"
        for offset in args.offsets:
            try:
                page = _get(
                    "rows",
                    dataset=args.dataset,
                    config=args.config,
                    split=args.split,
                    offset=offset,
                    length=min(args.length, 100),
                )
                row_pages.append({"offset": offset, "num_rows": len(page.get("rows", [])), "url": page.get("_url")})
                rows.extend([item["row"] for item in page.get("rows", [])])
            except RuntimeError as exc:
                row_pages.append({"offset": offset, "num_rows": 0, "error": str(exc)})

    compact_rows = [_compact_row(row) for row in rows]
    required = [
        "title",
        "abstract",
        "reviews",
        "decision",
        "mean_score",
        "mean_novelty",
        "mean_clarity",
        "mean_impact",
        "mean_reproducibility",
    ]
    feature_names = {feature["name"] for feature in first_rows.get("features", [])}
    required_fields_available = all(field in feature_names for field in required)
    scored = [row for row in compact_rows if _numeric(row.get("mean_score")) is not None]
    high = sorted(scored, key=lambda row: row["mean_score"], reverse=True)[:5]
    low = sorted(scored, key=lambda row: row["mean_score"])[:5]

    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "expert_review_taste_prior_data_probe",
        "dataset": args.dataset,
        "config": args.config,
        "split": args.split,
        "dataset_url": f"https://huggingface.co/datasets/{args.dataset}",
        "dataset_viewer_base_url": BASE_URL,
        "is_valid": {key: value for key, value in is_valid.items() if key != "_url"},
        "splits": splits.get("splits", []),
        "num_examples": statistics_payload.get("num_examples"),
        "feature_names": sorted(feature_names),
        "required_fields": required,
        "required_fields_available": required_fields_available,
        "offsets": args.offsets,
        "sampling_mode": sampling_mode,
        "stream_limit": args.stream_limit if args.streaming else None,
        "row_pages": row_pages,
        "sample_size": len(compact_rows),
        "score_summary": _score_summary(compact_rows),
        "high_score_examples": high,
        "low_score_examples": low,
        "interpretation": (
            "The public OpenReview dataset exposes enough expert-review fields "
            "to build a limited offline scientific-taste prior for IGRE. It can "
            "guide hypothesis selection or manuscript revision, but it cannot "
            "replace live human co-pilot interventions or prove performance gains."
        ),
        "summary_path": _rel(out_dir / "summary.json"),
    }
    paths = [
        _write(out_dir / "dataset_availability.json", json.dumps({"is_valid": is_valid, "splits": splits}, ensure_ascii=False, indent=2)),
        _write(out_dir / "dataset_statistics_excerpt.json", json.dumps(statistics_payload, ensure_ascii=False, indent=2)[:20000]),
        _write(out_dir / "sample_rows_compact.json", json.dumps(compact_rows, ensure_ascii=False, indent=2)),
        _write(out_dir / "high_score_examples.json", json.dumps(high, ensure_ascii=False, indent=2)),
        _write(out_dir / "low_score_examples.json", json.dumps(low, ensure_ascii=False, indent=2)),
        _write(out_dir / "expert_review_taste_prior_protocol.md", _protocol_markdown(summary)),
        _write(out_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2)),
        _write(out_dir / "README.md", _markdown(summary)),
    ]
    summary["artifacts"] = paths
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _update_manifest(paths + ["scripts/run_expert_review_taste_prior_probe.py"], summary)
    print(json.dumps({"summary": summary["summary_path"], "sample_size": summary["sample_size"]}, indent=2))


if __name__ == "__main__":
    main()
