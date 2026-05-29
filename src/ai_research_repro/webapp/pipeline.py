from __future__ import annotations

import html
import json
import math
import re
import shutil
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ..benchmarks import recommend_hf_benchmarks, search_academic_sources, semantic_scholar_dedupe, spec_from_candidate
from ..compute_backends import (
    run_hf_job_experiment,
    run_local_cpu_experiment,
    run_local_gpu_experiment,
    run_ssh_remote_experiment,
)
from ..charts import save_learning_curve
from ..templates.nanogpt_lite import apply_patch, default_config, summarize_config
from .db import Artifact, Project, Run, RunEvent, SessionLocal, decrypt_text, init_db, utcnow
from .provider import OpenAICompatibleProvider, ProviderConfig


StageName = str


def slugify(text: str, max_length: int = 50) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    cleaned = re.sub(r"-+", "-", cleaned)
    return cleaned[:max_length].strip("-") or "research"


def _now_iso() -> str:
    return utcnow().isoformat()


def _clean_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip() or default


@dataclass
class RunControl:
    pause_points: set[str] = field(default_factory=set)
    resume_event: threading.Event = field(default_factory=threading.Event)
    stop_event: threading.Event = field(default_factory=threading.Event)
    notes: list[dict[str, Any]] = field(default_factory=list)
    last_stage: str = "queued"

    def __post_init__(self) -> None:
        self.resume_event.set()

    def should_pause(self, stage: str) -> bool:
        return stage in self.pause_points

    def pause(self) -> None:
        self.resume_event.clear()

    def resume(self) -> None:
        self.resume_event.set()

    def wait(self, timeout: float | None = None) -> bool:
        return self.resume_event.wait(timeout)

    def cancel(self) -> None:
        self.stop_event.set()
        self.resume_event.set()


class RunControllerRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._controls: dict[int, RunControl] = {}
        self._listeners: dict[int, list[Callable[[dict[str, Any]], None]]] = {}

    def register(self, run_id: int, control: RunControl) -> None:
        with self._lock:
            self._controls[run_id] = control
            self._listeners.setdefault(run_id, [])

    def get(self, run_id: int) -> RunControl | None:
        with self._lock:
            return self._controls.get(run_id)

    def unregister(self, run_id: int) -> None:
        with self._lock:
            self._controls.pop(run_id, None)
            self._listeners.pop(run_id, None)

    def add_listener(self, run_id: int, listener: Callable[[dict[str, Any]], None]) -> None:
        with self._lock:
            self._listeners.setdefault(run_id, []).append(listener)

    def publish(self, run_id: int, event: dict[str, Any]) -> None:
        listeners = []
        with self._lock:
            listeners = list(self._listeners.get(run_id, []))
        for listener in listeners:
            try:
                listener(event)
            except Exception:
                pass


RUN_CONTROLLERS = RunControllerRegistry()


def openai_provider_from_project(project: Project) -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        ProviderConfig(
            base_url=project.api_base_url,
            api_key=decrypt_text(project.api_key_enc),
            model=project.model_name,
            name=project.provider_name,
        )
    )


def _emit(
    session,
    run: Run,
    *,
    kind: str,
    stage: str,
    title: str,
    message: str,
    payload: dict[str, Any] | None = None,
    progress: int | None = None,
) -> dict[str, Any]:
    seq = (session.query(RunEvent).filter(RunEvent.run_id == run.id).count() or 0) + 1
    event = RunEvent(
        run_id=run.id,
        seq=seq,
        kind=kind,
        stage=stage,
        title=title,
        message=message,
        payload_json=payload or {},
    )
    session.add(event)
    if progress is not None:
        run.progress = max(run.progress, progress)
    run.current_stage = stage
    run.updated_at = utcnow()
    session.commit()
    session.refresh(event)
    event_dict = {
        "id": event.id,
        "run_id": event.run_id,
        "seq": event.seq,
        "kind": event.kind,
        "stage": event.stage,
        "title": event.title,
        "message": event.message,
        "payload": event.payload_json or {},
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }
    RUN_CONTROLLERS.publish(run.id, event_dict)
    return event_dict


def _artifact(
    session,
    run: Run,
    *,
    kind: str,
    label: str,
    file_path: Path,
    mime_type: str = "application/octet-stream",
) -> Artifact:
    artifact = Artifact(
        run_id=run.id,
        kind=kind,
        label=label,
        file_name=file_path.name,
        mime_type=mime_type,
        path=str(file_path),
        size_bytes=file_path.stat().st_size if file_path.exists() else 0,
    )
    session.add(artifact)
    session.commit()
    session.refresh(artifact)
    return artifact


def _wait_if_paused(control: RunControl, run: Run, session) -> None:
    if control.stop_event.is_set():
        raise RuntimeError("Run was cancelled by the user.")
    while not control.resume_event.wait(0.25):
        if control.stop_event.is_set():
            raise RuntimeError("Run was cancelled by the user.")
        session.refresh(run)


def _load_recent_notes(run: Run) -> list[dict[str, Any]]:
    notes = run.user_notes or []
    return notes[-10:]


def _topic_keywords(topic: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9]+", topic.lower())
    stop = {
        "a",
        "an",
        "and",
        "for",
        "of",
        "the",
        "to",
        "in",
        "on",
        "with",
        "by",
        "from",
        "using",
        "via",
        "towards",
        "toward",
        "based",
        "into",
    }
    keywords = [t for t in tokens if len(t) > 2 and t not in stop]
    return keywords[:8] or tokens[:4]


def _fallback_ideas(topic: str) -> list[dict[str, Any]]:
    keywords = _topic_keywords(topic)
    base = ", ".join(keywords[:3]) if keywords else "the topic"
    return [
        {
            "title": f"Context-aware baseline tuning for {base}",
            "hypothesis": "Small changes to the control parameters should improve robustness without increasing implementation complexity.",
            "novelty_gap": "Extends the topic with a lightweight, reproducible adaptation loop.",
            "patch": {"lr": 0.04, "weight_decay": 0.0005, "max_steps": 450},
            "expected_effect": "More stable validation curves and clearer ablation signals.",
            "risk": "May not transfer if the main issue is data mismatch rather than optimization.",
            "score": 0.62,
        },
        {
            "title": f"Search-budget allocation for {base}",
            "hypothesis": "Allocating more compute to the most promising branch should improve the final result under a fixed budget.",
            "novelty_gap": "Focuses on search policy rather than the base model itself.",
            "patch": {"batch_size": 96, "eval_interval": 40, "grad_clip": 0.8},
            "expected_effect": "Better candidate ranking and fewer wasted runs.",
            "risk": "Could overfit the search loop to the toy benchmark.",
            "score": 0.58,
        },
        {
            "title": f"Regularized multi-stage refinement for {base}",
            "hypothesis": "A staged pipeline with explicit checkpoints will improve reproducibility and make the strongest candidate easier to identify.",
            "novelty_gap": "Adds explicit stage-wise selection and failure analysis.",
            "patch": {"hidden_size": 160, "n_embd": 40, "lr": 0.045},
            "expected_effect": "Smoother training and a more interpretable performance gap.",
            "risk": "Might reduce representational capacity if the topic needs larger models.",
            "score": 0.56,
        },
    ]


def _score_idea_against_literature(idea: dict[str, Any], literature: list[dict[str, Any]], topic: str) -> dict[str, Any]:
    query = f"{topic} {idea.get('title', '')} {idea.get('hypothesis', '')}"
    hits = search_academic_sources(query, limit=5)
    dedupe = semantic_scholar_dedupe(query, limit=8)
    title_hits = sum(
        1
        for item in hits
        if (item.get("title") or "").lower() and any(tok in (item.get("title") or "").lower() for tok in _topic_keywords(idea.get("title", "")))
    )
    novelty_penalty = min(0.45, 0.12 * len(hits))
    overlap_penalty = min(0.25, 0.1 * title_hits)
    duplicate_penalty = min(0.2, float(dedupe.get("duplicate_score") or 0.0))
    base = float(idea.get("score") or 0.5)
    novelty_score = max(0.0, min(1.0, base + 0.25 - novelty_penalty - overlap_penalty - duplicate_penalty))
    return {
        **idea,
        "novelty_query": query,
        "novelty_hits": hits,
        "semantic_scholar_dedupe": dedupe,
        "novelty_score": novelty_score,
        "literature_overlap": title_hits,
        "supported_by": len(hits),
    }


def _fallback_benchmarks(topic: str) -> list[dict[str, Any]]:
    kws = _topic_keywords(topic)
    focus = kws[0] if kws else "the topic"
    return [
        {
            "name": f"Public benchmark search for {focus}",
            "metric": "validated match",
            "why_fit": "A public benchmark with searchable metadata is needed to anchor the claim.",
            "status": "candidate",
        },
        {
            "name": f"Open evaluation protocol for {focus}",
            "metric": "task-specific score",
            "why_fit": "If no public benchmark fits, define a small evaluation protocol around the topic's core claim.",
            "status": "candidate",
        },
    ]


def _fallback_plan(topic: str, benchmark: dict[str, Any], idea: dict[str, Any]) -> dict[str, Any]:
    return {
        "thesis": f"Test whether {idea['title']} improves the measured objective for {topic}.",
        "baseline": "Current default configuration / strongest public baseline found during literature review.",
        "ablation": [
            "Remove the proposed modification and re-run the same protocol.",
            "Change one critical knob at a time.",
        ],
        "robustness": ["Repeat with a different random seed", "Check sensitivity to smaller budget"],
        "failure_modes": ["No improvement over baseline", "Improvement disappears under sensitivity checks"],
        "benchmark": benchmark["name"],
    }


def _fallback_paper(run: Run, project: Project, idea: dict[str, Any], benchmark: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": f"AI Scientist-v2 Style Research Loop for {project.name}",
        "abstract": (
            f"We study {project.topic} with an autonomous research loop that generates candidate ideas, "
            f"checks novelty against literature, selects a benchmark, executes a sandbox experiment, and "
            f"iterates toward a defensible paper draft."
        ),
        "introduction": (
            "Existing research workflows often separate ideation, benchmarking, execution, and writing. "
            "Our system keeps them in a single loop so the output reflects evidence rather than intent."
        ),
        "related_work": "We automatically gathered nearby papers and compare the final direction against them.",
        "method": (
            f"The selected idea is {idea['title']}. We anchor evaluation to {benchmark['name']} and "
            f"use a staged loop with checkpoints, review, and revision."
        ),
        "experiments": (
            f"The sandbox run reports baseline val loss {summary.get('baseline_val_loss', float('nan')):.4f} "
            f"and best val loss {summary.get('best_val_loss', float('nan')):.4f}."
        ),
        "limitations": "This run uses a portable sandbox benchmark and should be extended with domain-specific adapters.",
        "conclusion": "The loop demonstrates how AI Scientist-v2 style orchestration can be exposed as a product workflow.",
    }


IDEA_SYSTEM = """You are the ideation module in an AI Scientist-v2 style research loop.
You must propose diverse, testable, paper-shaped candidate ideas. Return JSON only."""


def generate_candidate_ideas(
    provider: OpenAICompatibleProvider,
    *,
    topic: str,
    literature: list[dict[str, Any]],
    num_ideas: int = 3,
) -> list[dict[str, Any]]:
    user = json.dumps(
        {
            "topic": topic,
            "target_count": num_ideas,
            "literature": literature[:8],
            "requirements": [
                "Return a JSON array of candidate ideas.",
                "Each item must include title, hypothesis, novelty_gap, patch, expected_effect, risk, score.",
                "Patch should be a small JSON object of change knobs that can be evaluated in a sandbox.",
                "Ideas should be meaningfully different from each other.",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )

    def fallback() -> list[dict[str, Any]]:
        return _fallback_ideas(topic)[:num_ideas]

    result = provider.complete_json(system=IDEA_SYSTEM, user=user, fallback=fallback)
    if isinstance(result, dict) and "ideas" in result:
        result = result["ideas"]
    if not isinstance(result, list):
        return fallback()
    cleaned: list[dict[str, Any]] = []
    for item in result[:num_ideas]:
        if not isinstance(item, dict):
            continue
        cleaned.append(
            {
                "title": _clean_text(item.get("title"), "Untitled idea"),
                "hypothesis": _clean_text(item.get("hypothesis")),
                "novelty_gap": _clean_text(item.get("novelty_gap")),
                "patch": dict(item.get("patch") or {}),
                "expected_effect": _clean_text(item.get("expected_effect")),
                "risk": _clean_text(item.get("risk")),
                "score": float(item.get("score") or 0.0),
            }
        )
    return cleaned or fallback()


BENCHMARK_SYSTEM = """You are the benchmark discovery module in an AI Scientist-v2 style research loop.
Pick public, searchable evaluation targets that fit the claim. Return JSON only."""


def discover_benchmarks(
    provider: OpenAICompatibleProvider,
    *,
    topic: str,
    ideas: list[dict[str, Any]],
    literature: list[dict[str, Any]],
    experiment_template: str = "sandbox",
) -> list[dict[str, Any]]:
    if experiment_template == "hf-streaming":
        return recommend_hf_benchmarks(topic=topic, ideas=ideas, literature=literature, limit=5)

    user = json.dumps(
        {
            "topic": topic,
            "ideas": ideas,
            "literature": literature[:10],
            "requirements": [
                "Return a JSON array of benchmark candidates.",
                "Each item must include name, metric, why_fit, query, status.",
                "Prefer publicly searchable benchmarks; if uncertain, say candidate.",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )

    def fallback() -> list[dict[str, Any]]:
        return _fallback_benchmarks(topic)

    result = provider.complete_json(system=BENCHMARK_SYSTEM, user=user, fallback=fallback)
    if isinstance(result, dict) and "benchmarks" in result:
        result = result["benchmarks"]
    if not isinstance(result, list):
        return fallback()
    candidates: list[dict[str, Any]] = []
    for item in result[:5]:
        if not isinstance(item, dict):
            continue
        name = _clean_text(item.get("name"))
        query = _clean_text(item.get("query"), name)
        verification = search_academic_sources(query, limit=3)
        candidates.append(
            {
                "name": name,
                "metric": _clean_text(item.get("metric"), "task-specific score"),
                "why_fit": _clean_text(item.get("why_fit")),
                "query": query,
                "status": _clean_text(item.get("status"), "candidate"),
                "verification": verification,
                "confidence": min(1.0, 0.25 + 0.15 * len(verification)),
            }
        )
    return candidates or fallback()


PLAN_SYSTEM = """You are the experiment design module in an AI Scientist-v2 style research loop.
Turn the selected idea into a staged, reproducible experiment plan. Return JSON only."""


def design_experiment_plan(
    provider: OpenAICompatibleProvider,
    *,
    topic: str,
    idea: dict[str, Any],
    benchmark: dict[str, Any],
    literature: list[dict[str, Any]],
    user_notes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    user = json.dumps(
        {
            "topic": topic,
            "selected_idea": idea,
            "benchmark": benchmark,
            "literature": literature[:10],
            "user_notes": user_notes or [],
            "requirements": [
                "Return a JSON object with thesis, baseline, ablation, robustness, failure_modes, sandbox_patch.",
                "sandbox_patch must be a small JSON object compatible with the toy benchmark knobs.",
                "Include stage names: initial_implementation, hyperparameter_tuning, proposed_method, ablation_studies.",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    if benchmark.get("backend") == "huggingface":
        requirements = json.loads(user)
        requirements["requirements"].extend(
            [
                "Include the exact datasets.load_dataset one-line loader snippet from the benchmark metadata.",
                "Use streaming=True by default so HF data stays remote and is only materialized as a bounded local sample.",
            ]
        )
        user = json.dumps(requirements, ensure_ascii=False, indent=2)

    def fallback() -> dict[str, Any]:
        return _fallback_plan(topic, benchmark, idea)

    result = provider.complete_json(system=PLAN_SYSTEM, user=user, fallback=fallback)
    if isinstance(result, dict):
        result.setdefault("benchmark", benchmark.get("name"))
        result.setdefault("sandbox_patch", idea.get("patch") or {})
        result.setdefault("benchmark_backend", benchmark.get("backend", "sandbox"))
        result.setdefault("benchmark_loader_snippet", benchmark.get("loader_snippet"))
        result.setdefault("benchmark_dataset_id", benchmark.get("dataset_id"))
        result.setdefault("benchmark_split", benchmark.get("split"))
        return result
    return fallback()


def _prepare_hf_benchmark(
    benchmark: dict[str, Any],
    *,
    output_dir: Path,
) -> tuple[list[dict[str, Any]], str | None, str | None]:
    spec = spec_from_candidate(benchmark)
    hf_loader_snippet = spec.loader_snippet
    try:
        hf_preview = spec.preview(limit=5)
    except Exception as exc:
        hf_preview = [{"error": f"preview failed: {type(exc).__name__}", "dataset_id": spec.dataset_id}]
    try:
        corpus_text = spec.build_corpus(limit=benchmark.get("sample_limit") or spec.sample_limit)
    except Exception as exc:
        corpus_text = json.dumps(
            {
                "benchmark": benchmark.get("name"),
                "dataset_id": spec.dataset_id,
                "split": spec.split,
                "loader_snippet": hf_loader_snippet,
                "error": f"materialization failed: {type(exc).__name__}: {exc}",
            },
            ensure_ascii=False,
            indent=2,
        )
    hf_meta = {
        "benchmark": benchmark,
        "preview": hf_preview,
        "loader_snippet": hf_loader_snippet,
        "corpus_chars": len(corpus_text or ""),
    }
    hf_meta_path = output_dir / "hf_benchmark_meta.json"
    hf_meta_path.write_text(json.dumps(hf_meta, indent=2, ensure_ascii=False), encoding="utf-8")
    hf_corpus_path = output_dir / "hf_benchmark_corpus.txt"
    hf_corpus_path.write_text(corpus_text or "", encoding="utf-8")
    return hf_preview, hf_loader_snippet, corpus_text


def _run_compute_backend(
    *,
    backend: str,
    benchmark: dict[str, Any],
    config,
    output_dir: Path,
    corpus_text: str | None,
    metadata: dict[str, Any],
) -> Any:
    if backend == "local-gpu":
        return run_local_gpu_experiment(config=config, out_dir=output_dir, corpus_text=corpus_text, metadata=metadata)
    if backend == "ssh-remote-gpu":
        remote = benchmark.get("compute_config") or {}
        return run_ssh_remote_experiment(
            out_dir=output_dir,
            host=str(remote.get("host") or ""),
            user=remote.get("user") or None,
            port=int(remote["port"]) if remote.get("port") else None,
            identity_file=remote.get("identity_file") or None,
            remote_workdir=remote.get("remote_workdir") or None,
            remote_python=remote.get("remote_python") or "python3",
            corpus_text=corpus_text,
            config=config,
            env=remote.get("env") or {},
            metadata=metadata,
        )
    if backend == "hf-job":
        remote = benchmark.get("compute_config") or {}
        command = remote.get("command") or [
            "python3",
            "-c",
            "from ai_research_repro.templates.nanogpt_lite import default_config, train_and_evaluate; "
            "import json; from pathlib import Path; "
            "result = train_and_evaluate(default_config(), out_dir=Path('remote_run')); "
            "print('===AI_RESEARCH_RESULT_JSON_START==='); "
            "print(json.dumps(result, ensure_ascii=False)); "
            "print('===AI_RESEARCH_RESULT_JSON_END===')",
        ]
        return run_hf_job_experiment(
            out_dir=output_dir,
            image=str(remote.get("image") or "python:3.11-slim"),
            command=command,
            flavor=str(remote.get("flavor") or "a10g-small"),
            env=remote.get("env") or {},
            secrets=remote.get("secrets") or {},
            metadata=metadata,
        )
    return run_local_cpu_experiment(config=config, out_dir=output_dir, corpus_text=corpus_text, metadata=metadata)


def run_sandbox_experiments(
    *,
    run: Run,
    idea: dict[str, Any],
    benchmark: dict[str, Any],
    plan: dict[str, Any],
    output_dir: Path,
    emit: Callable[..., dict[str, Any]],
    session,
    compute_backend: str = "local-cpu",
    compute_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base_cfg = default_config()
    candidate_patch = dict(idea.get("patch") or {})
    sandbox_patch = dict(plan.get("sandbox_patch") or {})
    combined_patch = {**sandbox_patch, **candidate_patch}
    candidate_cfg = apply_patch(base_cfg, combined_patch)

    baseline_dir = output_dir / "baseline"
    candidate_dir = output_dir / "candidate"
    hf_preview: list[dict[str, Any]] = []
    hf_loader_snippet: str | None = None
    hf_corpus_path: Path | None = None
    corpus_text: str | None = None
    backend = benchmark.get("backend", "sandbox")
    benchmark_metadata: dict[str, Any] = {"backend": backend}

    if backend == "huggingface":
        hf_preview, hf_loader_snippet, corpus_text = _prepare_hf_benchmark(benchmark, output_dir=output_dir)
        hf_meta_path = output_dir / "hf_benchmark_meta.json"
        hf_corpus_path = output_dir / "hf_benchmark_corpus.txt"
        emit(
            session,
            run,
            kind="benchmark.materialized",
            stage="benchmark",
            title="HF benchmark streamed",
            message="The selected Hugging Face benchmark was streamed locally and converted into a bounded corpus sample.",
            payload={"benchmark": benchmark, "preview": hf_preview, "loader_snippet": hf_loader_snippet},
            progress=38,
        )
        save_artifact(session, run, "json", "hf benchmark metadata", hf_meta_path, "application/json")
        save_artifact(session, run, "text", "hf benchmark corpus", hf_corpus_path, "text/plain")

    benchmark = dict(benchmark)
    benchmark["compute_config"] = dict(compute_config or {})
    baseline_result = _run_compute_backend(
        backend=compute_backend,
        benchmark=benchmark,
        config=base_cfg,
        output_dir=baseline_dir,
        corpus_text=corpus_text,
        metadata={**benchmark_metadata, "role": "baseline"},
    )
    candidate_result = _run_compute_backend(
        backend=compute_backend,
        benchmark=benchmark,
        config=candidate_cfg,
        output_dir=candidate_dir,
        corpus_text=corpus_text,
        metadata={**benchmark_metadata, "role": "candidate"},
    )

    save_learning_curve(candidate_result.history, output_dir / "best_learning_curve.svg")
    (output_dir / "baseline_config.json").write_text(summarize_config(base_cfg), encoding="utf-8")
    (output_dir / "candidate_config.json").write_text(summarize_config(candidate_cfg), encoding="utf-8")

    emit(
        session,
        run,
        kind="experiment.result",
        stage="execution",
        title="Benchmark complete",
        message="The selected execution backend finished and produced comparable baseline/candidate metrics.",
        payload={
            "baseline": baseline_result.metrics,
            "candidate": candidate_result.metrics,
            "patch": combined_patch,
            "backend": compute_backend,
            "benchmark_backend": backend,
            "hf_loader_snippet": hf_loader_snippet,
        },
        progress=78,
    )

    return {
        "baseline": baseline_result.__dict__,
        "candidate": candidate_result.__dict__,
        "combined_patch": combined_patch,
        "hf_preview": hf_preview,
        "hf_loader_snippet": hf_loader_snippet,
        "hf_corpus_path": str(hf_corpus_path) if hf_corpus_path else None,
        "compute_backend": compute_backend,
    }


PAPER_SYSTEM = """You are the manuscript writer in an AI Scientist-v2 style research loop.
Write a complete paper-shaped structured summary grounded in the provided artifacts.
Return JSON only."""

PAPER_REVIEW_SYSTEM = """You are a strict paper reviewer in an AI Scientist-v2 style research loop.
Score the manuscript for novelty, clarity, feasibility, and alignment with the evidence.
Return JSON only."""

PAPER_REVISE_SYSTEM = """You are a scientific manuscript reviser in an AI Scientist-v2 style research loop.
Revise the paper to address reviewer feedback while staying grounded in the evidence.
Return JSON only."""


def draft_paper(
    provider: OpenAICompatibleProvider,
    *,
    project: Project,
    run: Run,
    topic: str,
    idea: dict[str, Any],
    benchmark: dict[str, Any],
    summary: dict[str, Any],
    literature: list[dict[str, Any]],
    plan: dict[str, Any],
    user_notes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    user = json.dumps(
        {
            "project": project.name,
            "topic": topic,
            "selected_idea": idea,
            "benchmark": benchmark,
            "summary": summary,
            "literature": literature[:8],
            "plan": plan,
            "user_notes": user_notes or [],
            "requirements": [
                "Return JSON with title, abstract, introduction, related_work, method, experiments, limitations, conclusion.",
                "Use concise academic prose.",
                "Do not invent metrics beyond the supplied summary.",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )

    def fallback() -> dict[str, Any]:
        return _fallback_paper(run, project, idea, benchmark, summary)

    result = provider.complete_json(system=PAPER_SYSTEM, user=user, fallback=fallback)
    if isinstance(result, dict):
        result.setdefault("title", f"{project.name}: AI Scientist-v2 Style Discovery Loop")
        result.setdefault("abstract", fallback()["abstract"])
        result.setdefault("limitations", fallback()["limitations"])
        return result
    return fallback()


def review_paper(
    provider: OpenAICompatibleProvider,
    *,
    paper: dict[str, Any],
    benchmark: dict[str, Any],
    summary: dict[str, Any],
    literature: list[dict[str, Any]],
    user_notes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    user = json.dumps(
        {
            "paper": paper,
            "benchmark": benchmark,
            "summary": summary,
            "literature": literature[:8],
            "user_notes": user_notes or [],
            "requirements": [
                "Return JSON with overall, novelty, clarity, feasibility, strengths, weaknesses, recommendation, revision_focus.",
                "Use recommendation values like revise, accept, or hold.",
                "Ground comments in the provided evidence.",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )

    def fallback() -> dict[str, Any]:
        delta = float(summary.get("delta_val_loss") or 0.0)
        score = 6.0 + (0.8 if delta < 0 else 0.0)
        return {
            "overall": round(score, 2),
            "novelty": 6.5,
            "clarity": 7.0,
            "feasibility": 7.0,
            "strengths": ["Grounded in evidence", "Clear benchmark alignment"],
            "weaknesses": ["Needs stronger novelty framing", "Could be more explicit about limits"],
            "recommendation": "revise" if score < 7.3 else "hold",
            "revision_focus": "Strengthen the claim, sharpen the contribution, and tighten the limitations.",
        }

    result = provider.complete_json(system=PAPER_REVIEW_SYSTEM, user=user, fallback=fallback)
    if isinstance(result, dict):
        result.setdefault("overall", 0.0)
        result.setdefault("novelty", 0.0)
        result.setdefault("clarity", 0.0)
        result.setdefault("feasibility", 0.0)
        result.setdefault("strengths", [])
        result.setdefault("weaknesses", [])
        result.setdefault("recommendation", "revise")
        result.setdefault("revision_focus", "")
        return result
    return fallback()


def revise_paper(
    provider: OpenAICompatibleProvider,
    *,
    paper: dict[str, Any],
    review: dict[str, Any],
    summary: dict[str, Any],
    literature: list[dict[str, Any]],
    user_notes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    user = json.dumps(
        {
            "paper": paper,
            "review": review,
            "summary": summary,
            "literature": literature[:8],
            "user_notes": user_notes or [],
            "requirements": [
                "Return a revised JSON paper with the same keys as the input manuscript.",
                "Tighten claims, improve the method and experiment description, and reflect the reviewer feedback.",
                "Do not invent new metrics or results.",
            ],
        },
        ensure_ascii=False,
        indent=2,
    )

    def fallback() -> dict[str, Any]:
        revised = dict(paper)
        revised["abstract"] = paper.get("abstract", "") + " The final version was revised after automated review."
        revised["limitations"] = (
            paper.get("limitations", "")
            + " Reviewer feedback emphasized that the evidence is strongest for the sandbox benchmark, so claims are kept narrow."
        ).strip()
        revised["conclusion"] = paper.get("conclusion", "") + " The revised manuscript narrows the claim to the supported scope."
        return revised

    result = provider.complete_json(system=PAPER_REVISE_SYSTEM, user=user, fallback=fallback)
    if isinstance(result, dict):
        result.setdefault("title", paper.get("title"))
        result.setdefault("abstract", paper.get("abstract"))
        result.setdefault("limitations", paper.get("limitations"))
        return result
    return fallback()


def render_paper_html(
    *,
    project: Project,
    run: Run,
    paper: dict[str, Any],
    idea: dict[str, Any],
    benchmark: dict[str, Any],
    literature: list[dict[str, Any]],
    summary: dict[str, Any],
) -> str:
    lit_items = "".join(
        f"<li><strong>{html.escape(item.get('title') or 'Untitled')}</strong>"
        f" <span class='muted'>({html.escape(str(item.get('year') or 'n.d.'))})</span><br>"
        f"<span class='muted'>{html.escape((item.get('venue') or ''))}</span><br>"
        f"{html.escape((item.get('abstract') or '')[:240])}</li>"
        for item in literature[:6]
    ) or "<li>No literature hits available.</li>"

    def section(title: str, body: str) -> str:
        return f"<section class='paper-section'><h2>{html.escape(title)}</h2><p>{html.escape(body).replace(chr(10), '<br>')}</p></section>"

    metrics_html = "".join(
        f"<div class='metric'><span>{html.escape(key)}</span><strong>{html.escape(str(value))}</strong></div>"
        for key, value in summary.items()
    )

    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(paper.get('title') or project.name)}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #09111f;
      --bg2: #101b32;
      --card: rgba(17, 25, 43, 0.78);
      --card-border: rgba(148, 163, 184, 0.18);
      --text: #e5eefc;
      --muted: #91a4c7;
      --accent: #7dd3fc;
      --accent2: #f472b6;
      --line: rgba(125, 211, 252, 0.2);
    }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(125, 211, 252, 0.16), transparent 30%),
        radial-gradient(circle at top right, rgba(244, 114, 182, 0.12), transparent 24%),
        linear-gradient(180deg, var(--bg), #0d1729 70%, #08101c);
      color: var(--text);
    }}
    .paper {{
      max-width: 980px;
      margin: 0 auto;
      padding: 48px 32px 72px;
    }}
    .hero {{
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.86), rgba(15, 23, 42, 0.65));
      border: 1px solid var(--card-border);
      border-radius: 28px;
      padding: 32px;
      box-shadow: 0 28px 70px rgba(2, 6, 23, 0.45);
    }}
    .eyebrow {{
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-size: 12px;
      margin-bottom: 12px;
    }}
    h1 {{
      font-size: 42px;
      line-height: 1.05;
      margin: 0 0 16px;
    }}
    .sub {{
      color: var(--muted);
      max-width: 760px;
      line-height: 1.7;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 14px;
      margin: 22px 0 0;
    }}
    .metric, .card {{
      background: var(--card);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 16px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}
    .metric strong {{
      font-size: 20px;
    }}
    .content {{
      margin-top: 26px;
      display: grid;
      gap: 18px;
    }}
    .paper-section {{
      background: rgba(15, 23, 42, 0.72);
      border: 1px solid var(--card-border);
      border-radius: 22px;
      padding: 24px;
    }}
    .paper-section h2 {{
      margin: 0 0 14px;
      font-size: 22px;
    }}
    .paper-section p, .paper-section li {{
      color: #d8e3f5;
      line-height: 1.75;
    }}
    .two-col {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 18px;
    }}
    .muted {{
      color: var(--muted);
    }}
    .code-snippet {{
      background: #0f172a;
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 12px;
      color: #cbd5e1;
      padding: 14px 16px;
      overflow-x: auto;
      font-size: 12px;
      line-height: 1.6;
    }}
    ul {{
      margin: 0;
      padding-left: 20px;
    }}
    .footer {{
      margin-top: 28px;
      color: var(--muted);
      font-size: 12px;
      text-align: center;
    }}
  </style>
</head>
<body>
  <main class="paper">
    <section class="hero">
      <div class="eyebrow">AI Scientist-v2 Research Loop</div>
      <h1>{html.escape(paper.get("title") or project.name)}</h1>
      <p class="sub">{html.escape(paper.get("abstract") or "")}</p>
      <div class="grid">{metrics_html}</div>
    </section>

    <div class="content">
    <section class="paper-section">
        <h2>Research Context</h2>
        <div class="two-col">
          <div>
            <p><strong>Topic:</strong> {html.escape(project.topic)}</p>
            <p><strong>Selected idea:</strong> {html.escape(idea.get("title") or "")}</p>
            <p><strong>Benchmark:</strong> {html.escape(benchmark.get("name") or "")}</p>
            <p><strong>Benchmark backend:</strong> {html.escape(benchmark.get("backend") or "sandbox")}</p>
            <p><strong>Benchmark dataset:</strong> {html.escape(benchmark.get("dataset_id") or "local sandbox")}</p>
            <p><strong>Benchmark split:</strong> {html.escape(benchmark.get("split") or "n/a")}</p>
            <p><strong>Run label:</strong> {html.escape(run.label)}</p>
          </div>
          <div>
            <p class="muted">This paper draft is generated from the full research loop: ideation, literature review, benchmark discovery, experiment execution, and revision.</p>
            {f'<pre class="code-snippet">{html.escape(str(benchmark.get("loader_snippet") or ""))}</pre>' if benchmark.get("backend") == "huggingface" and benchmark.get("loader_snippet") else ""}
          </div>
        </div>
      </section>
      {section("Introduction", paper.get("introduction") or "")}
      {section("Related Work", paper.get("related_work") or "")}
      {section("Method", paper.get("method") or "")}
      {section("Experiments", paper.get("experiments") or "")}
      {section("Limitations", paper.get("limitations") or "")}
      {section("Conclusion", paper.get("conclusion") or "")}

      <section class="paper-section">
        <h2>Literature Snapshot</h2>
        <ul>{lit_items}</ul>
      </section>
    </div>
    <div class="footer">Generated by the local AI Scientist-v2 style workspace.</div>
  </main>
</body>
</html>
"""


def export_pdf_from_html(html_path: Path, pdf_path: Path) -> None:
    from playwright.sync_api import sync_playwright

    browser_paths = [
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    with sync_playwright() as p:
        launch_kwargs = {"headless": True}
        for candidate in browser_paths:
            if candidate and Path(candidate).exists():
                launch_kwargs["executable_path"] = str(candidate)
                break
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page(viewport={"width": 1440, "height": 2400}, device_scale_factor=1)
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.pdf(path=str(pdf_path), print_background=True, format="A4", margin={"top": "10mm", "bottom": "12mm", "left": "10mm", "right": "10mm"})
        browser.close()


def save_artifact(session, run: Run, kind: str, label: str, file_path: Path, mime_type: str = "application/octet-stream") -> Artifact:
    return _artifact(session, run, kind=kind, label=label, file_path=file_path, mime_type=mime_type)


def run_full_loop(
    *,
    run_id: int,
    session_factory=SessionLocal,
    emit: Callable[..., dict[str, Any]],
    control: RunControl,
) -> dict[str, Any]:
    init_db()
    session = session_factory()
    try:
        run = session.get(Run, run_id)
        if run is None:
            raise RuntimeError(f"Run {run_id} was not found.")
        project = session.get(Project, run.project_id)
        if project is None:
            raise RuntimeError("Project not found for run.")

        provider = openai_provider_from_project(project)
        topic = project.topic.strip()
        output_dir = Path(run.output_dir or (Path("data") / "runs" / f"run-{run.id}"))
        output_dir.mkdir(parents=True, exist_ok=True)
        run.output_dir = str(output_dir)
        run.status = "running"
        run.current_stage = "ideation"
        run.progress = 2
        session.commit()

        emit(session, run, kind="run.started", stage="ideation", title="Run started", message="The AI Scientist-v2 style loop has started.", payload={"topic": topic, "model": project.model_name}, progress=2)

        literature_query = topic
        literature = search_academic_sources(literature_query, limit=5)
        emit(session, run, kind="literature.search", stage="ideation", title="Literature searched", message="Initial academic sources were gathered to anchor ideation.", payload={"query": literature_query, "results": literature[:5]}, progress=6)

        ideas = generate_candidate_ideas(provider, topic=topic, literature=literature, num_ideas=3)
        emit(session, run, kind="ideas.generated", stage="ideation", title="Candidate ideas generated", message="Three candidate ideas were proposed.", payload={"ideas": ideas}, progress=14)

        scored_ideas = []
        for idx, idea in enumerate(ideas, start=1):
            scored = _score_idea_against_literature(idea, literature, topic)
            scored_ideas.append(scored)
            emit(
                session,
                run,
                kind="idea.checked",
                stage="ideation",
                title=f"Idea {idx} checked against literature",
                message=f"{scored['title']} was checked for novelty and overlap with academic sources.",
                payload={
                    "idea": scored,
                    "novelty_hits": scored["novelty_hits"][:5],
                    "novelty_score": scored["novelty_score"],
                },
                progress=14 + idx,
            )

        ideas_path = output_dir / "ideas.json"
        ideas_path.write_text(json.dumps(scored_ideas, indent=2, ensure_ascii=False), encoding="utf-8")
        save_artifact(session, run, "json", "candidate ideas", ideas_path, "application/json")

        if control.should_pause("ideation"):
            run.status = "waiting_user"
            session.commit()
            emit(session, run, kind="run.paused", stage="ideation", title="Paused for feedback", message="The run is waiting for user feedback before literature/benchmark selection continues.", payload={"checkpoint": "ideation"}, progress=15)
            _wait_if_paused(control, run, session)
            run.status = "running"
            session.commit()

        notes = _load_recent_notes(run)
        if notes:
            emit(session, run, kind="user.notes", stage="ideation", title="User feedback available", message="Recent user notes will be incorporated into downstream prompts.", payload={"notes": notes}, progress=16)

        ranked_ideas = sorted(
            scored_ideas,
            key=lambda item: (
                float(item.get("novelty_score") or item.get("score") or 0.0),
                -len(item.get("risk") or ""),
            ),
            reverse=True,
        )
        emit(
            session,
            run,
            kind="ideas.ranked",
            stage="literature",
            title="Candidate ideas ranked",
            message="The system sorted ideas by novelty evidence and feasibility proxy scores.",
            payload={"ranked": ranked_ideas},
            progress=19,
        )
        selected_idea = ranked_ideas[0]
        emit(session, run, kind="ideas.selected", stage="literature", title="Selected candidate", message=f"Selected idea: {selected_idea['title']}", payload={"selected": selected_idea, "ranked": ranked_ideas}, progress=20)

        literature_focus = search_academic_sources(f"{topic} {selected_idea['title']}", limit=8)
        literature.extend(literature_focus)
        literature_path = output_dir / "literature.json"
        literature_path.write_text(json.dumps(literature[:12], indent=2, ensure_ascii=False), encoding="utf-8")
        save_artifact(session, run, "json", "literature snapshot", literature_path, "application/json")
        emit(session, run, kind="literature.refined", stage="literature", title="Literature refinement complete", message="The search was re-run around the selected idea to refine novelty checking.", payload={"results": literature_focus[:6], "selected_idea": selected_idea}, progress=26)

        benchmarks = discover_benchmarks(
            provider,
            topic=topic,
            ideas=ideas,
            literature=literature[:12],
            experiment_template=project.experiment_template,
        )
        benchmarks_path = output_dir / "benchmarks.json"
        benchmarks_path.write_text(json.dumps(benchmarks, indent=2, ensure_ascii=False), encoding="utf-8")
        save_artifact(session, run, "json", "benchmark candidates", benchmarks_path, "application/json")
        selected_benchmark = max(benchmarks, key=lambda item: float(item.get("confidence") or 0.0)) if benchmarks else {"name": "Open evaluation protocol", "metric": "validated score", "verification": []}
        emit(session, run, kind="benchmark.selected", stage="benchmark", title="Benchmark selected", message=f"Selected benchmark: {selected_benchmark['name']}", payload={"benchmark": selected_benchmark, "all": benchmarks}, progress=34)

        if control.should_pause("benchmark"):
            run.status = "waiting_user"
            session.commit()
            emit(session, run, kind="run.paused", stage="benchmark", title="Paused for benchmark review", message="The run is waiting for user feedback before experiment design continues.", payload={"checkpoint": "benchmark"}, progress=35)
            _wait_if_paused(control, run, session)
            run.status = "running"
            session.commit()

        plan = design_experiment_plan(
            provider,
            topic=topic,
            idea=selected_idea,
            benchmark=selected_benchmark,
            literature=literature[:12],
            user_notes=notes,
        )
        plan_path = output_dir / "experiment_plan.json"
        plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
        save_artifact(session, run, "json", "experiment plan", plan_path, "application/json")
        emit(session, run, kind="experiment.plan", stage="planning", title="Experiment plan drafted", message="A structured multi-stage experiment plan was generated.", payload={"plan": plan}, progress=42)

        if control.should_pause("planning"):
            run.status = "waiting_user"
            session.commit()
            emit(session, run, kind="run.paused", stage="planning", title="Paused for plan review", message="The run is waiting for user feedback before execution begins.", payload={"checkpoint": "planning"}, progress=43)
            _wait_if_paused(control, run, session)
            run.status = "running"
            session.commit()

        run_dir = output_dir / "sandbox"
        run_dir.mkdir(parents=True, exist_ok=True)
        exec_result = run_sandbox_experiments(
            run=run,
            idea=selected_idea,
            benchmark=selected_benchmark,
            plan=plan,
            output_dir=run_dir,
            emit=emit,
            session=session,
            compute_backend=project.compute_backend,
            compute_config=project.compute_config_json or {},
        )
        baseline_result = exec_result["baseline"]
        candidate_result = exec_result["candidate"]
        summary = {
            "baseline_val_loss": baseline_result["metrics"]["final_val_loss"],
            "best_val_loss": candidate_result["metrics"]["final_val_loss"],
            "delta_val_loss": candidate_result["metrics"]["final_val_loss"] - baseline_result["metrics"]["final_val_loss"],
            "baseline_train_loss": baseline_result["metrics"]["final_train_loss"],
            "best_train_loss": candidate_result["metrics"]["final_train_loss"],
            "benchmark": selected_benchmark.get("name"),
            "benchmark_backend": selected_benchmark.get("backend", "sandbox"),
            "benchmark_dataset_id": selected_benchmark.get("dataset_id"),
            "benchmark_split": selected_benchmark.get("split"),
            "benchmark_loader_snippet": selected_benchmark.get("loader_snippet"),
            "candidate_patch": exec_result["combined_patch"],
            "hf_preview": exec_result.get("hf_preview", []),
        }
        summary_path = output_dir / "summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        save_artifact(session, run, "json", "summary", summary_path, "application/json")
        emit(session, run, kind="evaluation.summary", stage="execution", title="Experiment summary prepared", message="Baseline and candidate results were summarized for the manuscript.", payload=summary, progress=62)

        if control.should_pause("execution"):
            run.status = "waiting_user"
            session.commit()
            emit(session, run, kind="run.paused", stage="execution", title="Paused for experimental review", message="The run is waiting for user feedback before paper drafting begins.", payload={"checkpoint": "execution"}, progress=63)
            _wait_if_paused(control, run, session)
            run.status = "running"
            session.commit()

        paper = draft_paper(
            provider,
            project=project,
            run=run,
            topic=topic,
            idea=selected_idea,
            benchmark=selected_benchmark,
        summary=summary,
        literature=literature[:12],
        plan=plan,
        user_notes=notes,
    )
        review_rounds: list[dict[str, Any]] = []
        for round_idx in range(2):
            review = review_paper(
                provider,
                paper=paper,
                benchmark=selected_benchmark,
                summary=summary,
                literature=literature[:12],
                user_notes=notes,
            )
            review_rounds.append(review)
            emit(
                session,
                run,
                kind="paper.review",
                stage="writing",
                title=f"Paper review round {round_idx + 1}",
                message=f"Automated reviewer score: {review.get('overall')}",
                payload={"round": round_idx + 1, "review": review},
                progress=82 + round_idx,
            )
            if float(review.get("overall") or 0.0) >= 7.3 and str(review.get("recommendation") or "").lower() not in {"revise", "reject"}:
                break
            paper = revise_paper(
                provider,
                paper=paper,
                review=review,
                summary=summary,
                literature=literature[:12],
                user_notes=notes,
            )
            emit(
                session,
                run,
                kind="paper.revised",
                stage="writing",
                title=f"Paper revised after round {round_idx + 1}",
                message="The manuscript was revised according to the reviewer feedback.",
                payload={"round": round_idx + 1, "paper": paper},
                progress=83 + round_idx,
            )
        paper_html = render_paper_html(project=project, run=run, paper=paper, idea=selected_idea, benchmark=selected_benchmark, literature=literature[:12], summary=summary)
        paper_html_path = output_dir / "paper.html"
        paper_md_path = output_dir / "paper.json"
        paper_html_path.write_text(paper_html, encoding="utf-8")
        paper_md_path.write_text(json.dumps(paper, indent=2, ensure_ascii=False), encoding="utf-8")
        save_artifact(session, run, "html", "paper html", paper_html_path, "text/html")
        save_artifact(session, run, "json", "paper json", paper_md_path, "application/json")

        pdf_path = output_dir / "paper.pdf"
        try:
            export_pdf_from_html(paper_html_path, pdf_path)
            run.pdf_path = str(pdf_path)
            save_artifact(session, run, "pdf", "paper pdf", pdf_path, "application/pdf")
            emit(session, run, kind="paper.pdf", stage="writing", title="PDF exported", message="The manuscript was rendered to PDF and stored in the run directory.", payload={"pdf_path": str(pdf_path)}, progress=85)
        except Exception as exc:
            run.error_text = f"PDF export failed: {exc}"
            emit(session, run, kind="paper.pdf_failed", stage="writing", title="PDF export failed", message=str(exc), payload={"paper_html": str(paper_html_path)}, progress=85)

        if control.should_pause("writing"):
            run.status = "waiting_user"
            session.commit()
            emit(session, run, kind="run.paused", stage="writing", title="Paused for final review", message="The run is waiting for user feedback before it is finalized.", payload={"checkpoint": "writing"}, progress=86)
            _wait_if_paused(control, run, session)
            run.status = "running"
            session.commit()

        run.summary_json = summary
        run.paper_html = paper_html
        run.paper_markdown = json.dumps(paper, indent=2, ensure_ascii=False)
        run.status = "completed"
        run.current_stage = "completed"
        run.progress = 100
        session.commit()

        emit(session, run, kind="run.completed", stage="completed", title="Run complete", message="The research loop finished and all artifacts were persisted.", payload={"summary": summary, "paper_title": paper.get("title")}, progress=100)

        return {
            "run_id": run.id,
            "summary": summary,
            "paper": paper,
            "paper_reviews": review_rounds,
            "selected_idea": selected_idea,
            "selected_benchmark": selected_benchmark,
            "artifacts": {
                "ideas": str(ideas_path),
                "literature": str(literature_path),
                "benchmarks": str(benchmarks_path),
                "plan": str(plan_path),
                "summary": str(summary_path),
                "paper_html": str(paper_html_path),
                "pdf": str(pdf_path) if pdf_path.exists() else None,
            },
        }
    except Exception as exc:
        session.rollback()
        run = session.get(Run, run_id)
        if run is not None:
            run.status = "failed"
            run.error_text = str(exc)
            session.commit()
            emit(session, run, kind="run.failed", stage=run.current_stage or "failed", title="Run failed", message=str(exc), payload={"error": str(exc)}, progress=run.progress)
        raise
    finally:
        session.close()
