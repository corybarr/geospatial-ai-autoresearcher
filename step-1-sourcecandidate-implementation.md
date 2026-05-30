# Step 1 — `SourceCandidate` Implementation

## Goal
Implement the search/fetch stage so every discovered source is normalized into a `SourceCandidate` before deeper extraction.

## Purpose
This step creates a stable retrieval contract for the autoresearch loop. It separates raw discovery from later evidence extraction so provenance, snippets, and fetched text are preserved early.

## Inputs
- user research brief
- derived search queries
- upstream retrieval tools from `third_party/agentic-ai-public/` / `src/retrieval/upstream_baseline/`

## Output
A list of `SourceCandidate` objects:

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

## Concrete flow
1. Generate 3-6 search queries from the research brief.
2. Run Tavily web search for broad discovery.
3. Run targeted arXiv lookup for paper-like results and direct technical queries.
4. Optionally run Wikipedia only for foundational terms, not frontier evidence.
5. Fetch the best candidate content for each result.
6. Normalize every result into `SourceCandidate`.
7. Deduplicate by URL and near-duplicate title.
8. Return a bounded set for extraction.

## Query strategy
For a given brief, generate query families:
- direct domain query
- recent frontier query
- benchmark/dataset query
- implementation/repo query
- CesiumJS-adjacent query when relevant

Example families:
- `3D geospatial AI scene understanding`
- `geospatial world model remote sensing 3D`
- `terrain viewpoint planning 3D scene reasoning`
- `geospatial AI benchmark dataset reconstruction`
- `CesiumJS geospatial AI 3D tiles overlay reasoning`

## Tool use policy
- Tavily is the main broad discovery tool.
- arXiv is the main paper enrichment tool.
- Wikipedia is background-only and should rarely survive into the final candidate set.

## Normalization rules
- `id`: deterministic hash of query + URL
- `source_type`: inferred from domain/content pattern
- `publisher`: domain or venue name
- `authors`: parsed when available, otherwise empty list
- `published_at`: normalize when available, else `null`
- `search_snippet`: preserve raw retrieval snippet
- `retrieved_text`: bounded cleaned text for downstream extraction
- `confidence`: retrieval confidence, not scientific truth confidence

## Deduplication rules
Deduplicate in this order:
1. exact URL match
2. canonicalized URL match
3. exact title match
4. near-duplicate title match with same publisher or author overlap

Prefer keeping the candidate with:
- richer snippet
- cleaner fetched text
- better metadata completeness

## Success criteria
Step 1 is successful when the system can take a research brief and reliably produce a clean set of `SourceCandidate` items with:
- traceable provenance
- usable fetched text
- limited duplicates
- broad enough coverage for extraction

## Immediate implementation slice
Build this first:
- query generator
- Tavily adapter
- arXiv adapter
- fetch/clean helper
- `SourceCandidate` normalizer
- dedupe pass

Do not build yet:
- second-pass gap logic
- planner scoring
- UI integration beyond inspection/debug output
