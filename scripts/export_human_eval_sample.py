from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path
from typing import Any


def _artifact_id(method: str, seed: int, task_id: str) -> str:
    digest = hashlib.sha256(f"{method}:{seed}:{task_id}".encode("utf-8")).hexdigest()
    return digest[:12]


def _compact_answer(answer: Any, max_chars: int = 6000) -> str:
    text = json.dumps(answer, ensure_ascii=False, sort_keys=True, indent=2)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated for annotation packet]..."


def _iter_artifacts(results: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for method_result in results.get("results", []):
        method = str(method_result.get("method", ""))
        if method not in {"single_fixed", "multi_fixed"}:
            continue
        for seed_result in method_result.get("seeds", []):
            seed = int(seed_result.get("seed", 0))
            for item in seed_result.get("tasks", []):
                task = item.get("task", {})
                task_id = str(task.get("task_id", ""))
                artifacts.append(
                    {
                        "artifact_id": _artifact_id(method, seed, task_id),
                        "method": method,
                        "seed": seed,
                        "task_id": task_id,
                        "domain": task.get("domain", ""),
                        "question": task.get("question", ""),
                        "related_work_trap": task.get("related_work_trap", ""),
                        "required_evidence": task.get("required_evidence", []),
                        "expected_artifacts": task.get("expected_artifacts", []),
                        "rubric_score": item.get("score", {}).get("score", 0),
                        "answer": _compact_answer(item.get("answer", {})),
                    }
                )
    return artifacts


def build_sample(artifacts: list[dict[str, Any]], *, seed: int, per_method: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    by_method: dict[str, list[dict[str, Any]]] = {"single_fixed": [], "multi_fixed": []}
    for artifact in artifacts:
        by_method[str(artifact["method"])].append(artifact)
    sample: list[dict[str, Any]] = []
    for method, rows in by_method.items():
        rows = list(rows)
        rng.shuffle(rows)
        sample.extend(rows[:per_method])
    rng.shuffle(sample)
    for idx, row in enumerate(sample, start=1):
        row["annotation_order"] = idx
    return sample


def write_protocol(output_dir: Path, *, sample_count: int) -> None:
    protocol = f"""# Human Evaluation Protocol

This packet supports a blinded human calibration study for the 20-task, three-seed AI-research workflow artifacts.

## Scope

- Sample size: {sample_count} artifacts.
- Methods: `single_fixed` and `multi_fixed`.
- Task source: `research_artifacts/ai_research_tasks_20.json`.
- The annotation packet hides method and seed in the CSV shown to annotators.
- The key file maps blinded artifact IDs back to method, seed, task, and structural-rubric score.

## Annotation Task

For each artifact, read the task prompt and generated answer. Score the answer on 1-5 scales:

- `overall_quality`: research usefulness of the artifact.
- `scientific_validity`: whether claims are appropriately cautious and evidence-grounded.
- `claim_grounding`: whether claims are tied to concrete evidence or planned checks.
- `reproducibility`: whether another researcher could execute the proposed check.
- `novelty_calibration`: whether novelty and related-work risks are handled honestly.
- `overclaim_risk`: 1 means low overclaim risk; 5 means high overclaim risk.

Use `notes` for one concise reason. Annotators should not infer method identity from length alone; judge whether the content would actually help a researcher.

## Suggested Analysis

After annotation, join the completed CSV with `human_eval_key.csv`, then compute:

- mean human quality by method,
- paired single-vs-multi deltas by task and seed where both methods are present,
- human/model-judge correlation using `quality_primary_analysis.json`,
- disagreement cases for qualitative failure analysis.

No human ratings are included in this packet yet; it is a ready-to-run calibration protocol.
"""
    (output_dir / "human_eval_protocol.md").write_text(protocol, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--per-method", type=int, default=20)
    args = parser.parse_args()

    results = json.loads(args.results.read_text(encoding="utf-8"))
    artifacts = _iter_artifacts(results)
    sample = build_sample(artifacts, seed=args.seed, per_method=args.per_method)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    packet_path = args.output_dir / "human_eval_blinded_packet.csv"
    key_path = args.output_dir / "human_eval_key.csv"
    jsonl_path = args.output_dir / "human_eval_blinded_packet.jsonl"

    packet_fields = [
        "annotation_order",
        "artifact_id",
        "domain",
        "task_id",
        "question",
        "related_work_trap",
        "required_evidence",
        "expected_artifacts",
        "answer",
        "overall_quality",
        "scientific_validity",
        "claim_grounding",
        "reproducibility",
        "novelty_calibration",
        "overclaim_risk",
        "notes",
    ]
    with packet_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=packet_fields)
        writer.writeheader()
        for row in sample:
            writer.writerow(
                {
                    **{field: row.get(field, "") for field in packet_fields},
                    "required_evidence": json.dumps(row.get("required_evidence", []), ensure_ascii=False),
                    "expected_artifacts": json.dumps(row.get("expected_artifacts", []), ensure_ascii=False),
                    "overall_quality": "",
                    "scientific_validity": "",
                    "claim_grounding": "",
                    "reproducibility": "",
                    "novelty_calibration": "",
                    "overclaim_risk": "",
                    "notes": "",
                }
            )
    with key_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["artifact_id", "method", "seed", "task_id", "rubric_score"])
        writer.writeheader()
        for row in sample:
            writer.writerow(
                {
                    "artifact_id": row["artifact_id"],
                    "method": row["method"],
                    "seed": row["seed"],
                    "task_id": row["task_id"],
                    "rubric_score": row["rubric_score"],
                }
            )
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in sample:
            public_row = {key: value for key, value in row.items() if key not in {"method", "seed", "rubric_score"}}
            handle.write(json.dumps(public_row, ensure_ascii=False) + "\n")
    write_protocol(args.output_dir, sample_count=len(sample))
    print(json.dumps({"output_dir": str(args.output_dir), "sample_count": len(sample)}, indent=2))


if __name__ == "__main__":
    main()
