"""
Pydantic schemas mirroring json-structure.md.
Single source of truth for the autoresearch pipeline contracts.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

SourceType = Literal["paper", "repo", "blog", "model", "dataset", "demo", "news", "docs"]
RetrievalMethod = Literal["tavily", "arxiv", "wikipedia", "manual", "other"]
Modality = Literal["text", "image", "video", "3d", "remote_sensing", "multimodal", "other"]
SpatialScope = Literal["site", "city", "regional", "global", "indoor", "unknown"]
CesiumSurface = Literal[
    "terrain", "3d_tiles", "imagery", "overlay", "camera_path", "time_dynamic", "none"
]


class SourceCandidate(BaseModel):
    id: str
    query: str
    title: str
    url: str
    source_type: SourceType
    publisher: str = ""
    authors: List[str] = Field(default_factory=list)
    published_at: Optional[str] = None
    search_snippet: str = ""
    retrieved_text: str = ""
    retrieval_method: RetrievalMethod
    retrieval_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    confidence: float = 0.7


class ResearchRecord(BaseModel):
    id: str
    source_candidate_id: str
    title: str
    url: str
    source_type: SourceType
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


class ExperimentCandidate(BaseModel):
    id: str
    title: str
    hypothesis: str
    problem_statement: str
    based_on_records: List[str] = Field(default_factory=list)
    required_inputs: List[str] = Field(default_factory=list)
    method_outline: List[str] = Field(default_factory=list)
    expected_output: str
    cesiumjs_surface: CesiumSurface = "none"
    demo_shape: str = ""
    build_time_estimate: str = ""
    risks: List[str] = Field(default_factory=list)
    why_now: str = ""


class ExperimentScore(BaseModel):
    candidate_id: str
    geospatial_relevance: float = 0.0
    usefulness: float = 0.0
    feasibility: float = 0.0
    evidence_quality: float = 0.0
    demoability: float = 0.0
    cesiumjs_leverage: float = 0.0
    frontier_signal: float = 0.0
    total_score: float = 0.0
    why_it_ranked: str = ""


class PlannerOutput(BaseModel):
    candidates: List[ExperimentCandidate]
    scores: List[ExperimentScore]


class PipelineBundle(BaseModel):
    brief: str
    run_id: str
    sources: List[SourceCandidate]
    records: List[ResearchRecord]
    plan: PlannerOutput
