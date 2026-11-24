# Security, deployment, roadmap and approval
## Security and reliability
Local single-user default, bind server to localhost; no auth implied for public access. Validate PDF header, size/pages, sanitized path, isolated temp extraction, resource/time limits and cleanup. Use SQLAlchemy bound parameters, environment/secrets outside repository, .gitignore for data/models/.env, least privileges, redact query content and credentials from logs. Remote fetch only allowlisted provider endpoints and approved OA links with HTTPS, redirect and private-IP checks; no arbitrary URL fetch by default. Treat documents as untrusted prompts; prevent tool execution from document instructions. External processing opt-in, disclose transmitted data and provider. Cache with TTL and invalidation; rate limit, retry/backoff and timeout; bounded uploads, model batches, pagination, lazy models; clear errors, no fabricated fallback. Backup SQLite and private documents consistently, test restoration. License review for PyMuPDF (AGPL/commercial), models, datasets and provider terms before redistribution; consider pypdf alternative if license constraints demand it. No automatic telemetry of private content.

## Deployment strategy
Local Windows first. Docker CPU image with pinned dependencies and nonroot process, health check, mounted private data, configurable host/port. GitHub Actions offline unit/integration checks and secret scanning; no publishing/deploy workflow by default. Streamlit Community Cloud candidate only for non-sensitive demonstration data; review resource limits and storage persistence. PostgreSQL and durable object storage require approval if multi-user/production. Docker Compose only if multiple services justified. Public deployment requires authentication/access policy, credentials, privacy notice, backup, smoke checks and approval; verify actual URL, upload/search/answer and persistence after restart. No live URL or GitHub repository yet; supply only after creation and verification. Deliver README, install/test/deploy instructions, architecture/ER/data flow, NLP/model/dataset/retrieval/RAG/graph documentation, measured results, known limits, future work, slide presentation, demo script, interview Q&A, resume bullets (actual achieved results only).

## Eight-week roadmap and gates
| Week | Work and exit deliverable | Gate |
|---|---|---|
| 1 | Foundation, Git, env, database, PDF extraction, cleaning, tokenization, stops, stems, lemmas, POS, NER; verified pipeline | G2 then G3 as approved |
| 2 | BoW/TF-IDF, n-grams, cosine, BM25, classification and provider-backed lexical search | G4 |
| 3 | General/scientific embeddings, semantic search, related papers, retrieval comparison | G4 |
| 4 | Sections, summaries, methods/datasets/results/limits and paper comparison | G5 |
| 5 | Hybrid ranking/reranking, citation metadata, graph, evidence-linked relationships | G5 |
| 6 | Chunking, index, retrieval, RAG, source-linked QA, optional local generator | G6 |
| 7 | Verification, topic/stance analysis, trends/gaps, full UI integration | G6 then G7 |
| 8 | Unit/integration/UI/E2E tests, benchmark and error analysis, performance, docs, packaging, presentation | G7 then G8 |
Weeks 9–12 buffer for model compatibility, UI and validated advanced features. Time estimates conditional on laptop and skill level; no claim of scheduled background execution.

## Original phase mapping
G1: original 1 + initial inspection (18); G2: 2 + foundation parts of 11/15/18; G3: 3–4; G4: 5–6; G5: 7–8; G6: 9–10; G7: 11–15 integration and verification; G8: 16–17. Original 18 governance and 19 roadmap apply throughout. All detailed original requirements included verbatim in root file; final acceptance criteria tracked separately.

## Risk register
| Risk | Mitigation |
|---|---|
| API metering and access | no payment credentials, budget circuit breaker, cache, authorized uploads, fallback adapters |
| Python/Windows dependency mismatch | Python 3.11 proposed; verify wheels before installing; separate optional ML dependencies |
| Slow local inference | CPU-first, small models, batch and cache, extractive fallback; measure |
| Paywalls/licensing | abstract labels, OA only, authorized uploads, license review |
| PDF parsing failure | preserve coordinates, flag missing data, optional OCR/GROBID |
| Hallucinations or false claims | evidence IDs, validation, abstention, human audit |
| Domain shift | separate SciFact and CS evaluation, report limits |
| Scope creep | gated releases, weeks 9–12 buffer, core features first |
| Privacy/security | local-only defaults, secret isolation, no public access without approval |

## G2 approval request
Objective: create the actual repository foundation, typed configuration, DB migration baseline, professional navigation shell and tests. Affected: app.py, src/researchmind/{config,schemas,db,ui}, tests, pyproject.toml, .env.example, .gitignore, .streamlit/config.toml, README. Proposed dependencies: Streamlit, SQLAlchemy, Pydantic, pytest; add PyMuPDF after license review at ingestion gate, heavy ML later. Risks: Windows wheel compatibility and existing repo conflicts. Deliverable: runnable local app shell with actual persisted empty state and database tests, not a fake research dashboard. No paid API, public deployment or existing-file overwrite. Before G2 inspect actual Windows output or uploaded repository. Commands below are inspection only:

```powershell
Get-Location
Get-ChildItem -Force
py -0p
python --version
python -m pip --version
python -m pip list
$env:VIRTUAL_ENV
 git --version
 git status --short
```
If no repository exists, create only after approval. Proposed commands after approval and compatibility check: `py -3.11 -m venv .venv`, `.\.venv\Scripts\python.exe -m pip install --upgrade pip`, install approved pinned dependencies, `\.venv\Scripts\python.exe` path should be ` .\.venv\Scripts\python.exe` from project root; use ` .\.venv\Scripts\python.exe -m streamlit run app.py` and ` .\.venv\Scripts\python.exe -m pytest -q`. No command has been run on your Windows laptop.
