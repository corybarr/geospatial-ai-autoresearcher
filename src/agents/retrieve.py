"""
Step 1: Retrieval.

Anthropic workflow pattern: deterministic tool calls, no LLM in this step.
Wraps the upstream Tavily/arXiv tools from third_party/agentic-ai-public
and normalizes to SourceCandidate[].

Raindrop: each external retrieval (Tavily, arXiv) is a `tool_span`; the
top-level dedupe is a `task_span`.
"""
from __future__ import annotations

import hashlib
import sys
from typing import List

import raindrop.analytics as raindrop

from .schemas import SourceCandidate


def _sid(prefix: str, url: str) -> str:
    return f"{prefix}_{hashlib.sha1(url.encode()).hexdigest()[:10]}"


def _retrieve_tavily(query: str, n: int) -> List[SourceCandidate]:
    from src.retrieval.upstream_baseline import research_tools as _rt

    with raindrop.tool_span("tavily_search") as span:
        span.record_input({"query": query, "max_results": n})
        results = _rt.tavily_search_tool(query=query, max_results=n) or []
        out: List[SourceCandidate] = []
        for r in results:
            url = r.get("url") or ""
            if not url:
                continue
            out.append(
                SourceCandidate(
                    id=_sid("tav", url),
                    query=query,
                    title=r.get("title") or url,
                    url=url,
                    source_type="blog",
                    publisher=r.get("source") or "",
                    search_snippet=(r.get("content") or "")[:500],
                    retrieved_text=(r.get("content") or "")[:8000],
                    retrieval_method="tavily",
                )
            )
        span.set_properties({"raw_count": len(results), "normalized_count": len(out)})
        span.record_output({"titles": [c.title for c in out]})
        return out


def _retrieve_arxiv(query: str, n: int) -> List[SourceCandidate]:
    from src.retrieval.upstream_baseline import research_tools as _rt

    with raindrop.tool_span("arxiv_search") as span:
        span.record_input({"query": query, "max_results": n})
        results = _rt.arxiv_search_tool(query=query, max_results=n) or []
        out: List[SourceCandidate] = []
        for r in results:
            if "error" in r:
                continue
            url = r.get("link") or r.get("pdf_url") or r.get("url") or ""
            if not url:
                continue
            full_text = r.get("summary") or r.get("full_text") or ""
            out.append(
                SourceCandidate(
                    id=_sid("arx", url),
                    query=query,
                    title=r.get("title") or url,
                    url=url,
                    source_type="paper",
                    publisher="arXiv",
                    authors=r.get("authors") or [],
                    published_at=(r.get("published") or "")[:10] or None,
                    search_snippet=(full_text or "")[:500],
                    retrieved_text=full_text[:12000],
                    retrieval_method="arxiv",
                )
            )
        span.set_properties({"raw_count": len(results), "normalized_count": len(out)})
        span.record_output({"titles": [c.title for c in out]})
        return out


def _dedupe(cands: List[SourceCandidate]) -> List[SourceCandidate]:
    seen: set[str] = set()
    out: List[SourceCandidate] = []
    for c in cands:
        key = c.url.split("#")[0].rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def retrieve_sources(
    brief: str, n_tavily: int = 3, n_arxiv: int = 3
) -> List[SourceCandidate]:
    """MVP: one query = the brief itself. Tavily + arXiv only. URL dedupe."""
    with raindrop.task_span("retrieve_sources") as task:
        task.record_input({"brief": brief, "n_tavily": n_tavily, "n_arxiv": n_arxiv})
        cands: List[SourceCandidate] = []
        try:
            cands.extend(_retrieve_tavily(brief, n_tavily))
        except Exception as e:
            print(f"[retrieve] tavily failed: {e}", file=sys.stderr)
        try:
            cands.extend(_retrieve_arxiv(brief, n_arxiv))
        except Exception as e:
            print(f"[retrieve] arxiv failed: {e}", file=sys.stderr)
        deduped = _dedupe(cands)
        task.set_properties({"before_dedupe": len(cands), "after_dedupe": len(deduped)})
        task.record_output({"count": len(deduped)})
        return deduped
