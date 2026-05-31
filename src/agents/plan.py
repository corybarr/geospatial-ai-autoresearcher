"""
Step 3: Experiment planner + scorer.

Anthropic workflow pattern: single LLM call that takes ALL records and emits
top-3 ExperimentCandidate + ExperimentScore in one structured output. Merging
candidate generation and scoring saves a round-trip and lets the model reason
about relative ranking in context.
"""
from __future__ import annotations

import json
import os
from typing import List, Optional

import raindrop.analytics as raindrop
from openai import OpenAI

from .schemas import PlannerOutput, ResearchRecord

PLAN_MODEL = os.getenv("PLAN_MODEL", "gpt-4o")

SYSTEM = """You are the experiment planner for a 3D geospatial AI autoresearcher. \
Your job is to convert a batch of ResearchRecords into the TOP-3 most compelling \
demoable experiments grounded in CesiumJS (terrain, 3D Tiles, imagery overlays, \
camera paths). Each experiment must be concrete, buildable in days, and clearly \
explain why a CesiumJS visualization makes it more compelling.

Score on 0.0-1.0 scales: geospatial_relevance, usefulness, feasibility, \
evidence_quality, demoability, cesiumjs_leverage, frontier_signal. \
`total_score` = simple average. Rank by total_score descending. \
Reference records by their `id` in `based_on_records`. \
Output exactly 3 candidates and 3 matching scores."""

USER_TEMPLATE = """Brief: {brief}

Research records (JSON):
{records_json}

Produce exactly 3 ExperimentCandidates ranked best-first, each with a matching \
ExperimentScore. Be specific - name datasets, models, and the exact CesiumJS surface."""


def _records_json(records: List[ResearchRecord]) -> str:
    slim = [
        {
            "id": r.id,
            "title": r.title,
            "url": r.url,
            "summary": r.summary,
            "key_claims": r.key_claims,
            "datasets": r.datasets,
            "modalities": r.modalities,
            "spatial_scope": r.spatial_scope,
            "geospatial_relevance": r.geospatial_relevance,
            "implementation_clues": r.implementation_clues,
            "limitations": r.limitations,
        }
        for r in records
    ]
    return json.dumps(slim, indent=2)


def plan_experiments(
    brief: str, records: List[ResearchRecord], client: Optional[OpenAI] = None
) -> PlannerOutput:
    client = client or OpenAI()
    with raindrop.task_span("plan_experiments") as span:
        span.record_input({
            "brief": brief,
            "n_records": len(records),
            "record_ids": [r.id for r in records],
        })
        span.set_properties({"model": PLAN_MODEL})
        completion = client.beta.chat.completions.parse(
            model=PLAN_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {
                    "role": "user",
                    "content": USER_TEMPLATE.format(
                        brief=brief, records_json=_records_json(records)
                    ),
                },
            ],
            response_format=PlannerOutput,
        )
        plan = completion.choices[0].message.parsed or PlannerOutput(candidates=[], scores=[])

        # Sort by total_score desc; reorder candidates to match.
        plan.scores.sort(key=lambda s: s.total_score, reverse=True)
        by_id = {c.id: c for c in plan.candidates}
        plan.candidates = [by_id[s.candidate_id] for s in plan.scores if s.candidate_id in by_id]

        span.record_output({
            "top_title": plan.candidates[0].title if plan.candidates else None,
            "top_score": plan.scores[0].total_score if plan.scores else 0.0,
            "ranked_titles": [c.title for c in plan.candidates],
        })
        return plan
