#!/usr/bin/env python3
"""Citation-backed retrospective frontier-alignment probe.

This probe upgrades the manual frontier descriptors used in the smoke test by
querying Semantic Scholar for each historical OpenReview sample and extracting
terms from later citing papers. It is still a lightweight pilot, not a full
literature review, but the frontier descriptors are grounded in retrieved
post-paper academic metadata rather than hand-written keywords.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any
from urllib import parse, request
from urllib.error import HTTPError, URLError


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
SOURCE_DIR = DOC_DIR / "experiments" / "openreview_guided_regeneration_probe_20260602_073500"
CONTROL_DIR = DOC_DIR / "experiments" / "openreview_equal_context_ablation_20260602_142000"
CACHE_DIR = DOC_DIR / "experiments" / ".cache" / "semantic_scholar"

STOPWORDS = {
    "about",
    "across",
    "against",
    "algorithm",
    "algorithms",
    "approach",
    "based",
    "between",
    "datasets",
    "deep",
    "demonstrate",
    "different",
    "efficient",
    "empirical",
    "evaluate",
    "evaluation",
    "experiments",
    "framework",
    "generative",
    "improve",
    "improved",
    "improves",
    "language",
    "large",
    "learn",
    "learning",
    "method",
    "methods",
    "model",
    "models",
    "neural",
    "paper",
    "performance",
    "propose",
    "proposed",
    "provide",
    "results",
    "show",
    "shows",
    "study",
    "system",
    "systems",
    "task",
    "tasks",
    "their",
    "they",
    "these",
    "this",
    "through",
    "training",
    "using",
    "with",
    "without",
    "zhang",
}

ACTIONABILITY_TERMS = [
    "benchmark",
    "baseline",
    "ablation",
    "metric",
    "evaluation",
    "robustness",
    "dataset",
    "safety",
    "privacy",
    "calibration",
    "uncertainty",
    "mechanism",
    "causal",
    "scaling",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _cache_path(url: str) -> Path:
    import hashlib

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def _api_get(url: str, *, sleep_seconds: float = 1.5, max_attempts: int = 2) -> dict[str, Any]:
    cache_path = _cache_path(url)
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    last_error = None
    for attempt in range(max_attempts):
        try:
            req = request.Request(url, headers={"User-Agent": "codex-research-probe/1.0"})
            with request.urlopen(req, timeout=60) as resp:  # noqa: S310 - public academic metadata API.
                data = json.loads(resp.read().decode("utf-8"))
            cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            time.sleep(sleep_seconds)
            return data
        except HTTPError as exc:
            last_error = repr(exc)
            if exc.code == 429:
                time.sleep(sleep_seconds * (attempt + 5))
            else:
                time.sleep(sleep_seconds * (attempt + 2))
        except (URLError, TimeoutError) as exc:
            last_error = repr(exc)
            time.sleep(sleep_seconds * (attempt + 2))
    raise RuntimeError(f"Semantic Scholar request failed: {last_error}")


def _search_paper(paper: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    fields = "paperId,title,year,abstract,citationCount,influentialCitationCount,externalIds"
    arxiv_id = (paper.get("arxiv_id") or "").strip()
    if arxiv_id:
        url = f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{parse.quote(arxiv_id)}?fields={fields}"
        try:
            return _api_get(url), None
        except RuntimeError as exc:
            arxiv_error = str(exc)
        else:
            arxiv_error = None
    else:
        arxiv_error = None
    query = parse.quote(paper["title"])
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=1&fields={fields}"
    try:
        data = _api_get(url)
    except RuntimeError as exc:
        return None, arxiv_error or str(exc)
    items = data.get("data") or []
    return (items[0] if items else None), arxiv_error


def _citations(paper_id: str, *, limit: int) -> tuple[list[dict[str, Any]], str | None]:
    fields = "citingPaper.paperId,citingPaper.title,citingPaper.year,citingPaper.abstract,citingPaper.citationCount"
    url = (
        f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?"
        f"limit={limit}&fields={fields}"
    )
    try:
        data = _api_get(url)
    except RuntimeError as exc:
        return [], str(exc)
    return [item.get("citingPaper") or {} for item in data.get("data") or []], None


def _openalex_abstract(work: dict[str, Any]) -> str | None:
    inverted = work.get("abstract_inverted_index")
    if not isinstance(inverted, dict):
        return None
    positions: dict[int, str] = {}
    for token, indexes in inverted.items():
        for index in indexes:
            positions[int(index)] = token
    return " ".join(positions[index] for index in sorted(positions))


def _openalex_search(paper: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    query = parse.quote(paper["title"])
    url = f"https://api.openalex.org/works?search={query}&per-page=1"
    try:
        data = _api_get(url)
    except RuntimeError as exc:
        return None, str(exc)
    results = data.get("results") or []
    return (results[0] if results else None), None


def _openalex_citations(work_id: str, *, limit: int) -> tuple[list[dict[str, Any]], str | None]:
    openalex_id = work_id.rsplit("/", 1)[-1]
    url = (
        "https://api.openalex.org/works?"
        f"filter=cites:{parse.quote(openalex_id)}&per-page={limit}&sort=cited_by_count:desc"
    )
    try:
        data = _api_get(url)
    except RuntimeError as exc:
        return [], str(exc)
    rows = []
    for work in data.get("results") or []:
        rows.append(
            {
                "paperId": work.get("id"),
                "title": work.get("title"),
                "year": work.get("publication_year"),
                "abstract": _openalex_abstract(work),
                "citationCount": work.get("cited_by_count"),
            }
        )
    return rows, None


def _artifact_text(artifact: dict[str, Any]) -> str:
    parts = []
    for key in [
        "core_contribution",
        "method_sketch",
        "experiment_plan",
        "limitations",
        "claim_boundary",
        "mini_paper_artifact",
    ]:
        value = artifact.get(key)
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
    for key in ["review_insights_used", "generic_review_pressures_used"]:
        parts.extend(str(item) for item in artifact.get(key) or [])
    return "\n".join(parts).lower()


def _tokens(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z][a-z0-9\-]{3,}", text.lower())
        if token not in STOPWORDS and not token.isdigit()
    ]


def _extract_frontier_terms(citations: list[dict[str, Any]], *, max_terms: int) -> list[str]:
    counter: Counter[str] = Counter()
    for paper in citations:
        text = " ".join(
            str(paper.get(key) or "")
            for key in ["title", "abstract"]
        )
        counter.update(_tokens(text))
    return [term for term, _ in counter.most_common(max_terms)]


def _count_term(text: str, term: str) -> int:
    escaped = re.escape(term.lower())
    return len(re.findall(rf"\b{escaped}\b", text))


def _score(text: str, terms: list[str]) -> dict[str, Any]:
    if not terms:
        return {
            "score": 0.0,
            "frontier_alignment": 0.0,
            "actionability": 0.0,
            "matched_frontier_terms": [],
            "matched_actionability_terms": [],
        }
    hits = {term: _count_term(text, term) for term in terms}
    matched_terms = [term for term, count in hits.items() if count > 0]
    action_terms = [term for term in ACTIONABILITY_TERMS if _count_term(text, term) > 0]
    frontier_alignment = len(matched_terms) / len(terms) if terms else 0.0
    actionability = min(1.0, len(action_terms) / 5)
    total = (0.8 * frontier_alignment) + (0.2 * actionability)
    return {
        "score": round(total, 4),
        "frontier_alignment": round(frontier_alignment, 4),
        "actionability": round(actionability, 4),
        "matched_frontier_terms": matched_terms,
        "matched_actionability_terms": action_terms,
    }


def _winner(scores: dict[str, dict[str, Any]]) -> str:
    if all(score["score"] == 0 for score in scores.values()):
        return "not_scored_no_frontier_terms"
    ordered = sorted(scores.items(), key=lambda item: item[1]["score"], reverse=True)
    if len(ordered) > 1 and ordered[0][1]["score"] == ordered[1][1]["score"]:
        return "tie"
    return ordered[0][0]


def _summarize(per_paper: list[dict[str, Any]]) -> dict[str, Any]:
    winners = Counter(item["winner"] for item in per_paper)
    conditions = ["paper_only", "review_guided", "shuffled_review_control"]
    means = {}
    for condition in conditions:
        values = [item["scores"][condition]["score"] for item in per_paper if item["frontier_terms"]]
        means[condition] = round(mean(values), 4) if values else 0.0
    return {
        "paper_count": len(per_paper),
        "papers_with_retrieved_citations": sum(1 for item in per_paper if item["citation_count_used"] > 0),
        "thin_citation_graph_papers": sum(1 for item in per_paper if 0 < item["citation_count_used"] < 5),
        "winner_counts": dict(winners),
        "mean_scores": means,
        "mean_delta_review_guided_minus_paper_only": round(means["review_guided"] - means["paper_only"], 4),
        "mean_delta_review_guided_minus_shuffled_control": round(
            means["review_guided"] - means["shuffled_review_control"],
            4,
        ),
        "delayed_value_case_count": sum(
            1 for item in per_paper if item["temporal_diagnostic"]["pattern"] == "delayed_value_review_signal"
        ),
        "short_term_positive_long_term_negative_count": sum(
            1 for item in per_paper if item["temporal_diagnostic"]["pattern"] == "short_term_positive_long_term_negative"
        ),
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Citation-Backed Retrospective Frontier Probe",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Status: `{summary['status']}`",
        f"- Citation source: `{summary['citation_source']}`",
        "",
        "## Aggregate",
        "",
    ]
    aggregate = summary["aggregate"]
    lines.append(f"- Papers with retrieved citations: `{aggregate['papers_with_retrieved_citations']}` / `{aggregate['paper_count']}`")
    lines.append(f"- Thin citation-graph papers: `{aggregate['thin_citation_graph_papers']}`")
    lines.append(f"- Winner counts: `{json.dumps(aggregate['winner_counts'], sort_keys=True)}`")
    lines.append(f"- Mean scores: `{json.dumps(aggregate['mean_scores'], sort_keys=True)}`")
    lines.append(f"- Review-guided minus paper-only delta: `{aggregate['mean_delta_review_guided_minus_paper_only']}`")
    lines.append(f"- Review-guided minus shuffled-control delta: `{aggregate['mean_delta_review_guided_minus_shuffled_control']}`")
    lines.append(f"- Delayed-value cases: `{aggregate['delayed_value_case_count']}`")
    lines.append(
        "- Short-term-positive/long-term-negative cases: "
        f"`{aggregate['short_term_positive_long_term_negative_count']}`"
    )
    lines.extend(["", "## Per Paper", ""])
    for item in summary["per_paper"]:
        score_view = {k: v["score"] for k, v in item["scores"].items()}
        lines.append(
            f"- `{item['paper_id']}`: `{item['title']}`; winner `{item['winner']}`; "
            f"citations used `{item['citation_count_used']}`; scores "
            f"`{json.dumps(score_view, sort_keys=True)}`; temporal pattern "
            f"`{item['temporal_diagnostic']['pattern']}`"
        )
    lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"], ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="retrospective_frontier_citation_probe_20260602_163000")
    parser.add_argument("--citation-limit", type=int, default=40)
    parser.add_argument("--max-terms", type=int, default=16)
    parser.add_argument("--max-papers", type=int, default=None)
    args = parser.parse_args()

    selected_list = _load_json(SOURCE_DIR / "selected_papers.json")
    if args.max_papers is not None:
        selected_list = selected_list[: args.max_papers]
    selected = {item["paper_id"]: item for item in selected_list}
    regenerated = {item["paper_id"]: item for item in _load_json(SOURCE_DIR / "regenerated_artifacts.json")["papers"]}
    controls = {
        item["paper_id"]: item["context_control_regeneration"]
        for item in _load_json(CONTROL_DIR / "context_control_artifacts.json")["papers"]
    }
    local_quality = {
        item["paper_id"]: item
        for item in _load_json(SOURCE_DIR / "summary.json")["scoring"]["per_paper"]
    }

    per_paper = []
    retrieval_records = []
    for source in selected_list:
        paper_id = source["paper_id"]
        found, search_error = _search_paper(source)
        metadata_source = "Semantic Scholar Graph API"
        openalex_match = None
        citation_rows: list[dict[str, Any]] = []
        citation_error = None
        if found and found.get("paperId"):
            citation_rows, citation_error = _citations(found["paperId"], limit=args.citation_limit)
        if not citation_rows:
            openalex_match, openalex_search_error = _openalex_search(source)
            if openalex_match and openalex_match.get("id"):
                citation_rows, openalex_citation_error = _openalex_citations(openalex_match["id"], limit=args.citation_limit)
                metadata_source = "OpenAlex fallback"
                if not citation_error:
                    citation_error = openalex_citation_error
            else:
                if not search_error:
                    search_error = openalex_search_error
        original_year = found.get("year") if found else None
        later_citations = [
            row for row in citation_rows
            if row.get("title") and (not original_year or not row.get("year") or row["year"] >= original_year)
        ]
        terms = _extract_frontier_terms(later_citations, max_terms=args.max_terms)
        condition_artifacts = {
            "paper_only": regenerated[paper_id]["baseline_regeneration"],
            "review_guided": regenerated[paper_id]["review_guided_regeneration"],
            "shuffled_review_control": controls[paper_id],
        }
        scores = {
            condition: _score(_artifact_text(artifact), terms)
            for condition, artifact in condition_artifacts.items()
        }
        local_scores = local_quality.get(paper_id, {}).get("scores", {})
        local_paper_only = local_scores.get("baseline", {}).get("overall")
        local_review_guided = local_scores.get("review_guided", {}).get("overall")
        local_delta = None
        if isinstance(local_paper_only, (int, float)) and isinstance(local_review_guided, (int, float)):
            local_delta = local_review_guided - local_paper_only
        frontier_delta = scores["review_guided"]["score"] - scores["paper_only"]["score"]
        pattern = "not_classified"
        if local_delta is not None:
            if local_delta < 0 and frontier_delta > 0:
                pattern = "delayed_value_review_signal"
            elif local_delta > 0 and frontier_delta < 0:
                pattern = "short_term_positive_long_term_negative"
            elif local_delta > 0 and frontier_delta > 0:
                pattern = "short_and_long_term_positive"
            elif local_delta < 0 and frontier_delta < 0:
                pattern = "short_and_long_term_negative"
            else:
                pattern = "mixed_or_tie"
        per_paper.append(
            {
                "paper_id": paper_id,
                "title": source["title"],
                "semantic_scholar_match": found,
                "openalex_match": openalex_match,
                "metadata_source": metadata_source,
                "search_error": search_error,
                "citation_error": citation_error,
                "citation_count_retrieved": len(citation_rows),
                "citation_count_used": len(later_citations),
                "frontier_terms": terms,
                "scores": scores,
                "winner": _winner(scores),
                "temporal_diagnostic": {
                    "short_term_quality_source": _rel(SOURCE_DIR / "summary.json"),
                    "short_term_review_guided_minus_paper_only": local_delta,
                    "long_term_frontier_review_guided_minus_paper_only": round(frontier_delta, 4),
                    "pattern": pattern,
                },
            }
        )
        retrieval_records.append(
            {
                "paper_id": paper_id,
                "query_title": source["title"],
                "semantic_scholar_match": found,
                "openalex_match": openalex_match,
                "metadata_source": metadata_source,
                "search_error": search_error,
                "citation_error": citation_error,
                "citations": later_citations,
                "frontier_terms": terms,
            }
        )

    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "citation_backed_retrospective_frontier_probe",
        "citation_source": "Semantic Scholar Graph API with OpenAlex fallback",
        "citation_limit": args.citation_limit,
        "max_terms": args.max_terms,
        "source_regeneration_summary": _rel(SOURCE_DIR / "summary.json"),
        "control_source_summary": _rel(CONTROL_DIR / "summary.json"),
        "conditions": ["paper_only", "review_guided", "shuffled_review_control"],
        "per_paper": per_paper,
        "aggregate": _summarize(per_paper),
        "claim_boundary": (
            "This is a lightweight citation-backed pilot using retrieved Semantic Scholar "
            "metadata and simple term-overlap scoring. It is stronger than manual descriptors "
            "but still not a full citation graph reconstruction, blinded expert review, or "
            "proof of long-term SOTA alignment. Thin or topically broad citation graphs can "
            "produce misleading frontier terms and require relevance filtering."
        ),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(_markdown(summary), encoding="utf-8")
    (out_dir / "retrieval_records.json").write_text(
        json.dumps(retrieval_records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"summary": _rel(out_dir / "summary.json"), "readme": _rel(out_dir / "README.md")}, indent=2))


if __name__ == "__main__":
    main()
