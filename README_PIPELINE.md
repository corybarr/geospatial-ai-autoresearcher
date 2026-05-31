# Autoresearcher Backend — MVP

Workflow (Anthropic agent-design pattern):

```
brief ─▶ retrieve (Tavily+arXiv, deterministic)
        ─▶ extract (one LLM call per source, parallel)
        ─▶ plan   (one LLM call, generates+scores top-3)
        ─▶ {sources.json, records.json, experiments.json, bundle.json}
```

This is a **workflow**, not an autonomous agent — steps are fixed, no loop, no
tool-using LLM at top level. Step 2 uses the **parallelization** pattern. Step
3 merges candidate generation and scoring into one structured tool call.

## Files

- `src/agents/schemas.py` — Pydantic models for the 4 contracts
- `src/agents/retrieve.py` — Step 1, wraps upstream Tavily/arXiv tools
- `src/agents/extract.py` — Step 2, per-source ResearchRecord
- `src/agents/plan.py`    — Step 3, ranked ExperimentCandidate + Score
- `src/agents/pipeline.py` — orchestrator (local entrypoint)
- `modal_app.py` — Modal deployment + HTTP endpoints

## Run locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
export TAVILY_API_KEY=...
python -m src.agents.pipeline "frontier 3D geospatial / world models"
# artifacts: data/runs/<timestamp>/{sources,records,experiments,bundle}.json
# and       data/runs/latest -> <timestamp>
```

## Deploy on Modal

```bash
modal secret create autoresearch-secrets \
    ANTHROPIC_API_KEY=sk-ant-... \
    TAVILY_API_KEY=tvly-...

modal deploy modal_app.py
```

Endpoints:
- `GET /research?brief=...` — run pipeline, return bundle (slow, ~30–60s)
- `GET /latest`              — return last bundle from volume (fast, free)
- `GET /health`              — liveness

The CesiumJS frontend should hit `/latest` after a run, then read
`bundle.plan.candidates[0]` for the top experiment to visualize.

## One-off run via CLI (no deploy)

```bash
modal run modal_app.py::cli --brief "frontier 3D geospatial"
```
