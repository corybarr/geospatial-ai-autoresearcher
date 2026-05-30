# Claude Code Handoff — Step 1 SourceCandidate Pipeline

## Repo
- `git@github.com:corybarr/geospatial-ai-autoresearcher.git`

## Task
Implement **step 1 only** for **Geospatial AI Autoresearcher**: build the search/fetch pipeline that produces bounded, deduplicated `SourceCandidate[]` output.

## Goal
Take a research brief and return a clean set of `SourceCandidate` records with preserved provenance and usable fetched text, ready for later extraction into `ResearchRecord`.

## Required files already in repo
Use these as the contract:
- `json-structure.md`
- `step-1-sourcecandidate-implementation.md`
- `implementation-evals/step-1-sourcecandidate-success-eval.json`
- `PROVENANCE.md`

Use these as traced upstream baseline/reference only:
- `third_party/agentic-ai-public/`
- `src/retrieval/upstream_baseline/`

## Scope
Build only:
- query generation
- Tavily adapter
- arXiv adapter
- fetch/clean helper
- `SourceCandidate` normalization
- dedupe pass
- bounded final output set
- runnable entrypoint for step 1

Do not build yet:
- `ResearchRecord`
- experiment generation
- experiment scoring
- second-pass gap logic
- UI work beyond minimal inspection/debug output

## Output contract
The final output must be valid `SourceCandidate[]` as defined in `json-structure.md`.

## Acceptance contract
Your implementation must satisfy:
- `implementation-evals/step-1-sourcecandidate-success-eval.json`

Critical checks include:
- query generation
- retrieval execution
- schema validity
- provenance preservation
- retrieved text presence
- deduplication
- bounded output

## Provenance and reuse rules
- Preserve the upstream provenance chain.
- Do not hide copied logic.
- Reuse the vendored baseline selectively.
- Keep production code in this repo’s own source tree.
- If you adapt logic from upstream, keep attribution comments where appropriate.

## Suggested implementation approach
1. Inspect the upstream retrieval baseline.
2. Implement a thin custom layer in this repo for step 1.
3. Wrap/adapt retrieval tools rather than adopting the upstream report-oriented flow.
4. Emit `SourceCandidate[]` only.
5. Run against the three evaluation briefs in the eval spec.
6. Iterate until all critical checks pass.

## Required deliverables
- implementation under this repo
- runnable entrypoint for step 1
- sample output artifact
- short run instructions
- brief note describing what was reused vs newly written

## Definition of done
Done means a reviewer can run step 1 against the eval briefs, inspect the resulting JSON, and verify that the implementation meets the critical success conditions in the eval spec.
