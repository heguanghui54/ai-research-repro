from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
import json
import re
from typing import Any, Iterable

import httpx

try:
    from datasets import load_dataset
except Exception as exc:  # pragma: no cover - handled at runtime
    load_dataset = None  # type: ignore[assignment]
    _DATASETS_IMPORT_ERROR = exc
else:
    _DATASETS_IMPORT_ERROR = None


_WORD_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def _tokenize(text: str) -> set[str]:
    return {match.group(0).lower() for match in _WORD_RE.finditer(text or "")}


def _jaccard(left: str, right: str) -> float:
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / max(1, len(left_tokens | right_tokens))


def _normalize_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return f"<bytes len={len(value)}>"
    if isinstance(value, dict):
        return {str(key): _normalize_value(subvalue) for key, subvalue in value.items()}
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if hasattr(value, "shape"):
        shape = getattr(value, "shape", None)
        dtype = getattr(value, "dtype", None)
        return f"<array shape={shape} dtype={dtype}>"
    module = type(value).__module__
    if module.startswith("PIL"):
        size = getattr(value, "size", None)
        mode = getattr(value, "mode", None)
        return f"<image mode={mode} size={size}>"
    return str(value)


def _sample_to_text(sample: dict[str, Any], text_fields: Iterable[str] | None = None) -> str:
    fields = tuple(text_fields or ())
    if fields:
        pieces: list[str] = []
        for field in fields:
            value = sample.get(field)
            if isinstance(value, str) and value.strip():
                pieces.append(value.strip())
            elif isinstance(value, list):
                joined = " ".join(str(item).strip() for item in value if str(item).strip())
                if joined:
                    pieces.append(joined)
        if pieces:
            return "\n".join(pieces)
    normalized = _normalize_value(sample)
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True)


def search_semantic_scholar(query: str, limit: int = 5) -> list[dict[str, Any]]:
    if not query:
        return []
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    with httpx.Client(timeout=20) as client:
        response = client.get(
            url,
            params={
                "query": query,
                "limit": limit,
                "fields": "title,year,venue,url,abstract,citationCount,authors",
            },
        )
        response.raise_for_status()
        data = response.json().get("data", [])
    results: list[dict[str, Any]] = []
    for item in data:
        results.append(
            {
                "title": item.get("title"),
                "year": item.get("year"),
                "venue": item.get("venue"),
                "url": item.get("url"),
                "cited_by_count": item.get("citationCount"),
                "abstract": item.get("abstract"),
            }
        )
    return results


def search_openalex(query: str, limit: int = 5) -> list[dict[str, Any]]:
    if not query:
        return []
    url = "https://api.openalex.org/works"
    with httpx.Client(timeout=20) as client:
        response = client.get(url, params={"search": query, "per-page": limit})
        response.raise_for_status()
        data = response.json().get("results", [])
    results: list[dict[str, Any]] = []
    for item in data:
        abstract = None
        idx = item.get("abstract_inverted_index")
        if isinstance(idx, dict):
            words: dict[int, str] = {}
            for word, positions in idx.items():
                for pos in positions:
                    words[pos] = word
            abstract = " ".join(words[i] for i in sorted(words))
        results.append(
            {
                "title": item.get("title"),
                "year": item.get("publication_year"),
                "venue": (item.get("primary_location") or {}).get("source", {}).get("display_name"),
                "url": item.get("id"),
                "cited_by_count": item.get("cited_by_count"),
                "abstract": abstract,
            }
        )
    return results


def search_academic_sources(query: str, limit: int = 5) -> list[dict[str, Any]]:
    for fn in (search_semantic_scholar, search_openalex):
        try:
            results = fn(query, limit=limit)
            if results:
                return results
        except Exception:
            continue
    return []


def semantic_scholar_dedupe(query: str, limit: int = 8) -> dict[str, Any]:
    try:
        hits = search_semantic_scholar(query, limit=limit)
    except Exception:
        hits = []
    ranked: list[dict[str, Any]] = []
    duplicate_score = 0.0
    duplicate_count = 0
    for item in hits:
        title = str(item.get("title") or "")
        abstract = str(item.get("abstract") or "")
        venue = str(item.get("venue") or "")
        score = max(_jaccard(query, title), _jaccard(query, abstract), _jaccard(query, venue))
        duplicate_score = max(duplicate_score, score)
        if score >= 0.25:
            duplicate_count += 1
        ranked.append({**item, "dedupe_score": round(score, 4)})
    return {
        "query": query,
        "hits": ranked,
        "duplicate_score": round(duplicate_score, 4),
        "duplicate_count": duplicate_count,
    }


@dataclass(frozen=True)
class HFBenchmarkSpec:
    name: str
    dataset_id: str
    split: str
    metric: str
    task_type: str
    description: str
    keywords: tuple[str, ...]
    label_field: str = "label"
    config_name: str | None = None
    text_fields: tuple[str, ...] = ()
    streaming: bool = True
    trust_remote_code: bool = True
    sample_limit: int = 256

    @property
    def loader_snippet(self) -> str:
        parts = [repr(self.dataset_id)]
        if self.config_name:
            parts.append(repr(self.config_name))
        kwargs = [f"split={self.split!r}"]
        if self.streaming:
            kwargs.append("streaming=True")
        if self.trust_remote_code:
            kwargs.append("trust_remote_code=True")
        return f"load_dataset({', '.join(parts + kwargs)})"

    def load_split(self, split: str | None = None, *, streaming: bool | None = None):
        if load_dataset is None:
            raise RuntimeError(
                "The datasets package is not available. Install `datasets` to use HF benchmark adapters."
            ) from _DATASETS_IMPORT_ERROR
        split_name = split or self.split
        use_streaming = self.streaming if streaming is None else streaming
        kwargs: dict[str, Any] = {"split": split_name, "streaming": use_streaming}
        if self.trust_remote_code:
            kwargs["trust_remote_code"] = True
        if self.config_name:
            return load_dataset(self.dataset_id, self.config_name, **kwargs)
        return load_dataset(self.dataset_id, **kwargs)

    def preview(self, limit: int = 5, *, split: str | None = None) -> list[dict[str, Any]]:
        dataset = self.load_split(split=split, streaming=True)
        return [_normalize_value(sample) for sample in islice(dataset, limit)]

    def build_corpus(self, limit: int | None = None, *, split: str | None = None) -> str:
        dataset = self.load_split(split=split, streaming=True)
        sample_limit = limit or self.sample_limit
        lines: list[str] = []
        for sample in islice(dataset, sample_limit):
            if not isinstance(sample, dict):
                lines.append(str(sample))
                continue
            lines.append(_sample_to_text(sample, self.text_fields))
        return "\n".join(line for line in lines if line)

    def as_candidate(self, *, topic: str, literature: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        query = f"{topic} {self.name} {self.dataset_id}"
        verification = search_academic_sources(query, limit=3)
        dedupe = semantic_scholar_dedupe(query, limit=5)
        keyword_hits = sum(1 for keyword in self.keywords if keyword in topic.lower())
        confidence = 0.3 + 0.08 * len(verification) + 0.05 * keyword_hits - 0.04 * dedupe["duplicate_count"]
        confidence = max(0.05, min(0.98, confidence))
        try:
            preview = self.preview(limit=3)
        except Exception as exc:
            preview = [{"error": f"preview unavailable: {type(exc).__name__}", "dataset_id": self.dataset_id}]
        return {
            "name": self.name,
            "metric": self.metric,
            "why_fit": self.description,
            "query": query,
            "status": "candidate",
            "backend": "huggingface",
            "dataset_id": self.dataset_id,
            "config_name": self.config_name,
            "split": self.split,
            "streaming": self.streaming,
            "trust_remote_code": self.trust_remote_code,
            "label_field": self.label_field,
            "text_fields": list(self.text_fields),
            "loader_snippet": self.loader_snippet,
            "sample_limit": self.sample_limit,
            "sample_preview": preview,
            "verification": verification,
            "semantic_scholar_dedupe": dedupe,
            "confidence": confidence,
        }


HF_BENCHMARK_CATALOG: tuple[HFBenchmarkSpec, ...] = (
    HFBenchmarkSpec(
        name="MNIST robustness",
        dataset_id="ylecun/mnist",
        split="train",
        metric="accuracy",
        task_type="vision_classification",
        description="A compact digit benchmark for fast robustness and architecture ablations.",
        keywords=("mnist", "digit", "vision", "robustness", "classification"),
        label_field="label",
        text_fields=(),
        sample_limit=256,
    ),
    HFBenchmarkSpec(
        name="Fashion-MNIST robustness",
        dataset_id="zalando-datasets/fashion_mnist",
        split="train",
        metric="accuracy",
        task_type="vision_classification",
        description="A clothing-image benchmark that keeps the run compact while still being non-trivial.",
        keywords=("fashion", "mnist", "vision", "image", "classification"),
        label_field="label",
        text_fields=(),
        sample_limit=256,
    ),
    HFBenchmarkSpec(
        name="KMNIST robustness",
        dataset_id="tanganke/kmnist",
        split="train",
        metric="accuracy",
        task_type="vision_classification",
        description="A Japanese character benchmark that is close to MNIST but exposes a different label manifold.",
        keywords=("kmnist", "kanji", "vision", "digit", "classification"),
        label_field="label",
        text_fields=(),
        sample_limit=256,
    ),
    HFBenchmarkSpec(
        name="CIFAR-10 compact benchmark",
        dataset_id="uoft-cs/cifar10",
        split="train",
        metric="accuracy",
        task_type="vision_classification",
        description="A familiar small-image benchmark with stronger variation than grayscale digit data.",
        keywords=("cifar", "image", "vision", "classification", "robustness"),
        label_field="label",
        text_fields=(),
        sample_limit=256,
    ),
    HFBenchmarkSpec(
        name="IMDB sentiment benchmark",
        dataset_id="stanfordnlp/imdb",
        split="train",
        metric="accuracy",
        task_type="text_classification",
        description="A streaming-friendly sentiment benchmark that produces an immediately usable text corpus.",
        keywords=("imdb", "sentiment", "text", "language", "review"),
        label_field="label",
        text_fields=("text",),
        sample_limit=512,
    ),
    HFBenchmarkSpec(
        name="Emotion classification benchmark",
        dataset_id="dair-ai/emotion",
        split="train",
        metric="accuracy",
        task_type="text_classification",
        description="A compact emotion benchmark with a clean text field that is ideal for streaming runs.",
        keywords=("emotion", "sentiment", "text", "language"),
        label_field="label",
        text_fields=("text",),
        sample_limit=512,
    ),
    HFBenchmarkSpec(
        name="Amazon polarity benchmark",
        dataset_id="fancyzhx/amazon_polarity",
        split="train",
        metric="accuracy",
        task_type="text_classification",
        description="A large-scale review benchmark that benefits from streaming because the raw dataset is huge.",
        keywords=("amazon", "polarity", "sentiment", "review", "text"),
        label_field="label",
        text_fields=("title", "content"),
        sample_limit=512,
    ),
)


def _topic_score(spec: HFBenchmarkSpec, topic: str) -> int:
    topic_l = topic.lower()
    return sum(1 for keyword in spec.keywords if keyword in topic_l)


def recommend_hf_benchmarks(
    *,
    topic: str,
    ideas: list[dict[str, Any]] | None = None,
    literature: list[dict[str, Any]] | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    scored = sorted(
        HF_BENCHMARK_CATALOG,
        key=lambda spec: (
            _topic_score(spec, topic),
            -spec.sample_limit,
            spec.name,
        ),
        reverse=True,
    )
    candidates: list[dict[str, Any]] = []
    for spec in scored[:limit]:
        candidate = spec.as_candidate(topic=topic, literature=literature)
        candidate["topic_score"] = _topic_score(spec, topic)
        if ideas:
            candidate["idea_overlap"] = sum(
                1
                for idea in ideas
                if spec.name.lower() in json.dumps(idea, ensure_ascii=False).lower()
                or any(keyword in json.dumps(idea, ensure_ascii=False).lower() for keyword in spec.keywords)
            )
        candidates.append(candidate)
    return candidates


def spec_from_candidate(candidate: dict[str, Any]) -> HFBenchmarkSpec:
    return HFBenchmarkSpec(
        name=str(candidate.get("name") or "HF benchmark"),
        dataset_id=str(candidate.get("dataset_id") or ""),
        split=str(candidate.get("split") or "train"),
        metric=str(candidate.get("metric") or "accuracy"),
        task_type=str(candidate.get("task_type") or "text_classification"),
        description=str(candidate.get("why_fit") or candidate.get("description") or ""),
        keywords=tuple(candidate.get("keywords") or ()),
        label_field=str(candidate.get("label_field") or "label"),
        config_name=candidate.get("config_name") or None,
        text_fields=tuple(candidate.get("text_fields") or ()),
        streaming=bool(candidate.get("streaming", True)),
        trust_remote_code=bool(candidate.get("trust_remote_code", True)),
        sample_limit=int(candidate.get("sample_limit") or 256),
    )
