from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class ResearchTask:
    task_id: str
    question: str
    related_work_trap: str
    required_evidence: list[str]
    toy_experiment: str
    source: str = "micro"
    domain: str = "ai_research"
    expected_artifacts: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_TASKS = [
    ResearchTask(
        task_id="novelty_guard",
        question="Design a novelty guard for AI-generated ML research ideas.",
        related_work_trap="Do not claim novelty for generic literature retrieval or ordinary reviewer prompts.",
        required_evidence=["duplicate-risk analysis", "retrieval ablation", "false positive/negative discussion"],
        toy_experiment="Evaluate on 20 generated ideas with 5 known duplicates.",
        expected_artifacts=["novelty rubric", "ablation table", "failure analysis"],
    ),
    ResearchTask(
        task_id="multi_agent_topology",
        question="Test whether multi-agent topology affects automated research quality.",
        related_work_trap="Control for total token budget; otherwise more agents may only mean more compute.",
        required_evidence=["single-agent baseline", "same-budget comparison", "topology ablation"],
        toy_experiment="Compare single, chain, tree, and graph teams on five compact research tasks.",
        expected_artifacts=["topology configs", "same-budget table", "milestone analysis"],
    ),
    ResearchTask(
        task_id="artifact_evolution",
        question="Measure whether self-evolving research policies improve across tasks.",
        related_work_trap="Prompt-only memory is not enough; preserve executable artifacts and logs.",
        required_evidence=["policy update log", "before/after comparison", "policy drift check"],
        toy_experiment="Run shuffled tasks twice and compare second-pass reproducibility failures.",
        expected_artifacts=["strategy_policy.md", "policy diff", "drift audit"],
    ),
    ResearchTask(
        task_id="figure_vlm_critic",
        question="Decide when a VLM figure critic helps automated paper writing.",
        related_work_trap="Figure critique must be grounded in generated plots, not generic style advice.",
        required_evidence=["with/without VLM ablation", "figure defect taxonomy", "cost accounting"],
        toy_experiment="Score generated plots for readability, label correctness, and paper impact.",
        expected_artifacts=["figure critique", "defect taxonomy", "cost table"],
    ),
    ResearchTask(
        task_id="paper_claim_grounding",
        question="Write a short paper section that separates proven results from hypotheses.",
        related_work_trap="Do not report pilot or simulated outcomes as completed empirical results.",
        required_evidence=["claim-evidence table", "limitations section", "reproducibility checklist"],
        toy_experiment="Audit generated paper sections for unsupported claims and missing commands.",
        expected_artifacts=["claim-evidence table", "limitations", "reproducibility checklist"],
    ),
]


def _coerce_task(raw: dict[str, Any], *, index: int, source_name: str) -> ResearchTask:
    task_id = str(raw.get("task_id") or raw.get("id") or f"{source_name}_{index:03d}")
    question = str(raw.get("question") or raw.get("prompt") or raw.get("goal") or "")
    if not question:
        raise ValueError(f"Task {task_id} is missing question/prompt/goal.")
    required_evidence = raw.get("required_evidence") or raw.get("evidence") or raw.get("metrics") or []
    if isinstance(required_evidence, str):
        required_evidence = [required_evidence]
    expected_artifacts = raw.get("expected_artifacts") or raw.get("artifacts") or []
    if isinstance(expected_artifacts, str):
        expected_artifacts = [expected_artifacts]
    return ResearchTask(
        task_id=task_id,
        question=question,
        related_work_trap=str(raw.get("related_work_trap") or raw.get("trap") or "Avoid unsupported novelty or performance claims."),
        required_evidence=[str(item) for item in required_evidence],
        toy_experiment=str(raw.get("toy_experiment") or raw.get("experiment") or raw.get("evaluation") or "Define and execute a compact reproducible evaluation."),
        source=str(raw.get("source") or source_name),
        domain=str(raw.get("domain") or "ai_research"),
        expected_artifacts=[str(item) for item in expected_artifacts] or None,
    )


def load_tasks(path: Path | None = None) -> list[ResearchTask]:
    if path is None:
        return list(DEFAULT_TASKS)
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Task file is empty: {path}")
    if path.suffix == ".jsonl":
        raw_items = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        raw = json.loads(text)
        raw_items = raw["tasks"] if isinstance(raw, dict) and "tasks" in raw else raw
    if not isinstance(raw_items, list):
        raise ValueError("Task file must contain a JSON array, JSONL rows, or an object with `tasks`.")
    return [_coerce_task(item, index=idx, source_name=path.stem) for idx, item in enumerate(raw_items, start=1)]


def save_task_template(path: Path) -> None:
    template = {
        "tasks": [
            {
                "task_id": "external_example_001",
                "source": "airs_bench_or_researchgym_subset",
                "domain": "language_modeling",
                "question": "State the research objective the agent must solve.",
                "related_work_trap": "Describe a common false novelty or leakage trap.",
                "required_evidence": ["baseline comparison", "ablation", "reproducibility commands"],
                "toy_experiment": "Describe the smallest executable evaluation for this task.",
                "expected_artifacts": ["experiment script", "metrics.json", "paper section"],
            }
        ]
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(template, indent=2), encoding="utf-8")

