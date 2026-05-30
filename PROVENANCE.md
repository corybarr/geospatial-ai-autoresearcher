# Provenance

## Upstream source
- Repository: `https://github.com/https-deeplearning-ai/agentic-ai-public`
- Pinned commit: `0ee5559e7d5491188f86dff6df80a8d4597a49b5`

## Imported baseline purpose
We are using this upstream codebase as a traced baseline for retrieval-oriented components of **Geospatial AI Autoresearcher**.

## Imported files in active use baseline
- `src/research_tools.py`
- `src/agents.py`
- `src/planning_agent.py`

## Import structure
- Full upstream repository snapshot preserved under `third_party/agentic-ai-public/`
- Retrieval-oriented baseline copies preserved under `src/retrieval/upstream_baseline/`

## Adaptation policy
- Production code for this project will live outside the vendored baseline.
- All adapted files derived from the upstream baseline will carry attribution headers naming the upstream file path and pinned commit.
- Structural changes for typed outputs, geospatial schemas, and experiment planning will be implemented in this repository’s own source tree rather than directly mutating provenance records.
