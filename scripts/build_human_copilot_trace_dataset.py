#!/usr/bin/env python3
"""Build a derived human co-pilot trace dataset manifest.

The dataset intentionally uses derived metadata from the repository artifacts
rather than raw Codex chat logs. This keeps the evidence auditable while
reducing privacy and credential risk.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
OUT_JSON = DOC_DIR / "human_copilot_trace_dataset.json"
OUT_MD = DOC_DIR / "human_copilot_trace_dataset.md"


PUBLIC_DATASETS = [
    {
        "name": "CoAuthor",
        "url": "https://p-lambda.github.io/coauthor/",
        "fit": "human-AI collaborative writing interactions",
        "gap": "not scientific co-pilot research trajectories with benchmark execution",
    },
    {
        "name": "CUPID",
        "url": "https://cupid.kixlab.org/",
        "fit": "human-curated multi-turn preference interaction histories",
        "gap": "preference inference benchmark, not human scientific taste gates",
    },
    {
        "name": "neulab/agent-data-collection",
        "url": "https://huggingface.co/datasets/neulab/agent-data-collection",
        "fit": "agent trajectories across web, code, household, knowledge, and software tasks",
        "gap": "broad agent corpus, not AI Scientist-v2-style co-pilot research logs",
    },
    {
        "name": "WebChain",
        "url": "https://huggingface.co/datasets/webagentlab/WebChain",
        "fit": "human-annotated web interaction trajectories",
        "gap": "web/GUI task trajectories, not scientific hypothesis-experiment-paper loops",
    },
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _git_log() -> list[dict[str, str]]:
    proc = subprocess.run(
        ["git", "log", "--format=%H%x09%cs%x09%s", "--", "docs/co_pilot_ai_scientist_v3", "skills/co-pilot-ai-scientist-v3", "scripts"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    rows = []
    for line in proc.stdout.splitlines()[:80]:
        parts = line.split("\t", 2)
        if len(parts) == 3:
            rows.append({"commit": parts[0], "date": parts[1], "subject": parts[2]})
    return rows


def _gate_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    paths = sorted(DOC_DIR.glob("human_gate_logs/*.json"))
    paths.extend(sorted(DOC_DIR.glob("experiments/**/human_gate_logs/*.json")))
    for path in paths:
        try:
            data = _load_json(path)
        except json.JSONDecodeError:
            continue
        records.append(
            {
                "source": _rel(path),
                "gate_id": data.get("gate_id"),
                "gate_type": data.get("gate_type"),
                "research_task_id": data.get("research_task_id"),
                "option_count": len(data.get("options", [])) if isinstance(data.get("options"), list) else None,
                "has_attention_cost": isinstance(data.get("attention_cost"), dict),
                "has_taste_insight": isinstance(data.get("taste_insight"), dict),
                "human_decision": data.get("human_decision"),
            }
        )
    for path in sorted(DOC_DIR.glob("experiments/**/*trajectory.json")):
        try:
            data = _load_json(path)
        except json.JSONDecodeError:
            continue
        for index, gate in enumerate(data.get("gates", [])):
            if not isinstance(gate, dict):
                continue
            records.append(
                {
                    "source": f"{_rel(path)}#gates[{index}]",
                    "gate_id": gate.get("gate_id"),
                    "gate_type": gate.get("gate_type"),
                    "research_task_id": gate.get("research_task_id"),
                    "option_count": len(gate.get("options", [])) if isinstance(gate.get("options"), list) else None,
                    "has_attention_cost": isinstance(gate.get("attention_cost"), dict),
                    "has_taste_insight": isinstance(gate.get("taste_insight"), dict),
                    "human_decision": gate.get("human_decision"),
                }
            )
    seen = set()
    deduped = []
    for record in records:
        key = (record["source"], record.get("gate_id"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def _prospective_packages() -> list[dict[str, Any]]:
    packages = []
    for path in sorted(DOC_DIR.glob("experiments/prospective_matched_*/prospective_manifest.json")):
        manifest = _load_json(path)
        trajectory = _load_json(ROOT / manifest["co_pilot_trajectory"])
        baseline = _load_json(ROOT / manifest["autonomous_baseline"])
        packages.append(
            {
                "package_id": manifest.get("package_id"),
                "manifest": _rel(path),
                "status": manifest.get("status"),
                "co_pilot_metric": trajectory.get("co_pilot_test_metric")
                or trajectory.get("metrics", {}).get("co_pilot_variant", {}).get("mean_normalized_score"),
                "autonomous_metric": trajectory.get("autonomous_test_metric")
                or trajectory.get("metrics", {}).get("autonomous_baseline", {}).get("mean_normalized_score"),
                "benchmark": baseline.get("benchmark")
                if isinstance(baseline, dict)
                else trajectory.get("metrics", {}).get("task"),
                "human_gate_count": len(manifest.get("human_gate_logs", []))
                if isinstance(manifest.get("human_gate_logs"), list)
                else 0,
            }
        )
    return packages


def _markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Human Co-Pilot Trace Dataset Protocol",
        "",
        "This artifact answers whether the paper needs human co-pilot usage data.",
        "Yes: the central claim concerns human scientific taste and insight at",
        "creative or high-leverage decision nodes, so the paper needs trace data",
        "showing where human decisions entered the research loop and what happened",
        "afterward.",
        "",
        "## Public Dataset Survey",
        "",
        "| Dataset | Useful signal | Why it is insufficient for this paper |",
        "| --- | --- | --- |",
    ]
    for item in data["public_dataset_survey"]:
        lines.append(f"| [{item['name']}]({item['url']}) | {item['fit']} | {item['gap']} |")
    lines.extend(
        [
            "",
            "No surveyed public dataset directly provides human scientist co-pilot",
            "interventions inside an AI Scientist-v2-style loop with linked hypotheses,",
            "benchmark runs, code artifacts, claim audits, and manuscripts. Public",
            "datasets should therefore be used as related work or auxiliary design",
            "evidence, not as the primary empirical support for IGRE.",
            "",
            "## Proposed Primary Dataset",
            "",
            "Use the author's Codex research sessions as an author-in-the-loop trace",
            "corpus, but only after deriving a privacy-preserving metadata layer. Raw",
            "chat logs are not required for the public release. The released dataset",
            "should include gate records, artifact paths, commit IDs, benchmark metrics,",
            "manuscript revisions, and claim-audit outcomes.",
            "",
            "## Current Derived Dataset Snapshot",
            "",
            f"- Gate records indexed: {data['current_snapshot']['gate_record_count']}",
            f"- Records with attention cost: {data['current_snapshot']['attention_cost_records']}",
            f"- Records with taste/insight: {data['current_snapshot']['taste_insight_records']}",
            f"- Prospective matched packages: {data['current_snapshot']['prospective_package_count']}",
            f"- Git commits indexed for this package: {data['current_snapshot']['commit_count']}",
            "",
            "## What This Dataset Can Support",
            "",
            "- Ecological validity: a real researcher used the co-pilot workflow while building the paper.",
            "- Process claims: human gates can be inserted, logged, audited, and linked to artifacts.",
            "- Case-study claims: human taste/insight can be represented as a high-variance search prior.",
            "- Negative findings: some human-gated choices lose to autonomous baselines on short-budget metrics.",
            "",
            "## What It Cannot Support Alone",
            "",
            "- Population-level claims about all scientists.",
            "- Average performance superiority over autonomous AI Scientist-v2.",
            "- Top-conference empirical sufficiency without multi-task/multi-seed matched evaluation.",
            "- Human attention efficiency unless timing is prospectively recorded.",
            "",
            "## Release Rules",
            "",
            "1. Remove credentials, private URLs, and personally identifying content.",
            "2. Release derived event records before raw transcripts.",
            "3. Preserve enough artifact links for reproducibility.",
            "4. Mark operator-recorded timing separately from independent human-subject timing.",
            "5. Treat the first release as a single-author longitudinal case study.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    gates = _gate_records()
    packages = _prospective_packages()
    commits = _git_log()
    data: dict[str, Any] = {
        "status": "derived_metadata_protocol",
        "public_dataset_survey": PUBLIC_DATASETS,
        "primary_dataset_positioning": "single_author_longitudinal_codex_copilot_trace_corpus",
        "current_snapshot": {
            "gate_record_count": len(gates),
            "attention_cost_records": sum(1 for item in gates if item["has_attention_cost"]),
            "taste_insight_records": sum(1 for item in gates if item["has_taste_insight"]),
            "prospective_package_count": len(packages),
            "commit_count": len(commits),
        },
        "gate_records": gates,
        "prospective_packages": packages,
        "commit_index": commits,
        "claim_scope": {
            "supports": [
                "single-author ecological case study",
                "gate-level process audit",
                "artifact-linked human intervention analysis",
                "negative-result reporting for human gates",
            ],
            "does_not_support_alone": [
                "population-level human benefit",
                "average benchmark superiority",
                "top-conference empirical sufficiency",
                "human attention efficiency without prospective timing",
            ],
        },
    }
    OUT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(data), encoding="utf-8")
    print(json.dumps({"json": _rel(OUT_JSON), "markdown": _rel(OUT_MD)}, indent=2))


if __name__ == "__main__":
    main()
