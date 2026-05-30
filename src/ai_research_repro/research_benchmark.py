from __future__ import annotations

import json
import random
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .benchmark_tasks import ResearchTask, load_tasks
from .llm import chat_json_result
from .manifest import write_repro_manifest


@dataclass
class MethodSpec:
    name: str
    roles: list[str]
    self_evolve: bool = False
    reflection: bool = False
    ensemble_attempts: int = 0
    structured_memory: bool = False


METHODS = {
    "author_curated_reference": MethodSpec(name="author_curated_reference", roles=[]),
    "fixed_template": MethodSpec(name="fixed_template", roles=[]),
    "single_fixed": MethodSpec(name="single_fixed", roles=["researcher"]),
    "single_reflection": MethodSpec(name="single_reflection", roles=["researcher"], reflection=True),
    "single_self_consistency": MethodSpec(
        name="single_self_consistency",
        roles=["researcher"],
        reflection=True,
        ensemble_attempts=6,
    ),
    "multi_fixed": MethodSpec(
        name="multi_fixed",
        roles=["ideator", "literature_critic", "experiment_manager", "coder", "reviewer", "writer"],
    ),
    "multi_no_literature": MethodSpec(
        name="multi_no_literature",
        roles=["ideator", "experiment_manager", "coder", "reviewer", "writer"],
    ),
    "multi_no_coder": MethodSpec(
        name="multi_no_coder",
        roles=["ideator", "literature_critic", "experiment_manager", "reviewer", "writer"],
    ),
    "multi_no_reviewer": MethodSpec(
        name="multi_no_reviewer",
        roles=["ideator", "literature_critic", "experiment_manager", "coder", "writer"],
    ),
    "multi_artifact_evolution": MethodSpec(
        name="multi_artifact_evolution",
        roles=["ideator", "literature_critic", "experiment_manager", "coder", "reviewer", "writer"],
        self_evolve=True,
        reflection=True,
    ),
    "multi_structured_evolution": MethodSpec(
        name="multi_structured_evolution",
        roles=["ideator", "literature_critic", "experiment_manager", "coder", "reviewer", "writer"],
        self_evolve=True,
        reflection=True,
        structured_memory=True,
    ),
}


SYSTEM_PROMPT = """You are running a compact AI Scientist-v2 style research benchmark.
Return JSON only. Be conservative: do not invent citations, benchmark numbers, or completed experiments."""


ROLE_PROMPTS = {
    "ideator": "Propose a focused, testable research hypothesis and identify the smallest useful experiment.",
    "literature_critic": "Identify novelty risks, related-work traps, and evidence needed to avoid overclaiming.",
    "experiment_manager": "Turn the idea into a reproducible experiment plan with baselines, ablations, and commands.",
    "coder": "Specify executable artifacts, file outputs, and failure checks without inventing completed results.",
    "reviewer": "Critique claim grounding, reproducibility, and missing evidence.",
    "writer": "Synthesize a conservative paper-ready artifact grounded only in the trace.",
    "researcher": "Produce the full compact research artifact directly.",
}


def _fallback_answer(task: ResearchTask, method: MethodSpec, policy: str) -> dict[str, Any]:
    missing = [item for item in task.required_evidence if item.lower() not in policy.lower()]
    return {
        "hypothesis": f"{method.name} can address {task.question}",
        "novelty_check": task.related_work_trap,
        "experiment_plan": task.toy_experiment,
        "required_evidence_addressed": [item for item in task.required_evidence if item not in missing],
        "limitations": ["Pilot benchmark only", "Needs LLM or human judging for final paper claims"],
        "claim_evidence_table": [
            {"claim": "The plan is executable", "evidence": task.toy_experiment, "status": "planned"}
        ],
        "reproducibility_commands": [
            "PYTHONPATH=src python3 -m ai_research_repro.cli research-benchmark --workspace runs/research_pilot"
        ],
        "policy_update": "Keep explicit evidence checklists and same-budget comparisons." if method.self_evolve else "",
    }


def _fallback_role(role: str, task: ResearchTask, method: MethodSpec) -> dict[str, Any]:
    return {
        "role": role,
        "contribution": ROLE_PROMPTS.get(role, "Contribute to the research artifact."),
        "evidence_updates": list(task.required_evidence),
        "concerns": [task.related_work_trap, "Fallback trace only; requires API-backed validation."],
        "next_instruction": f"Keep {method.name} grounded in explicit evidence and reproducible commands.",
    }


def _fixed_template_answer(task: ResearchTask) -> dict[str, Any]:
    return {
        "hypothesis": "A research workflow should be evaluated with explicit evidence before any claim is reported.",
        "novelty_check": "No novelty is claimed by this fixed template baseline.",
        "experiment_plan": "Run the benchmark command and compare this fixed template against API-backed agent workflows.",
        "required_evidence_addressed": [],
        "limitations": [
            "This is a non-adaptive fixed template.",
            "It does not inspect the task-specific evidence requirements.",
            "It is included only to calibrate the rubric dynamic range.",
        ],
        "claim_evidence_table": [
            {
                "claim": "This baseline is reproducible.",
                "evidence": "It is generated deterministically without an LLM call.",
                "status": "verified",
            }
        ],
        "reproducibility_commands": [
            "PYTHONPATH=src python3 -m ai_research_repro.cli research-benchmark --methods fixed_template"
        ],
        "policy_update": "",
    }


def _author_curated_reference_answer(task: ResearchTask) -> dict[str, Any]:
    expected_artifacts = task.expected_artifacts or []
    evidence_rows = [
        {
            "claim": f"The artifact explicitly covers required evidence: {item}.",
            "evidence": f"`{item}` is named in the evidence checklist and mapped to a concrete experiment component.",
            "status": "verified",
        }
        for item in task.required_evidence
    ]
    artifact_rows = [
        {
            "claim": f"The plan names expected artifact: {item}.",
            "evidence": f"`{item}` is included in the deliverable checklist for this task.",
            "status": "verified",
        }
        for item in expected_artifacts
    ]
    all_evidence = ", ".join(task.required_evidence) or "the task-specific required evidence"
    all_artifacts = ", ".join(expected_artifacts) or "the task-specific expected artifacts"
    return {
        "hypothesis": (
            f"For `{task.task_id}`, a conservative AI-research workflow is credible only if it ties "
            f"the question `{task.question}` to explicit evidence, executable checks, and scoped claims."
        ),
        "novelty_check": (
            f"Novelty is not assumed. The main related-work trap is: {task.related_work_trap} "
            "The reference answer treats this as a risk to audit rather than a contribution."
        ),
        "experiment_plan": (
            f"Run the task's minimal experiment: {task.toy_experiment} Compare a simple single-agent "
            "baseline, a budget-matched self-consistency baseline, fixed multi-agent orchestration, "
            "and artifact-evolution variants. Report both raw artifact-completeness and independent "
            f"quality review. Required evidence checklist: {all_evidence}. Expected artifact checklist: {all_artifacts}."
        ),
        "required_evidence_addressed": list(task.required_evidence),
        "claim_evidence_table": evidence_rows
        + artifact_rows
        + [
            {
                "claim": "This reference artifact is a calibration target, not a human evaluation result.",
                "evidence": "It is generated deterministically from the task schema and does not use hidden empirical outcomes.",
                "status": "verified",
            },
            {
                "claim": "The related-work trap is explicitly represented in the plan.",
                "evidence": task.related_work_trap,
                "status": "verified",
            },
        ],
        "limitations": [
            "This is an author-curated deterministic reference, not an independent human baseline.",
            "It can calibrate the upper end of the structural rubric but cannot establish scientific truth.",
            "It uses task metadata directly, so it should not be compared as a deployable autonomous agent.",
        ],
        "reproducibility_commands": [
            "PYTHONPATH=src python3 -m ai_research_repro.cli research-benchmark --methods author_curated_reference --role-mode orchestrated",
            "PYTHONPATH=src python3 -m ai_research_repro.cli analyze-results --results runs/research_pilot_deepseek_v3/research_benchmark_results.json",
        ],
        "policy_update": "",
    }


def _score_answer(task: ResearchTask, answer: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(answer, ensure_ascii=False).lower()
    evidence_hits = sum(1 for item in task.required_evidence if item.lower() in text)
    expected_artifacts = task.expected_artifacts or []
    artifact_hits = sum(1 for item in expected_artifacts if item.lower() in text)
    has_plan = bool(answer.get("experiment_plan"))
    limitations = answer.get("limitations", [])
    commands = answer.get("reproducibility_commands", [])
    claim_table = answer.get("claim_evidence_table", [])
    has_limits = bool(limitations)
    has_commands = bool(commands)
    has_claim_table = bool(claim_table)
    mentions_trap = any(token in text for token in task.related_work_trap.lower().split(";")[0].split()[:4])
    actionable_command_terms = ("python", "python3", "bash", "pytest", "make", "uv ", "pip ", "rscript")
    command_text = "\n".join(str(item).lower() for item in commands if isinstance(commands, list))
    has_actionable_command = any(term in command_text for term in actionable_command_terms)
    limitation_count = len(limitations) if isinstance(limitations, list) else int(has_limits)
    claim_rows = claim_table if isinstance(claim_table, list) else []
    final_statuses = {"observed", "measured", "verified", "completed"}
    nonfinal_claim_rows = 0
    final_claim_rows = 0
    for row in claim_rows:
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", "")).lower()
        if status in final_statuses:
            final_claim_rows += 1
        elif status:
            nonfinal_claim_rows += 1
    risk_mentions = sum(1 for term in ("fallback", "simulated", "placeholder") if term in text)
    score = (
        evidence_hits * 3
        + artifact_hits * 2
        + int(has_plan) * 2
        + min(limitation_count, 3)
        + int(has_commands)
        + int(has_actionable_command)
        + int(has_claim_table)
        + min(final_claim_rows, 3)
        + int(mentions_trap)
        - min(nonfinal_claim_rows, 3)
        - risk_mentions
    )
    score = max(score, 0)
    return {
        "score": score,
        "evidence_hits": evidence_hits,
        "max_evidence_hits": len(task.required_evidence),
        "artifact_hits": artifact_hits,
        "max_artifact_hits": len(expected_artifacts),
        "has_experiment_plan": has_plan,
        "has_limitations": has_limits,
        "has_reproducibility_commands": has_commands,
        "has_actionable_reproducibility_command": has_actionable_command,
        "has_claim_evidence_table": has_claim_table,
        "final_claim_rows": final_claim_rows,
        "nonfinal_claim_rows": nonfinal_claim_rows,
        "risk_mentions": risk_mentions,
        "mentions_related_work_trap": mentions_trap,
    }


def _usage_total(call_meta: list[dict[str, Any]]) -> dict[str, int]:
    totals = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    for meta in call_meta:
        usage = meta.get("usage", {}) if isinstance(meta, dict) else {}
        for key in totals:
            totals[key] += int(usage.get(key, 0) or 0)
    return totals


def _token_set(text: str) -> set[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    return {token for token in cleaned.split() if len(token) > 2}


def _build_failure_memory(task: ResearchTask, result: dict[str, Any]) -> dict[str, Any]:
    score = result.get("score", {})
    answer = result.get("answer", {})
    text = json.dumps(answer, ensure_ascii=False).lower()
    missing_evidence = [
        item for item in task.required_evidence if item.lower() not in text
    ]
    expected_artifacts = task.expected_artifacts or []
    missing_artifacts = [
        item for item in expected_artifacts if item.lower() not in text
    ]
    failure_tags = []
    if missing_evidence:
        failure_tags.append("missing_required_evidence")
    if missing_artifacts:
        failure_tags.append("missing_expected_artifact")
    if not score.get("has_claim_evidence_table"):
        failure_tags.append("missing_claim_evidence_table")
    if not score.get("has_reproducibility_commands"):
        failure_tags.append("missing_reproducibility_commands")
    if not score.get("has_actionable_reproducibility_command"):
        failure_tags.append("non_actionable_command")
    if score.get("nonfinal_claim_rows", 0):
        failure_tags.append("nonfinal_claim_status")
    if score.get("risk_mentions", 0):
        failure_tags.append("risk_language")
    if not score.get("mentions_related_work_trap"):
        failure_tags.append("missed_related_work_trap")
    if not failure_tags:
        failure_tags.append("preserve_success_pattern")

    prevention_rules = []
    if missing_evidence:
        prevention_rules.append("Echo every required_evidence item verbatim in the artifact and map each item to an evidence row.")
    if missing_artifacts:
        prevention_rules.append("Name every expected_artifact item verbatim in the experiment plan or deliverable checklist.")
    if "missing_claim_evidence_table" in failure_tags:
        prevention_rules.append("Always return a non-empty claim_evidence_table; use conservative planned/to_be_tested statuses if needed.")
    if "non_actionable_command" in failure_tags:
        prevention_rules.append("Use executable commands containing python3, bash, pytest, make, uv, pip, or Rscript.")
    if "nonfinal_claim_status" in failure_tags:
        prevention_rules.append("Separate completed/verified claims from hypotheses; avoid presenting planned work as measured.")
    if "risk_language" in failure_tags:
        prevention_rules.append("Avoid fallback, simulated, and placeholder wording unless explicitly framed as a limitation.")
    if "missed_related_work_trap" in failure_tags:
        prevention_rules.append("Mention the related_work_trap explicitly and treat it as a novelty risk.")
    if not prevention_rules:
        prevention_rules.append("Keep the same evidence-table, command, limitation, and trap-grounding discipline on later tasks.")

    keywords = _token_set(
        " ".join(
            [
                task.task_id,
                task.question,
                task.related_work_trap,
                " ".join(task.required_evidence),
                " ".join(expected_artifacts),
                " ".join(failure_tags),
            ]
        )
    )
    return {
        "source_task_id": task.task_id,
        "source_score": score.get("score", 0),
        "failure_tags": failure_tags,
        "missing_evidence": missing_evidence,
        "missing_artifacts": missing_artifacts,
        "prevention_rules": prevention_rules[:5],
        "keywords": sorted(keywords)[:80],
    }


def _memory_relevance(task: ResearchTask, memory: dict[str, Any]) -> float:
    task_terms = _token_set(
        " ".join(
            [
                task.task_id,
                task.question,
                task.related_work_trap,
                " ".join(task.required_evidence),
                " ".join(task.expected_artifacts or []),
            ]
        )
    )
    memory_terms = set(memory.get("keywords", []))
    if not task_terms or not memory_terms:
        return 0.0
    return len(task_terms & memory_terms) / len(task_terms | memory_terms)


def _format_structured_memory_policy(base_policy: str, task: ResearchTask, memory: list[dict[str, Any]]) -> str:
    if not memory:
        return (
            f"{base_policy}\n"
            "Structured failure memory: no prior task records yet. Create explicit evidence rows, limitations, "
            "and executable commands so later tasks can retrieve concrete failures."
        )
    ranked = sorted(memory, key=lambda item: _memory_relevance(task, item), reverse=True)[:3]
    lines = [
        base_policy,
        "Structured failure memory retrieved for this task:",
    ]
    for idx, item in enumerate(ranked, start=1):
        lines.append(
            f"{idx}. source_task={item.get('source_task_id')} score={item.get('source_score')} "
            f"tags={', '.join(item.get('failure_tags', []))}"
        )
        if item.get("missing_evidence"):
            lines.append(f"   missing_evidence={', '.join(item['missing_evidence'])}")
        if item.get("missing_artifacts"):
            lines.append(f"   missing_artifacts={', '.join(item['missing_artifacts'])}")
        for rule in item.get("prevention_rules", [])[:3]:
            lines.append(f"   prevention_rule={rule}")
    lines.append(
        "Use the retrieved memory as a checklist. Do not claim completed empirical results unless measured evidence is present."
    )
    return "\n".join(lines)


def _direct_answer(task: ResearchTask, method: MethodSpec, model: str, policy: str, seed: int) -> tuple[dict[str, Any], list[dict[str, Any]], int, int, list[dict[str, Any]]]:
    task_payload = asdict(task)
    method_payload = asdict(method)
    prompt_chars = len(json.dumps(task_payload)) + len(json.dumps(method_payload)) + len(policy)
    started = time.perf_counter()
    user = f"""Task:
{json.dumps(task_payload, indent=2)}

Method:
{json.dumps(method_payload, indent=2)}

Seed:
{seed}

Current strategy policy:
{policy}

Produce a compact research artifact with these fields:
hypothesis, novelty_check, experiment_plan, required_evidence_addressed,
claim_evidence_table, limitations, reproducibility_commands, policy_update.
"""
    llm_result = chat_json_result(
        system=SYSTEM_PROMPT,
        user=user,
        model=model,
        fallback=lambda: _fallback_answer(task, method, policy),
    )
    answer = llm_result.parsed
    if not isinstance(answer, dict):
        answer = _fallback_answer(task, method, policy)
    answer["_runtime_seconds_inner"] = round(time.perf_counter() - started, 4)
    return answer, [], 1, prompt_chars, [llm_result.meta or {}]


def _role_step(
    *,
    role: str,
    task: ResearchTask,
    method: MethodSpec,
    model: str,
    policy: str,
    seed: int,
    trace: list[dict[str, Any]],
) -> tuple[dict[str, Any], int, dict[str, Any]]:
    trace_context = json.dumps(trace[-3:], indent=2, ensure_ascii=False)
    user = f"""Role:
{role}

Role objective:
{ROLE_PROMPTS.get(role, "Contribute to the research artifact.")}

Task:
{json.dumps(asdict(task), indent=2)}

Method:
{json.dumps(asdict(method), indent=2)}

Seed:
{seed}

Current strategy policy:
{policy}

Recent role trace:
{trace_context}

Return JSON with fields:
role, contribution, evidence_updates, concerns, next_instruction.
"""
    prompt_chars = len(user)
    llm_result = chat_json_result(
        system=SYSTEM_PROMPT,
        user=user,
        model=model,
        fallback=lambda: _fallback_role(role, task, method),
    )
    result = llm_result.parsed
    if not isinstance(result, dict):
        result = _fallback_role(role, task, method)
    result["role"] = role
    return result, prompt_chars, llm_result.meta or {}


def _orchestrated_answer(task: ResearchTask, method: MethodSpec, model: str, policy: str, seed: int) -> tuple[dict[str, Any], list[dict[str, Any]], int, int, list[dict[str, Any]]]:
    trace: list[dict[str, Any]] = []
    call_meta: list[dict[str, Any]] = []
    prompt_chars = 0
    call_count = 0
    for role in method.roles:
        step, chars, meta = _role_step(
            role=role,
            task=task,
            method=method,
            model=model,
            policy=policy,
            seed=seed,
            trace=trace,
        )
        trace.append(step)
        call_meta.append(meta)
        prompt_chars += chars
        call_count += 1

    synth_prompt = f"""Synthesize the role trace into one compact research artifact.

Task:
{json.dumps(asdict(task), indent=2)}

Method:
{json.dumps(asdict(method), indent=2)}

Current strategy policy:
{policy}

Role trace:
{json.dumps(trace, indent=2, ensure_ascii=False)}

Return JSON with fields:
hypothesis, novelty_check, experiment_plan, required_evidence_addressed,
claim_evidence_table, limitations, reproducibility_commands, policy_update.
Do not claim completed empirical results unless the trace contains measured evidence.
"""
    prompt_chars += len(synth_prompt)
    call_count += 1
    llm_result = chat_json_result(
        system=SYSTEM_PROMPT,
        user=synth_prompt,
        model=model,
        fallback=lambda: _fallback_answer(task, method, policy),
    )
    answer = llm_result.parsed
    call_meta.append(llm_result.meta or {})
    if not isinstance(answer, dict):
        answer = _fallback_answer(task, method, policy)
    answer["role_trace_summary"] = [
        {
            "role": item.get("role", ""),
            "contribution": item.get("contribution", ""),
            "concerns": item.get("concerns", []),
        }
        for item in trace
    ]
    return answer, trace, call_count, prompt_chars, call_meta


def _self_consistency_answer(task: ResearchTask, method: MethodSpec, model: str, policy: str, seed: int) -> tuple[dict[str, Any], list[dict[str, Any]], int, int, list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    trace: list[dict[str, Any]] = []
    call_meta: list[dict[str, Any]] = []
    prompt_chars = 0
    attempts = max(method.ensemble_attempts, 2)

    for attempt in range(attempts):
        task_payload = asdict(task)
        method_payload = asdict(method)
        user = f"""Task:
{json.dumps(task_payload, indent=2)}

Method:
{json.dumps(method_payload, indent=2)}

Seed:
{seed}

Self-consistency attempt:
{attempt}

Current strategy policy:
{policy}

Produce one independent compact research artifact with these fields:
hypothesis, novelty_check, experiment_plan, required_evidence_addressed,
claim_evidence_table, limitations, reproducibility_commands, policy_update.
Return JSON only. Prefer concrete evidence artifacts and executable commands over broad prose.
"""
        prompt_chars += len(user)
        llm_result = chat_json_result(
            system=SYSTEM_PROMPT,
            user=user,
            model=model,
            fallback=lambda: _fallback_answer(task, method, policy),
        )
        candidate = llm_result.parsed if isinstance(llm_result.parsed, dict) else _fallback_answer(task, method, policy)
        candidates.append(candidate)
        call_meta.append(llm_result.meta or {})
        trace.append(
            {
                "role": f"researcher_attempt_{attempt}",
                "contribution": candidate.get("hypothesis", ""),
                "evidence_updates": candidate.get("required_evidence_addressed", []),
                "concerns": candidate.get("limitations", []),
                "next_instruction": "Synthesize the strongest conservative elements across independent attempts.",
            }
        )

    synth_prompt = f"""Synthesize independent single-agent attempts into one compact research artifact.

Task:
{json.dumps(asdict(task), indent=2)}

Method:
{json.dumps(asdict(method), indent=2)}

Current strategy policy:
{policy}

Independent attempts:
{json.dumps(candidates, indent=2, ensure_ascii=False)}

Return JSON with fields:
hypothesis, novelty_check, experiment_plan, required_evidence_addressed,
claim_evidence_table, limitations, reproducibility_commands, policy_update.
Use only claims supported by the attempts or task metadata. Keep unsupported claims as limitations.
"""
    prompt_chars += len(synth_prompt)
    llm_result = chat_json_result(
        system=SYSTEM_PROMPT,
        user=synth_prompt,
        model=model,
        fallback=lambda: _fallback_answer(task, method, policy),
    )
    answer = llm_result.parsed if isinstance(llm_result.parsed, dict) else _fallback_answer(task, method, policy)
    call_meta.append(llm_result.meta or {})
    answer["self_consistency_summary"] = [
        {
            "attempt": idx,
            "hypothesis": candidate.get("hypothesis", ""),
            "limitations": candidate.get("limitations", []),
        }
        for idx, candidate in enumerate(candidates)
    ]
    return answer, trace, attempts + 1, prompt_chars, call_meta


def _run_one(
    task: ResearchTask,
    method: MethodSpec,
    model: str,
    policy: str,
    seed: int,
    role_mode: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    if method.name == "author_curated_reference":
        answer = _author_curated_reference_answer(task)
        role_trace = []
        call_count = 0
        prompt_chars = 0
        call_meta = [{"provider": "deterministic", "model": "author_curated_reference", "fallback": False, "usage": {}}]
    elif method.name == "fixed_template":
        answer = _fixed_template_answer(task)
        role_trace = []
        call_count = 0
        prompt_chars = 0
        call_meta = [{"provider": "deterministic", "model": "fixed_template", "fallback": False, "usage": {}}]
    elif role_mode == "orchestrated" and method.ensemble_attempts:
        answer, role_trace, call_count, prompt_chars, call_meta = _self_consistency_answer(task, method, model, policy, seed)
    elif role_mode == "orchestrated" and len(method.roles) > 1:
        answer, role_trace, call_count, prompt_chars, call_meta = _orchestrated_answer(task, method, model, policy, seed)
    else:
        answer, role_trace, call_count, prompt_chars, call_meta = _direct_answer(task, method, model, policy, seed)
    answer.pop("_runtime_seconds_inner", None)
    token_usage = _usage_total(call_meta)
    return {
        "task": asdict(task),
        "method": asdict(method),
        "seed": seed,
        "role_mode": role_mode,
        "answer": answer,
        "role_trace": role_trace,
        "score": _score_answer(task, answer),
        "runtime_seconds": round(time.perf_counter() - started, 4),
        "estimated_output_chars": len(json.dumps(answer, ensure_ascii=False)),
        "estimated_prompt_chars": prompt_chars,
        "llm_call_count": call_count,
        "llm_call_meta": call_meta,
        "token_usage": token_usage,
    }


def _write_tables(workspace: Path, summary: dict[str, Any]) -> None:
    rows = []
    for method_result in summary["results"]:
        for seed_result in method_result["seeds"]:
            rows.append(
                {
                    "method": method_result["method"],
                    "seed": seed_result["seed"],
                    "total_score": seed_result["total_score"],
                    "mean_task_score": seed_result["mean_task_score"],
                    "runtime_seconds": seed_result["runtime_seconds"],
                    "estimated_output_chars": seed_result["estimated_output_chars"],
                    "estimated_prompt_chars": seed_result["estimated_prompt_chars"],
                    "llm_call_count": seed_result["llm_call_count"],
                    "prompt_tokens": seed_result["token_usage"]["prompt_tokens"],
                    "completion_tokens": seed_result["token_usage"]["completion_tokens"],
                    "total_tokens": seed_result["token_usage"]["total_tokens"],
                }
            )
    csv_path = workspace / "research_benchmark_summary.csv"
    header = [
        "method",
        "seed",
        "total_score",
        "mean_task_score",
        "runtime_seconds",
        "estimated_output_chars",
        "estimated_prompt_chars",
        "llm_call_count",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
    ]
    csv_path.write_text(
        "\n".join([",".join(header)] + [",".join(str(row[col]) for col in header) for row in rows]) + "\n",
        encoding="utf-8",
    )

    md = [
        "# Research Benchmark Summary",
        "",
        f"- Model: `{summary['model']}`",
        f"- Role mode: `{summary['role_mode']}`",
        f"- Task count: {summary['task_count']}",
        f"- Seeds: {', '.join(str(seed) for seed in summary['seeds'])}",
        "",
        "| Method | Mean Total Score | Std | Mean Runtime (s) |",
        "| --- | ---: | ---: | ---: |",
    ]
    for method_result in summary["results"]:
        totals = [seed_result["total_score"] for seed_result in method_result["seeds"]]
        runtimes = [seed_result["runtime_seconds"] for seed_result in method_result["seeds"]]
        std = statistics.pstdev(totals) if len(totals) > 1 else 0.0
        md.append(
            f"| `{method_result['method']}` | {statistics.mean(totals):.2f} | {std:.2f} | {statistics.mean(runtimes):.2f} |"
        )
    md.extend(
        [
            "",
            "These are benchmark-instrumentation scores, not final scientific findings. Real paper claims require API-backed runs and human or independent model review.",
            "",
        ]
    )
    (workspace / "research_benchmark_summary.md").write_text("\n".join(md), encoding="utf-8")


def _write_role_traces(workspace: Path, summary: dict[str, Any]) -> None:
    trace_dir = workspace / "role_traces"
    trace_dir.mkdir(parents=True, exist_ok=True)
    index_lines = ["# Role Trace Index", ""]
    for method_result in summary["results"]:
        method = method_result["method"]
        for seed_result in method_result["seeds"]:
            seed = seed_result["seed"]
            for task_result in seed_result["tasks"]:
                role_trace = task_result.get("role_trace") or []
                if not role_trace:
                    continue
                task_id = task_result["task"]["task_id"]
                path = trace_dir / f"{method}_seed{seed}_{task_id}.md"
                lines = [
                    f"# Role Trace: {method} / seed {seed} / {task_id}",
                    "",
                    f"- Score: {task_result['score']['score']}",
                    f"- LLM calls: {task_result['llm_call_count']}",
                    f"- Estimated prompt chars: {task_result['estimated_prompt_chars']}",
                    f"- Token usage: `{json.dumps(task_result.get('token_usage', {}))}`",
                    "",
                ]
                for step in role_trace:
                    lines.extend(
                        [
                            f"## {step.get('role', 'role')}",
                            "",
                            f"**Contribution:** {step.get('contribution', '')}",
                            "",
                            f"**Evidence updates:** `{json.dumps(step.get('evidence_updates', []), ensure_ascii=False)}`",
                            "",
                            f"**Concerns:** `{json.dumps(step.get('concerns', []), ensure_ascii=False)}`",
                            "",
                            f"**Next instruction:** {step.get('next_instruction', '')}",
                            "",
                        ]
                    )
                path.write_text("\n".join(lines), encoding="utf-8")
                index_lines.append(f"- [{path.name}](role_traces/{path.name})")
    if len(index_lines) == 2:
        index_lines.append("No role traces were generated. Use `--role-mode orchestrated` with multi-agent methods.")
    (workspace / "role_trace_index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")


def run_research_benchmark(
    *,
    workspace: Path,
    methods: list[str] | None = None,
    model: str = "deepseek-chat",
    seeds: list[int] | None = None,
    task_file: Path | None = None,
    command: str = "",
    role_mode: str = "metadata",
) -> dict[str, Any]:
    if role_mode not in {"metadata", "orchestrated"}:
        raise ValueError("role_mode must be `metadata` or `orchestrated`.")
    workspace.mkdir(parents=True, exist_ok=True)
    selected = [METHODS[name] for name in (methods or list(METHODS))]
    tasks_for_run = load_tasks(task_file)
    seeds = seeds or [0]
    results = []

    for method in selected:
        seed_summaries = []
        for seed in seeds:
            rng = random.Random(seed)
            tasks = list(tasks_for_run)
            rng.shuffle(tasks)
            policy = "Always ground novelty and claims in explicit evidence. Keep commands reproducible."
            structured_memory: list[dict[str, Any]] = []
            method_results = []
            for task in tasks:
                print(
                    f"[research-benchmark] method={method.name} seed={seed} task={task.task_id} role_mode={role_mode}",
                    flush=True,
                )
                effective_policy = (
                    _format_structured_memory_policy(policy, task, structured_memory)
                    if method.structured_memory
                    else policy
                )
                result = _run_one(task, method, model, effective_policy, seed, role_mode)
                if method.structured_memory:
                    result["structured_memory_before"] = [
                        {
                            "source_task_id": item.get("source_task_id", ""),
                            "source_score": item.get("source_score", 0),
                            "failure_tags": item.get("failure_tags", []),
                            "relevance": round(_memory_relevance(task, item), 4),
                        }
                        for item in sorted(
                            structured_memory,
                            key=lambda item: _memory_relevance(task, item),
                            reverse=True,
                        )[:3]
                    ]
                method_results.append(result)
                if method.structured_memory:
                    memory_record = _build_failure_memory(task, result)
                    structured_memory.append(memory_record)
                    result["structured_memory_after"] = memory_record
                    policy = (
                        "Always ground novelty and claims in explicit evidence. Keep commands reproducible.\n"
                        f"Structured memory contains {len(structured_memory)} task records; retrieve relevant failures before each task."
                    )
                update = result["answer"].get("policy_update", "")
                if method.self_evolve and update and not method.structured_memory:
                    policy = f"{policy}\n- {update}"
            total_score = sum(item["score"]["score"] for item in method_results)
            seed_summaries.append(
                {
                    "seed": seed,
                    "total_score": total_score,
                    "mean_task_score": round(total_score / len(method_results), 4),
                    "runtime_seconds": round(sum(item["runtime_seconds"] for item in method_results), 4),
                    "estimated_output_chars": sum(item["estimated_output_chars"] for item in method_results),
                    "estimated_prompt_chars": sum(item["estimated_prompt_chars"] for item in method_results),
                    "llm_call_count": sum(item["llm_call_count"] for item in method_results),
                    "token_usage": _usage_total([meta for item in method_results for meta in item.get("llm_call_meta", [])]),
                    "final_strategy_policy": policy,
                    "tasks": method_results,
                }
            )
            partial_results = results + [
                {
                    "method": method.name,
                    "mean_total_score": statistics.mean(item["total_score"] for item in seed_summaries),
                    "seeds": seed_summaries,
                }
            ]
            partial_summary = {
                "model": model,
                "role_mode": role_mode,
                "task_count": len(tasks_for_run),
                "task_source": str(task_file) if task_file else "default_micro_tasks",
                "task_ids": [task.task_id for task in tasks_for_run],
                "seeds": sorted({seed_result["seed"] for item in partial_results for seed_result in item.get("seeds", [])}),
                "results": partial_results,
                "checkpoint": {
                    "last_completed_method": method.name,
                    "last_completed_seed": seed,
                    "complete": False,
                },
            }
            (workspace / "research_benchmark_results.partial.json").write_text(
                json.dumps(partial_summary, indent=2),
                encoding="utf-8",
            )
        results.append(
            {
                "method": method.name,
                "mean_total_score": statistics.mean(item["total_score"] for item in seed_summaries),
                "seeds": seed_summaries,
            }
        )

    summary = {
        "model": model,
        "role_mode": role_mode,
        "task_count": len(tasks_for_run),
        "task_source": str(task_file) if task_file else "default_micro_tasks",
        "task_ids": [task.task_id for task in tasks_for_run],
        "seeds": seeds,
        "results": results,
        "checkpoint": {
            "complete": True,
        },
    }
    (workspace / "research_benchmark_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_tables(workspace, summary)
    _write_role_traces(workspace, summary)
    write_repro_manifest(workspace=workspace, command=command, summary=summary)
    return summary


def aggregate_result_scores(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in summary["results"]:
        totals = [seed_result["total_score"] for seed_result in item["seeds"]]
        rows.append(
            {
                "method": item["method"],
                "mean_total_score": round(statistics.mean(totals), 4),
                "std_total_score": round(statistics.pstdev(totals), 4) if len(totals) > 1 else 0.0,
            }
        )
    return rows


def merge_research_benchmark_results(
    *,
    base_results: Path,
    add_results: list[Path],
    workspace: Path,
    command: str = "",
) -> dict[str, Any]:
    summary = json.loads(base_results.read_text(encoding="utf-8"))
    existing = {item["method"] for item in summary.get("results", [])}
    for path in add_results:
        other = json.loads(path.read_text(encoding="utf-8"))
        if other.get("task_ids") != summary.get("task_ids"):
            raise ValueError(f"Cannot merge {path}: task_ids differ from base results.")
        if other.get("seeds") != summary.get("seeds"):
            raise ValueError(f"Cannot merge {path}: seeds differ from base results.")
        if other.get("role_mode") != summary.get("role_mode"):
            raise ValueError(f"Cannot merge {path}: role_mode differs from base results.")
        for method_result in other.get("results", []):
            method = method_result["method"]
            if method in existing:
                continue
            summary["results"].append(method_result)
            existing.add(method)
    summary["merged_from"] = [str(base_results)] + [str(path) for path in add_results]
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "research_benchmark_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_tables(workspace, summary)
    _write_role_traces(workspace, summary)
    write_repro_manifest(workspace=workspace, command=command, summary=summary)
    return summary


def extend_research_benchmark_results(
    *,
    base_results: Path,
    add_results: list[Path],
    workspace: Path,
    command: str = "",
) -> dict[str, Any]:
    summary = json.loads(base_results.read_text(encoding="utf-8"))
    method_map = {item["method"]: item for item in summary.get("results", [])}
    seed_set = set(summary.get("seeds", []))
    for path in add_results:
        other = json.loads(path.read_text(encoding="utf-8"))
        if other.get("task_ids") != summary.get("task_ids"):
            raise ValueError(f"Cannot extend {path}: task_ids differ from base results.")
        if other.get("role_mode") != summary.get("role_mode"):
            raise ValueError(f"Cannot extend {path}: role_mode differs from base results.")
        if other.get("task_source") != summary.get("task_source"):
            raise ValueError(f"Cannot extend {path}: task_source differs from base results.")
        for method_result in other.get("results", []):
            method = method_result["method"]
            target = method_map.get(method)
            if target is None:
                target = {"method": method, "mean_total_score": 0.0, "seeds": []}
                summary["results"].append(target)
                method_map[method] = target
            existing_seed_ids = {seed_result["seed"] for seed_result in target.get("seeds", [])}
            for seed_result in method_result.get("seeds", []):
                seed = seed_result["seed"]
                if seed in existing_seed_ids:
                    continue
                target.setdefault("seeds", []).append(seed_result)
                existing_seed_ids.add(seed)
                seed_set.add(seed)
    for method_result in summary.get("results", []):
        method_result["seeds"] = sorted(method_result.get("seeds", []), key=lambda item: item["seed"])
        method_result["mean_total_score"] = statistics.mean(item["total_score"] for item in method_result["seeds"])
    summary["seeds"] = sorted(seed_set)
    summary["extended_from"] = [str(base_results)] + [str(path) for path in add_results]
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "research_benchmark_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_tables(workspace, summary)
    _write_role_traces(workspace, summary)
    write_repro_manifest(workspace=workspace, command=command, summary=summary)
    return summary
