"""
Modal deployment for the Geospatial AI Autoresearcher.

Anthropic agent-design notes:
- This is a **workflow**, not an autonomous agent: a fixed prompt-chain
  retrieve → extract* → plan. We chose this because the steps and ordering
  are known up front; an autonomous agent loop would add cost and latency
  with no benefit (see Anthropic "Building effective agents").
- Step 2 uses the **parallelization** pattern (one LLM call per source).
- Step 3 merges generation + scoring into one call (saves a hop, lets the
  model rank in shared context).

Deploy:
    modal deploy modal_app.py

Run once (no deploy):
    modal run modal_app.py::cli --brief "your brief here"

HTTP usage after deploy:
    GET  https://<your-modal-url>/research?brief=...
    GET  https://<your-modal-url>/latest
    GET  https://<your-modal-url>/health
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import modal

APP_NAME = "geospatial-ai-autoresearcher"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "openai>=1.50.0",
        "tavily-python>=0.5.0",
        "pydantic>=2.7",
        "requests>=2.32",
        "pdfminer.six>=20231228",
        "wikipedia>=1.4.0",
        "fastapi[standard]>=0.115.0",
        "raindrop-ai>=0.0.50",
    )
    .add_local_python_source("src")
)

app = modal.App(APP_NAME, image=image)

# Persistent volume for artifacts so Cory's CesiumJS frontend can fetch them.
volume = modal.Volume.from_name("autoresearch-data", create_if_missing=True)
DATA_DIR = Path("/data")

# Secrets: create with
#   modal secret create autoresearch-secrets \
#       OPENAI_API_KEY=... TAVILY_API_KEY=...
secrets = [modal.Secret.from_name("autoresearch-secrets")]


@app.function(
    secrets=secrets,
    volumes={str(DATA_DIR): volume},
    timeout=600,
)
def run_pipeline_remote(brief: str, n_tavily: int = 3, n_arxiv: int = 3) -> dict:
    """Single-call pipeline. Returns the full bundle and writes artifacts to volume."""
    from src.agents.pipeline import run_pipeline

    bundle = run_pipeline(
        brief=brief,
        n_tavily=n_tavily,
        n_arxiv=n_arxiv,
        out_root=DATA_DIR / "runs",
    )
    volume.commit()
    return bundle.model_dump()


@app.function(secrets=secrets, volumes={str(DATA_DIR): volume}, timeout=60)
@modal.fastapi_endpoint(method="GET", docs=True)
def research(brief: str = "frontier 3D geospatial / world models for scene understanding",
             n_tavily: int = 3, n_arxiv: int = 3) -> dict:
    """Fire-and-forget. Modal's HTTP gateway hard-caps responses at ~150s, but the
    pipeline can take longer with large max_results. We spawn the work and return
    immediately; clients poll /latest to get the result when it's done."""
    call = run_pipeline_remote.spawn(brief=brief, n_tavily=n_tavily, n_arxiv=n_arxiv)
    return {
        "status": "started",
        "call_id": call.object_id,
        "brief": brief,
        "n_tavily": n_tavily,
        "n_arxiv": n_arxiv,
        "poll": "/latest",
        "note": "Run started in the background. Poll /latest in 30-180s for the bundle.",
    }


@app.function(secrets=secrets, volumes={str(DATA_DIR): volume}, timeout=900)
@modal.fastapi_endpoint(method="GET")
def research_sync(brief: str = "frontier 3D geospatial / world models for scene understanding",
                  n_tavily: int = 3, n_arxiv: int = 3) -> dict:
    """Synchronous variant. Subject to Modal's ~150s HTTP gateway timeout, so use
    only with small n_tavily/n_arxiv (default 3+3 finishes in ~30s)."""
    return run_pipeline_remote.local(brief=brief, n_tavily=n_tavily, n_arxiv=n_arxiv)


@app.function(volumes={str(DATA_DIR): volume})
@modal.fastapi_endpoint(method="GET")
def latest() -> dict:
    """Return the most recent bundle.json (cheap, no LLM cost). For the CesiumJS frontend."""
    volume.reload()
    latest_dir = DATA_DIR / "runs" / "latest"
    if not latest_dir.exists():
        return {"error": "no runs yet"}
    return json.loads((latest_dir / "bundle.json").read_text())


@app.function()
@modal.fastapi_endpoint(method="GET")
def health() -> dict:
    return {"ok": True, "app": APP_NAME}


@app.local_entrypoint()
def cli(brief: str = "frontier 3D geospatial / world models for scene understanding"):
    bundle = run_pipeline_remote.remote(brief=brief)
    print(json.dumps(bundle["plan"], indent=2))
