# Geospatial AI Autoresearcher — JSON Structure Draft

This draft locks the core structured data types for the autoresearch loop before more implementation work. Each type exists to turn messy retrieval and synthesis into stable machine-readable records that can be ranked, displayed, and revised without brittle text parsing.

## 1) `SourceCandidate`

**Why this structure is needed:**
This is the first normalized shape after search/fetch, so the system can keep raw source discovery separate from deeper extraction and avoid losing provenance too early.

```json
{
  "id": "string",
  "query": "string",
  "title": "string",
  "url": "string",
  "source_type": "paper|repo|blog|model|dataset|demo|news|docs",
  "publisher": "string",
  "authors": ["string"],
  "published_at": "YYYY-MM-DD|null",
  "search_snippet": "string",
  "retrieved_text": "string",
  "retrieval_method": "tavily|arxiv|wikipedia|manual|other",
  "retrieval_timestamp": "ISO-8601 string",
  "confidence": 0.0
}
```

## 2) `ResearchRecord`

**Why this structure is needed:**
This is the main evidence object for the system, converting messy source text into a consistent research record that can support citation-backed synthesis instead of freeform summaries.

```json
{
  "id": "string",
  "source_candidate_id": "string",
  "title": "string",
  "url": "string",
  "source_type": "paper|repo|blog|model|dataset|demo|news|docs",
  "summary": "string",
  "key_claims": ["string"],
  "datasets": ["string"],
  "benchmarks": ["string"],
  "modalities": ["text|image|video|3d|remote_sensing|multimodal|other"],
  "spatial_scope": "site|city|regional|global|indoor|unknown",
  "geospatial_relevance": 0.0,
  "implementation_clues": ["string"],
  "limitations": ["string"],
  "citation_snippets": ["string"],
  "novelty_notes": ["string"],
  "confidence": 0.0
}
```

## 3) `ExperimentCandidate`

**Why this structure is needed:**
This type converts evidence into buildable proposed experiments, so the planner outputs concrete next actions rather than themes, trends, or generic recommendations.

```json
{
  "id": "string",
  "title": "string",
  "hypothesis": "string",
  "problem_statement": "string",
  "based_on_records": ["string"],
  "required_inputs": ["string"],
  "method_outline": ["string"],
  "expected_output": "string",
  "cesiumjs_surface": "terrain|3d_tiles|imagery|overlay|camera_path|time_dynamic|none",
  "demo_shape": "string",
  "build_time_estimate": "hours|days|weeks string",
  "risks": ["string"],
  "why_now": "string"
}
```

## 4) `ExperimentScore`

**Why this structure is needed:**
This is the ranking contract that makes prioritization explicit, reviewable, and comparable across experiments instead of hiding judgment in prose.

```json
{
  "candidate_id": "string",
  "geospatial_relevance": 0.0,
  "usefulness": 0.0,
  "feasibility": 0.0,
  "evidence_quality": 0.0,
  "demoability": 0.0,
  "cesiumjs_leverage": 0.0,
  "frontier_signal": 0.0,
  "total_score": 0.0,
  "why_it_ranked": "string"
}
```

## 5) `ResearchGap`

**Why this structure is needed:**
This gives the autoresearch loop a clean way to represent missing coverage, conflicts, or weak evidence so the second pass can be intentional instead of vague.

```json
{
  "id": "string",
  "gap_type": "missing_source|weak_evidence|conflict|outdated|coverage_gap",
  "description": "string",
  "related_record_ids": ["string"],
  "recommended_followup_queries": ["string"],
  "priority": 0.0
}
```

## Suggested implementation order
1. `SourceCandidate`
2. `ResearchRecord`
3. `ExperimentCandidate`
4. `ExperimentScore`
5. `ResearchGap`

## Current recommendation
Start implementation with `SourceCandidate` and `ResearchRecord` only. That gives us a clean retrieval-to-extraction contract before we wire experiment generation and ranking.
