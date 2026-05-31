"""
Orchestrator. Anthropic workflow pattern: prompt-chain retrieve → extract* → plan.
The * is parallelization (concurrent per-source extraction).

Observability: Raindrop. The whole `run_pipeline` call is one Interaction;
each step (retrieve / extract-per-source / plan) is a child span.
"""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List

import raindrop.analytics as raindrop
from openai import OpenAI

from .extract import extract_record
from .plan import plan_experiments
from .retrieve import retrieve_sources
from .schemas import PipelineBundle, ResearchRecord, SourceCandidate

DEFAULT_BRIEF = "frontier 3D geospatial / world models for scene understanding"

# Initialize Raindrop once per process. tracing_enabled=True lets us use
# @raindrop.interaction / task_span / tool_span decorators in sibling modules.
_RAINDROP_KEY = os.getenv("RAINDROP_WRITE_KEY")
if _RAINDROP_KEY:
    raindrop.init(_RAINDROP_KEY, tracing_enabled=True)


def _write_artifacts(out_dir: Path, bundle: PipelineBundle) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "sources.json").write_text(
        json.dumps([s.model_dump() for s in bundle.sources], indent=2)
    )
    (out_dir / "records.json").write_text(
        json.dumps([r.model_dump() for r in bundle.records], indent=2)
    )
    (out_dir / "experiments.json").write_text(
        json.dumps(bundle.plan.model_dump(), indent=2)
    )
    (out_dir / "bundle.json").write_text(json.dumps(bundle.model_dump(), indent=2))


@raindrop.interaction("autoresearch")
def run_pipeline(
    brief: str = DEFAULT_BRIEF,
    n_tavily: int = 3,
    n_arxiv: int = 3,
    out_root: Path | None = None,
    user_id: str = "hackathon-demo",
) -> PipelineBundle:
    run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    client = OpenAI()

    # One Raindrop Interaction per pipeline run. We finish it at the end with
    # the top-ranked experiment title as `output`.
    interaction = raindrop.begin(
        user_id=user_id,
        event="autoresearch_run",
        input=brief,
        properties={"run_id": run_id, "n_tavily": n_tavily, "n_arxiv": n_arxiv},
    )

    t0 = time.time()
    print(f"[pipeline] run_id={run_id} brief={brief!r}")

    # Step 1
    sources: List[SourceCandidate] = retrieve_sources(brief, n_tavily, n_arxiv)
    print(f"[pipeline] retrieved {len(sources)} sources in {time.time()-t0:.1f}s")

    # Step 2 (parallel). NOTE: OTEL context does not auto-propagate across threads;
    # per-source spans land at the trace root rather than nested under the interaction.
    # Acceptable trade-off for MVP latency.
    t1 = time.time()
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(sources)))) as ex:
        records: List[ResearchRecord] = list(
            ex.map(lambda s: extract_record(s, brief, client=client), sources)
        )
    print(f"[pipeline] extracted {len(records)} records in {time.time()-t1:.1f}s")

    # Step 3
    t2 = time.time()
    plan = plan_experiments(brief, records, client=client)
    print(f"[pipeline] planned {len(plan.candidates)} experiments in {time.time()-t2:.1f}s")

    bundle = PipelineBundle(
        brief=brief, run_id=run_id, sources=sources, records=records, plan=plan
    )

    if out_root is not None:
        run_dir = out_root / run_id
        _write_artifacts(run_dir, bundle)
        latest = out_root / "latest"
        if latest.exists() or latest.is_symlink():
            latest.unlink()
        latest.symlink_to(run_dir, target_is_directory=True)
        print(f"[pipeline] wrote artifacts to {run_dir}")

    top = plan.candidates[0].title if plan.candidates else "(no experiments)"
    interaction.finish(
        output=top,
        properties={
            "n_sources": len(sources),
            "n_records": len(records),
            "n_candidates": len(plan.candidates),
            "top_score": plan.scores[0].total_score if plan.scores else 0.0,
            "duration_s": round(time.time() - t0, 2),
        },
    )

    # Serverless: must flush before the function exits or events are lost.
    raindrop.flush()
    print(f"[pipeline] total {time.time()-t0:.1f}s")
    return bundle


if __name__ == "__main__":
    import sys

    brief = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BRIEF
    out = Path(os.getenv("OUT_DIR", "data/runs"))
    bundle = run_pipeline(brief=brief, out_root=out)
    print(json.dumps(bundle.plan.model_dump(), indent=2))
    raindrop.shutdown()
