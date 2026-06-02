#!/usr/bin/env python3
"""Validate delayed-value review candidates against later citation frontiers.

This probe tests whether the candidate-mining screen is merely a heuristic
labeler or whether its top candidates are more aligned with later citation
metadata than control comments. It uses OpenAlex public metadata, retrieves
works that cite the reviewed paper, extracts lightweight frontier terms from
later citing-paper titles/abstracts, and scores review excerpts against those
terms.

The result is still a lexical proxy, not proof of long-horizon scientific
value. Its purpose is to decide whether the candidate queue is a better input
for expensive TFR replay than arbitrary review snippets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any
from urllib import parse, request
from urllib.error import HTTPError, URLError


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
SOURCE_DIR = DOC_DIR / "experiments" / "delayed_value_review_candidate_mining_20260603_001500"
OUT_DIR = DOC_DIR / "experiments" / "delayed_value_candidate_frontier_validation_20260603_011500"
CACHE_DIR = DOC_DIR / "experiments" / ".cache" / "openalex_candidate_frontier"

STOPWORDS = {
    "about", "abstract", "across", "also", "and", "approach", "are", "based",
    "benchmark", "better", "between", "can", "conference", "data", "dataset",
    "deep", "demonstrate", "different", "efficient", "empirical", "evaluate",
    "evaluation", "experiment", "experiments", "for", "from", "graph", "have",
    "how", "important", "improve", "improved", "improves", "including",
    "large", "learn", "learning", "method", "methods", "model", "models",
    "more", "new", "not", "novel", "our", "paper", "performance", "propose",
    "proposed", "provide", "results", "review", "reviewer", "show", "shows",
    "study", "system", "systems", "task", "tasks", "that", "the", "their",
    "these", "this", "through", "title", "using", "with", "work",
}

ACTION_TERMS = {
    "ablation", "baseline", "benchmark", "calibration", "causal", "dataset",
    "evaluation", "fairness", "generalization", "mechanism", "metric",
    "privacy", "robustness", "safety", "scaling", "theory", "uncertainty",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _cache_path(url: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{hashlib.sha256(url.encode('utf-8')).hexdigest()}.json"


def _api_get(url: str, *, sleep_seconds: float = 0.1, attempts: int = 2) -> dict[str, Any]:
    cache_path = _cache_path(url)
    if cache_path.exists():
        return _load_json(cache_path)
    last_error = ""
    for attempt in range(attempts):
        try:
            req = request.Request(url, headers={"User-Agent": "codex-research-probe/1.0"})
            with request.urlopen(req, timeout=12) as resp:  # noqa: S310 - public metadata endpoint.
                data = json.loads(resp.read().decode("utf-8"))
            cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            time.sleep(sleep_seconds)
            return data
        except HTTPError as exc:
            last_error = repr(exc)
            if exc.code == 429:
                time.sleep(1.5 * (attempt + 1))
            else:
                time.sleep(0.5 * (attempt + 1))
        except (URLError, TimeoutError, socket.timeout) as exc:
            last_error = repr(exc)
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(last_error)


def _openalex_abstract(work: dict[str, Any]) -> str:
    inverted = work.get("abstract_inverted_index")
    if not isinstance(inverted, dict):
        return ""
    positions: dict[int, str] = {}
    for token, indexes in inverted.items():
        for index in indexes:
            positions[int(index)] = token
    return " ".join(positions[index] for index in sorted(positions))


def _search_work(title: str) -> tuple[dict[str, Any] | None, str | None]:
    url = f"https://api.openalex.org/works?search={parse.quote(title)}&per-page=1"
    try:
        data = _api_get(url)
    except RuntimeError as exc:
        return None, str(exc)
    results = data.get("results") or []
    return (results[0] if results else None), None


def _citing_works(openalex_id: str, *, limit: int) -> tuple[list[dict[str, Any]], str | None]:
    short_id = openalex_id.rsplit("/", 1)[-1]
    url = (
        "https://api.openalex.org/works?"
        f"filter=cites:{parse.quote(short_id)}&per-page={limit}&sort=cited_by_count:desc"
    )
    try:
        data = _api_get(url)
    except RuntimeError as exc:
        return [], str(exc)
    return data.get("results") or [], None


def _tokens(text: str) -> list[str]:
    tokens = []
    for token in re.findall(r"[a-z][a-z0-9\-]{2,}", text.lower()):
        if token.endswith("s") and len(token) > 4:
            token = token[:-1]
        if token not in STOPWORDS and not token.isdigit():
            tokens.append(token)
    return tokens


def _frontier_terms(citations: list[dict[str, Any]], *, top_k: int) -> list[str]:
    counter: Counter[str] = Counter()
    for work in citations:
        text = " ".join([str(work.get("title") or ""), _openalex_abstract(work)])
        counter.update(_tokens(text))
    return [term for term, _ in counter.most_common(top_k)]


def _score_text(text: str, terms: list[str]) -> dict[str, Any]:
    token_set = set(_tokens(text))
    matched = [term for term in terms if term in token_set]
    matched_actions = sorted(ACTION_TERMS & token_set)
    alignment = len(matched) / len(terms) if terms else 0.0
    actionability = min(1.0, len(matched_actions) / 5)
    score = 0.8 * alignment + 0.2 * actionability
    return {
        "score": round(score, 4),
        "frontier_alignment": round(alignment, 4),
        "actionability": round(actionability, 4),
        "matched_frontier_terms": matched,
        "matched_actionability_terms": matched_actions,
    }


def _title_overlap(query_title: str, matched_title: str) -> float:
    query_tokens = set(_tokens(query_title))
    matched_tokens = set(_tokens(matched_title))
    if not query_tokens or not matched_tokens:
        return 0.0
    return len(query_tokens & matched_tokens) / len(query_tokens | matched_tokens)


def _select(records: list[dict[str, Any]], *, label: str, limit: int, reverse: bool = True) -> list[dict[str, Any]]:
    selected = []
    seen_titles = set()
    pool = [record for record in records if record.get("candidate_label") == label]
    pool.sort(key=lambda item: float(item.get("delayed_candidate_score") or 0), reverse=reverse)
    for record in pool:
        title = str(record.get("title") or "")
        if not title or title in seen_titles:
            continue
        selected.append(record)
        seen_titles.add(title)
        if len(selected) >= limit:
            break
    return selected


def _evaluate(record: dict[str, Any], *, citation_limit: int, frontier_terms: int) -> dict[str, Any]:
    title = str(record.get("title") or "")
    work, search_error = _search_work(title)
    if not work:
        return {
            "review_id": record.get("review_id"),
            "title": title,
            "candidate_label": record.get("candidate_label"),
            "status": "not_scored_no_openalex_match",
            "search_error": search_error,
        }
    overlap = _title_overlap(title, str(work.get("title") or ""))
    if overlap < 0.45:
        return {
            "review_id": record.get("review_id"),
            "paper_index": record.get("paper_index"),
            "title": title,
            "candidate_label": record.get("candidate_label"),
            "status": "not_scored_possible_match_drift",
            "openalex_id": work.get("id"),
            "openalex_title": work.get("title"),
            "openalex_year": work.get("publication_year"),
            "title_token_overlap": round(overlap, 4),
        }
    citations, citation_error = _citing_works(str(work.get("id")), limit=citation_limit)
    terms = _frontier_terms(citations, top_k=frontier_terms)
    if not terms:
        status = "not_scored_no_citation_terms"
    else:
        status = "scored"
    review_score = _score_text(str(record.get("excerpt") or record.get("text") or ""), terms)
    title_score = _score_text(title, terms)
    return {
        "review_id": record.get("review_id"),
        "paper_index": record.get("paper_index"),
        "title": title,
        "candidate_label": record.get("candidate_label"),
        "delayed_candidate_score": record.get("delayed_candidate_score"),
        "decision": record.get("decision"),
        "mean_score": record.get("mean_score"),
        "status": status,
        "openalex_id": work.get("id"),
        "openalex_title": work.get("title"),
        "openalex_year": work.get("publication_year"),
        "openalex_cited_by_count": work.get("cited_by_count"),
        "title_token_overlap": round(overlap, 4),
        "citation_error": citation_error,
        "citation_count_retrieved": len(citations),
        "frontier_terms": terms,
        "review_signal": review_score,
        "title_signal": title_score,
        "review_minus_title_score": round(review_score["score"] - title_score["score"], 4),
        "primary_gates": record.get("primary_gates"),
        "actionable_categories": record.get("actionable_categories"),
        "excerpt": record.get("excerpt"),
    }


def _aggregate(per_item: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [item for item in per_item if item.get("status") == "scored"]
    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in scored:
        by_label[str(item.get("candidate_label"))].append(item)
    label_table = {}
    for label, items in sorted(by_label.items()):
        label_table[label] = {
            "scored_count": len(items),
            "mean_review_signal_score": round(mean(item["review_signal"]["score"] for item in items), 4),
            "mean_frontier_alignment": round(mean(item["review_signal"]["frontier_alignment"] for item in items), 4),
            "mean_review_minus_title_score": round(mean(item["review_minus_title_score"] for item in items), 4),
            "review_beats_title_count": sum(1 for item in items if item["review_minus_title_score"] > 0),
        }
    delayed = by_label.get("delayed_value_replay_candidate", [])
    controls = [item for item in scored if item.get("candidate_label") != "delayed_value_replay_candidate"]
    delayed_mean = mean(item["review_signal"]["score"] for item in delayed) if delayed else 0.0
    control_mean = mean(item["review_signal"]["score"] for item in controls) if controls else 0.0
    return {
        "attempted_count": len(per_item),
        "scored_count": len(scored),
        "not_scored_count": len(per_item) - len(scored),
        "label_table": label_table,
        "delayed_candidate_mean_review_signal_score": round(delayed_mean, 4),
        "control_mean_review_signal_score": round(control_mean, 4),
        "delayed_minus_control_mean_score": round(delayed_mean - control_mean, 4),
        "delayed_review_beats_title_count": sum(1 for item in delayed if item["review_minus_title_score"] > 0),
        "delayed_scored_count": len(delayed),
    }


def _markdown(summary: dict[str, Any]) -> str:
    aggregate = summary["aggregate"]
    lines = [
        "# Delayed-Value Candidate Frontier Validation",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Candidate source: `{summary['candidate_source']}`",
        f"- Attempted reviews: `{aggregate['attempted_count']}`",
        f"- Scored reviews: `{aggregate['scored_count']}`",
        f"- Delayed minus control mean score: `{aggregate['delayed_minus_control_mean_score']}`",
        "",
        "## Label Results",
        "",
        "| Label | Scored | Mean review signal | Mean frontier alignment | Mean review-title delta | Review beats title |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, item in aggregate["label_table"].items():
        lines.append(
            f"| {label} | {item['scored_count']} | {item['mean_review_signal_score']} | "
            f"{item['mean_frontier_alignment']} | {item['mean_review_minus_title_score']} | "
            f"{item['review_beats_title_count']} |"
        )
    lines.extend(["", "## Scored Items", ""])
    for item in summary["per_item"]:
        if item.get("status") != "scored":
            continue
        lines.append(
            f"- `{item['review_id']}` `{item['candidate_label']}` score "
            f"`{item['review_signal']['score']}` title-delta "
            f"`{item['review_minus_title_score']}` citations "
            f"`{item['citation_count_retrieved']}`: {item['title']}"
        )
    lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"], ""])
    return "\n".join(lines)


def _write(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return _rel(path)


def _update_manifest(paths: list[str], summary: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        if path not in artifacts:
            artifacts.append(path)
    manifest["status"] = "pilot_package_with_candidate_frontier_validation"
    manifest["delayed_value_candidate_frontier_validation"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "scored_count": summary["aggregate"]["scored_count"],
        "delayed_minus_control_mean_score": summary["aggregate"]["delayed_minus_control_mean_score"],
        "claim_boundary": "OpenAlex lexical citation-frontier validation, not proof of causal delayed-value insight.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="delayed_value_candidate_frontier_validation_20260603_011500")
    parser.add_argument("--candidate-source", default=str(SOURCE_DIR / "candidate_reviews.json"))
    parser.add_argument("--per-label", type=int, default=8)
    parser.add_argument("--citation-limit", type=int, default=25)
    parser.add_argument("--frontier-terms", type=int, default=25)
    args = parser.parse_args()

    source_path = Path(args.candidate_source)
    if not source_path.is_absolute():
        source_path = ROOT / source_path
    records = _load_json(source_path)
    selected = []
    for label in [
        "delayed_value_replay_candidate",
        "long_horizon_positive_candidate",
        "short_term_repair_signal",
        "generic_or_unrouted",
    ]:
        selected.extend(_select(records, label=label, limit=args.per_label))
    per_item = [
        _evaluate(record, citation_limit=args.citation_limit, frontier_terms=args.frontier_terms)
        for record in selected
    ]
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "candidate_frontier_validation",
        "candidate_source": _rel(source_path),
        "openalex_api": "https://api.openalex.org/",
        "selection": {
            "per_label": args.per_label,
            "citation_limit": args.citation_limit,
            "frontier_terms": args.frontier_terms,
            "labels": [
                "delayed_value_replay_candidate",
                "long_horizon_positive_candidate",
                "short_term_repair_signal",
                "generic_or_unrouted",
            ],
        },
        "aggregate": _aggregate(per_item),
        "per_item": per_item,
        "interpretation": (
            "This probe asks whether delayed-value candidates are more aligned "
            "with citation-derived future-frontier terms than control review "
            "comments. It is useful as a screening validation for replay priority, "
            "but the lexical score can miss semantic direction changes."
        ),
        "claim_boundary": (
            "This is an OpenAlex lexical validation of candidate ranking. It does "
            "not prove that a review caused or would have caused a future frontier "
            "trajectory; positive candidates still require full TFR replay and "
            "semantic or human future-frontier judgement."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = [
        _write(OUT_DIR / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2)),
        _write(OUT_DIR / "per_item.json", json.dumps(per_item, ensure_ascii=False, indent=2)),
        _write(OUT_DIR / "README.md", _markdown(summary)),
    ]
    summary["summary_path"] = paths[0]
    _write(OUT_DIR / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    _update_manifest(paths + ["scripts/run_delayed_value_candidate_frontier_validation.py"], summary)
    print(
        json.dumps(
            {
                "summary": paths[0],
                "scored_count": summary["aggregate"]["scored_count"],
                "delayed_minus_control_mean_score": summary["aggregate"]["delayed_minus_control_mean_score"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
