"""
Step 2: ResearchRecord extraction.

Anthropic workflow pattern: **parallelization** — one LLM call per SourceCandidate.
Uses OpenAI's Pydantic-native structured outputs (`beta.chat.completions.parse`)
to guarantee schema-valid JSON without manual parsing.
"""
from __future__ import annotations

import os
from typing import List, Optional

import raindrop.analytics as raindrop
from openai import OpenAI
from pydantic import BaseModel, Field

from .schemas import Modality, ResearchRecord, SourceCandidate, SpatialScope

EXTRACT_MODEL = os.getenv("EXTRACT_MODEL", "gpt-4o-mini")

SYSTEM = """You are a research analyst extracting structured evidence from one source at a time \
for a 3D geospatial AI autoresearcher. Be concrete, cite from the source text, and never invent \
datasets, benchmarks, or numbers that are not stated. Prefer short crisp claims."""

USER_TEMPLATE = """Brief (project focus): {brief}

Source title: {title}
Source URL: {url}
Source type: {source_type}

SOURCE TEXT (may be truncated):
\"\"\"
{text}
\"\"\"

Extract a ResearchRecord. Score `geospatial_relevance` 0.0-1.0 for how much this source actually \
informs 3D geospatial / world-model / scene-understanding work (not generic AI). Pull 2-4 verbatim \
`citation_snippets` from the source text. If a field is unknown, use an empty list or \"unknown\"."""


class ExtractPayload(BaseModel):
    """Schema OpenAI returns; we then merge with source metadata into a ResearchRecord."""
    summary: str
    key_claims: List[str] = Field(default_factory=list)
    datasets: List[str] = Field(default_factory=list)
    benchmarks: List[str] = Field(default_factory=list)
    modalities: List[Modality] = Field(default_factory=list)
    spatial_scope: SpatialScope = "unknown"
    geospatial_relevance: float = 0.0
    implementation_clues: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    citation_snippets: List[str] = Field(default_factory=list)
    novelty_notes: List[str] = Field(default_factory=list)
    confidence: float = 0.7


def extract_record(
    source: SourceCandidate, brief: str, client: Optional[OpenAI] = None
) -> ResearchRecord:
    client = client or OpenAI()
    with raindrop.task_span("extract_record") as span:
        span.record_input({
            "source_id": source.id,
            "source_title": source.title,
            "source_url": source.url,
            "source_type": source.source_type,
            "text_chars": len(source.retrieved_text or source.search_snippet),
        })
        span.set_properties({"model": EXTRACT_MODEL})
        completion = client.beta.chat.completions.parse(
            model=EXTRACT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {
                    "role": "user",
                    "content": USER_TEMPLATE.format(
                        brief=brief,
                        title=source.title,
                        url=source.url,
                        source_type=source.source_type,
                        text=(source.retrieved_text or source.search_snippet)[:10000],
                    ),
                },
            ],
            response_format=ExtractPayload,
        )
        payload = completion.choices[0].message.parsed or ExtractPayload(summary="")
        span.record_output({
            "summary": payload.summary,
            "geospatial_relevance": payload.geospatial_relevance,
            "n_claims": len(payload.key_claims),
            "n_citations": len(payload.citation_snippets),
        })

    return ResearchRecord(
        id=f"rec_{source.id}",
        source_candidate_id=source.id,
        title=source.title,
        url=source.url,
        source_type=source.source_type,
        summary=payload.summary,
        key_claims=payload.key_claims,
        datasets=payload.datasets,
        benchmarks=payload.benchmarks,
        modalities=payload.modalities,
        spatial_scope=payload.spatial_scope,
        geospatial_relevance=payload.geospatial_relevance,
        implementation_clues=payload.implementation_clues,
        limitations=payload.limitations,
        citation_snippets=payload.citation_snippets,
        novelty_notes=payload.novelty_notes,
        confidence=payload.confidence,
    )
