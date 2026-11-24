# Phase 5 implementation record — v0.5.0

## Scope and decisions
- Extractive sentence selection and section-aware structured analysis. Each excerpt preserves paper, document version, passage, page and section or provider record identifier; manual abstracts explicitly unverified.
- Thirteen structured fields: problem, objectives, questions, background, methodology, algorithms, datasets, setup, metrics, results, contributions, limitations, future work. Missing fields remain unknown. Pattern matching is not a validated scientific extraction model.
- Abstract, full available text, technical and section summaries; no generative simplified summaries or cross-paper synthesized narrative yet. Comparison supports 2–10 papers, latest document per paper, year, DOI and evidence excerpts; CSV export.
- NetworkX directed multigraph constructed from stored metadata and evidence. DOI/OpenAlex reference resolution, unresolved reference nodes, provider authorship and OpenAlex affiliations, indexed topics, user-supplied method/dataset mentions. No inferred uses/evaluates/extends edges. Unresolved author identity is scoped to provider record, not merged by name. Citation counts kept separately per provider; incoming/outgoing graph citations are corpus-local.
- Plotly pan/zoom, node type filtering, edge evidence table and JSON export, publication-year chart. 500-node visualization limit. Graph and analysis derived at read time from existing SQLite tables; no duplicate derived storage or schema change.
- No private document text sent externally. No paid API, public deployment or external model inference introduced.

## Files
`documents/intelligence.py` extractive fields and summaries; `services/intelligence.py` database evidence access; `graph/network.py` graph construction and visualization; `ui/intelligence.py` comparison and graph pages; existing analyzer and workspace connected. NetworkX and Plotly added to project dependencies.

## Validation
41 tests passed, one Streamlit test module skipped in this execution environment. Synthetic PDF and provider metadata fixtures verify provenance, missing-field behavior, comparisons, graph reference resolution, graph deletion, source distinctions and version ownership. Plotly figure construction tested, not browser rendering. Existing 34 regression tests passed. Tests are functional checks, not scientific accuracy benchmarks. No live API/model validation or Windows browser verification performed. Existing Phase 2–4 limitations retained.

## Remaining limitations
- PDF parsing/section heuristics, sentence splitting and extraction patterns may miss or misclassify content; no table/equation interpretation, OCR, trained scientific NER or factual synthesis. Dataset/method fields are candidate excerpts, not normalized entities. User lexicon graph edges explicitly indicate mentions only. No inferred citation contexts or contradictory findings. Author identity resolution incomplete. Graph filters do not change the full selected-corpus citation table.
- Graph is recomputed each run; large corpora need caching/indexing. External reference nodes are not downloaded. No independent scientific corpus evaluation; actual Streamlit layout, CSV export and interactions require local verification. Phase 4 transformer inference and Phase 3 live API limitations remain.
- Phase 6 requires approval: passage retrieval, evidence-grounded QA with optional local generator, citation validation, claim verification, trends and candidate research gaps.
