# Valeria — Hackathon Submission Draft

Status: draft for fast review and revision

## Project name
**Geospatial AI Autoresearcher**

## Form responses

### What did you build? In one sentence:
Geospatial AI Autoresearcher is an autoresearch system that ingests frontier geospatial and world-model signals, turns them into structured evidence with citations, and ranks the next 3D geospatial AI experiments by relevance, usefulness, and feasibility.

### Who are your teammates?
- Cory Barr
- [confirm any additional teammates before submission]

### Please provide the email contact of each person on your team:
- Cory Barr — [fill in preferred submission email]
- Additional teammate(s) — [fill in]

### Please provide a demo video under one minute:
- Pending
- Script draft below

### Please provide a link to your code on Github:
- **Current best draft:** `git@github.com:corybarr/geospatial-ai-autoresearcher.git`

### Did you use Raindrop Workshop and would like to be considered for the track prize?
Draft answer options:
- **If no meaningful integration shipped:** No.
- **If lightweight instrumentation shipped and is demoable:** Yes — we used Raindrop Workshop to trace the autoresearch loop from search through extraction and ranking.

**Current best draft:** No, unless a real Raindrop trace/instrumentation path is completed and visible before submission.

### What was the biggest technical challenges you solved today:
We solved the problem of turning messy frontier research intake across papers, repos, demos, and model launches into a structured, citation-backed decision pipeline that produces concrete 3D geospatial experiment recommendations instead of generic summaries, and we connected that output to a CesiumJS scene so the top recommendation becomes spatially legible and demoable.

## Shorter answer variants

### One-sentence build summary — shorter
We built an autoresearch system that ingests frontier geospatial and world-model signals, turns them into structured evidence with citations, and ranks the next 3D geospatial AI experiments by relevance, usefulness, and feasibility.

### Biggest challenge — shorter
The hardest part was converting noisy multi-source research into structured, ranked, evidence-backed geospatial experiments that could be shown clearly in a live CesiumJS workflow.

## 60-second demo video script

Target length: 45-60 seconds

### Version A — direct and simple
0-5 sec
- Title card / opening app state
- Voiceover: “Geospatial AI Autoresearcher turns frontier geospatial AI signals into ranked next experiments.”

5-12 sec
- Show the research brief input
- Voiceover: “It starts with a frontier research brief focused on 3D geospatial AI.”

12-22 sec
- Show source ingestion / records appearing
- Voiceover: “The system searches across papers, repos, demos, and model launches, then extracts structured evidence including claims, datasets, limitations, and citations.”

22-34 sec
- Show ranked experiment list
- Voiceover: “Instead of stopping at summaries, it converts that evidence into ranked next experiments, weighted for 3D geospatial relevance, usefulness, and feasibility.”

34-48 sec
- Open the top experiment in CesiumJS
- Voiceover: “Then we ground the winning recommendation in a real CesiumJS scene so the idea becomes spatially concrete and immediately demoable.”

48-58 sec
- Hold on final scene + ranked card
- Voiceover: “The result is an autoresearch loop that helps decide what to build next in geospatial AI — with evidence, prioritization, and a map-native demo surface.”

### Version B — more competition-optimized
0-6 sec
- Opening on final ranked result
- Voiceover: “This is Geospatial AI Autoresearcher, an autoresearch system for 3D geospatial AI.”

6-16 sec
- Flip to sources / extraction
- Voiceover: “It finds frontier signals across papers, repos, and demos, and turns them into structured, citation-backed research records.”

16-28 sec
- Show scoring/ranking
- Voiceover: “Then it ranks the next experiments to run based on geospatial relevance, evidence quality, usefulness, and feasibility.”

28-46 sec
- Show CesiumJS scene with selected experiment overlay
- Voiceover: “We use CesiumJS to ground the top recommendation in terrain and 3D scene context, so the experiment is not just a text idea — it becomes spatially legible.”

46-58 sec
- Final composed shot
- Voiceover: “So instead of a generic research copilot, this becomes a concrete decision system for what to build next in geospatial AI.”

## Recommended current submission stance
- Submit with **Retrieval & Knowledge Synthesis** as the primary story
- Treat **Applied Autonomous Research** as the secondary story
- Only opt into the Raindrop track if there is a real, visible integration

## Open fields to confirm before final submit
- actual teammate list
- actual contact email(s)
- whether Raindrop shipped enough to justify track selection
- final demo video link
