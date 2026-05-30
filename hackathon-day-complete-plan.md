# Valeria — Saturday Hackathon Complete Plan

## Project
**Geospatial AI Autoresearcher**

## One-line summary
A two-part system: an autoresearch backend that searches broadly across frontier AI research, and a **CesiumJS web app** that turns the best findings into a ranked experiment plan specifically for **3D geospatial AI**.

## Clean restatement
Build a same-day hackathon demo that proves an autonomous research loop can ingest frontier geospatial/world-model signals, structure them into evidence, and convert them into a **ranked short-list of 3D geospatial experiments**. The backend does the research and planning. The CesiumJS app is the workbench that makes the best recommendation spatially concrete and easy to demo.

## Why this shape
- keeps the autoresearch loop real
- avoids coupling crawling/planning to the map UI
- uses CesiumJS where it is actually differentiated: terrain, 3D Tiles, camera/viewpoint context, and geospatial overlays
- fits the hackathon theme better than a generic trend dashboard
- aligns cleanly to the hackathon's strongest judging lane for this build: **Retrieval & Knowledge Synthesis**, with a concrete applied domain

## Judging alignment
Primary lane to optimize for:
- **Retrieval & Knowledge Synthesis**

Secondary lane naturally covered:
- **Applied Autonomous Research** for the specific domain of 3D geospatial AI

De-emphasized lane unless it becomes genuinely strong:
- **Agent Architectures & Control Loops** as the headline story

Implication:
- the demo should foreground finding, validating, integrating, citing, and structuring information
- any control-loop or observability material should stay supportive, not central

## Minimum impressive end-of-day demo
1. Enter a research brief focused on 3D geospatial AI.
2. Run a bounded research loop over a small live source set.
3. Show structured extraction for each item: claim, modality, dataset, spatial relevance, implementation clue, limitation, and citation.
4. Rank the top 3 proposed experiments.
5. Open the top experiment in CesiumJS and show a concrete scene-level concept overlay.
6. Explain why it won, what evidence supported it, and what to build next.

## Module boundaries

### 1) Researcher / summarizer
Purpose:
- broad intake and synthesis across 3D geospatial AI, broader geospatial AI, and world models

Responsibilities:
- generate or refine search queries
- ingest papers/repos/blogs/model launches
- extract structured facts and claims
- dedupe and cluster near-duplicate findings
- preserve citations and confidence notes

Should not do:
- final experiment prioritization
- CesiumJS-specific UI decisions
- broad generic observability work

### 2) Experiment planner
Purpose:
- narrow the broad intake into ranked **3D geospatial AI** experiments with explicit CesiumJS weighting

Responsibilities:
- score findings against a fixed rubric
- propose concrete experiments, not themes
- explain why each experiment matters now
- produce a top-3 recommendation list

Should not do:
- broad discovery crawling
- generic summarization for its own sake
- drift into non-geospatial frontier commentary

### 3) CesiumJS workbench
Purpose:
- spatialize the top recommendation so the demo feels real and differentiated

Responsibilities:
- load terrain / 3D Tiles / imagery context
- present selected experiment card and rationale
- render simple overlays tied to the experiment concept
- support camera/viewpoint storytelling

Should not do:
- own research orchestration
- become the backend dependency hub

## Data flow / data model

### Flow
1. User enters or selects a research brief.
2. Researcher collects 6-12 sources.
3. Extractor normalizes each source into a structured research record.
4. Planner converts records into experiment candidates.
5. Planner scores and ranks candidates.
6. CesiumJS displays the winning experiment in scene context.

### Core records

#### ResearchRecord
- id
- title
- url
- source_type (paper/repo/blog/model/dataset/demo)
- date
- summary
- key_claims[]
- datasets[]
- modalities[]
- spatial_scope
- 3d_relevance
- implementation_clues[]
- limitations[]
- citation_snippets[]
- confidence

#### ExperimentCandidate
- id
- title
- hypothesis
- based_on_records[]
- required_inputs[]
- expected_output
- cesiumjs_surface
- demo_shape
- build_time_estimate
- novelty_note
- risks[]

#### ExperimentScore
- candidate_id
- geospatial_3d_relevance
- cesiumjs_leverage
- implementation_feasibility
- demo_clarity
- frontier_signal
- evidence_quality
- data_availability
- total_score
- why_it_ranked

## Ranking criteria for experiments
Weight these explicitly:
1. **3D geospatial relevance** — is this actually about spatial/scene/terrain reasoning?
2. **CesiumJS leverage** — does it become more compelling because it can be shown on terrain, 3D Tiles, globe/site context, camera reasoning, or overlays?
3. **Demoability today** — can we show a believable concept by end of day?
4. **Implementation tractability next** — does it suggest a real next build, not a hand-wave?
5. **Frontier signal** — does it reflect a real emerging capability rather than stale baseline work?
6. **Evidence quality** — are the supporting sources concrete and citable?
7. **Data availability** — can we plausibly source the needed assets/data?

## Critical components
- source ingestion over a bounded set of live links
- structured extraction with citations
- visible normalized ResearchRecord schema in the demo
- fixed experiment-generation template
- deterministic scoring rubric
- top-3 experiment list
- compact architecture/pipeline panel for technical depth
- CesiumJS scene with one clear experiment overlay
- backup screenshots / fallback output if live calls wobble

## Biggest risks / unknowns
- live research intake may be noisy or low-signal
- extraction quality may not be consistent enough without templates
- planner can drift into generic recommendations unless rubric is strict
- CesiumJS scene setup can eat time if asset choice is not fixed early
- tempting observability/debug work can steal time from the actual demo

## Raindrop use
Raindrop is **optional** and should not be a product dependency.

Use it only if setup takes less than 30 minutes.

Acceptable use:
- instrument the autoresearch backend
- show traces of search -> extraction -> ranking
- keep a debug view or judge backup proving the loop is real

Do not:
- build the core architecture around Raindrop
- spend meaningful UI time on observability
- let it replace the actual product story

## Build sequence for the next 6-10 hours

### Phase 0 — Lock the wedge
**Target: now -> +30 min**

Deliverables:
- fixed demo brief
- fixed rubric
- fixed source count target
- fixed CesiumJS scene choice
- fixed top-experiment overlay concept
- fixed judging-lane framing: **Retrieval & Knowledge Synthesis** first

Exit criteria:
- no open product questions
- one-sentence story is stable
- the team can say in one line why this is not a generic research dashboard

### Phase 1 — Backend happy path
**Target: next 90 min**

Deliverables:
- source list ingestion
- structured ResearchRecord output
- saved citations
- one prompt/template for extraction
- visible limitation / confidence fields in extraction

Exit criteria:
- can reliably produce records from a small source batch
- records are strong enough to support cited ranking, not just summaries

### Phase 2 — Planner
**Target: following 60-90 min**

Deliverables:
- ExperimentCandidate generator
- scoring rubric implementation
- ranked top-3 list
- rationale text for each score

Exit criteria:
- top-3 list looks specific, geospatial, and non-generic

### Phase 3 — CesiumJS workbench
**Target: following 90 min**

Deliverables:
- stable CesiumJS scene
- experiment selection panel
- one experiment rendered as overlay/annotation/viewpoint story

Exit criteria:
- selected experiment is spatially legible in the browser

### Phase 4 — Demo integration
**Target: following 60 min**

Deliverables:
- single click or single-path demo flow
- clean transition from research records -> ranked experiments -> CesiumJS scene
- compact architecture/pipeline panel visible somewhere in the app or pitch assets
- backup static artifacts captured

Exit criteria:
- full demo runs end-to-end without improvisation
- demo clearly communicates system shape, not just outputs

### Phase 5 — Optional Raindrop pass
**Target: max 30 min, only if core path is already working**

Deliverables:
- traces on backend loop
- one screenshot or live trace for backup/judging

Exit criteria:
- visible proof of agent loop with near-zero product disruption

### Phase 6 — Submission and polish
**Target: final 60-90 min before submission**

Deliverables:
- submission copy
- screenshots/video
- 30-sec and 90-sec pitch versions
- fallback screenshots for every key state
- one sentence explicitly aligning the project to retrieval, synthesis, citation, and structured extraction

Exit criteria:
- ready well before hard deadline

## Timed schedule for today

### 8:00-8:30 AM
- lock project framing
- explicitly choose **Retrieval & Knowledge Synthesis** as the main judging lane
- fix source schema, scoring rubric, and CesiumJS scene target

### 8:30-10:00 AM
- build research ingestion + extraction pipeline
- output structured ResearchRecords with citations, limitations, and confidence

### 10:00-11:15 AM
- build planner
- generate and rank top 3 ExperimentCandidates
- make citation-backed ranking rationale visible

### 11:15 AM-12:30 PM
- build CesiumJS workbench
- render one top experiment as a scene-grounded concept overlay

### 12:30-1:15 PM
- connect backend output to UI
- add a compact architecture/pipeline panel
- make the demo one-path and judge-readable

### 1:15-2:00 PM
- tighten copy, labels, and rationale
- capture screenshots and backup outputs

### 2:00-2:30 PM
- optional Raindrop instrumentation only if core path is done

### 2:30-4:00 PM
- stabilize
- rehearse
- submission assets and pitch
- **feature freeze by 4:00 PM**

### 4:00-4:45 PM
- demo freeze
- no new features
- final QA and packaging

### 4:45-5:15 PM
- lock submission assets and copy

### 5:15-5:45 PM
- submit early

### 5:45-6:15 PM
- reserve buffer for failures, upload issues, or last-minute wording

## First cut-line if time slips
Cut in this order:
1. Raindrop integration
2. clustering/dedupe sophistication
3. broad world-model taxonomy depth
4. architecture panel polish beyond the bare minimum
5. multiple experiment visualizations
6. extra UI polish

Keep at all costs:
- live or fresh bounded source intake
- structured evidence with citations
- ranked top-3 experiments
- one CesiumJS-grounded experiment view

## Strict success condition
By early afternoon, the team must be able to run one complete demo showing:
- bounded frontier research intake
- structured evidence extraction
- ranked 3D geospatial experiment recommendations
- one winning experiment grounded in CesiumJS
- a clear answer to: **what should we build next, and why?**
