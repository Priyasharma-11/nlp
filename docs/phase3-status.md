# Phase 3 delivery record — v0.3.0

## Changes
- OpenAlex, Crossref and arXiv search adapters using HTTPX, with page limits, in-memory bounded ten-minute cache, bounded retries, basic request spacing and optional environment credentials. Only explicit user queries go to providers. No full-text automatic downloads.
- DOI/provider-ID deduplication, separate normalized and raw provider metadata, retrieval timestamps and original PDF bytes stored in SQLite. No fuzzy cross-provider deduplication for DOI-less records.
- Local PyMuPDF extraction, PDF signature/size/page/password validation, Unicode NFC, heuristic heading recognition and column ordering, page/block coordinates, empty-page warnings, SHA-256 deduplication. PDF-to-paper association is user-selected; embedded metadata is unverified. No table/figure/equation semantic extraction, OCR, sentence segmentation or reliable scientific summaries yet. Text order and section detection need real-corpus validation.
- Forward-only SQLite migrations using PRAGMA user_version and transactional additive table creation, rather than introducing Alembic for a single local database. Revision 1 recognizes Phase 2 tables, revision 2 adds source_records, documents and passages. Existing Phase 2 fields are preserved. No destructive migration.
- Discovery and Paper analyzer pages connected to real services; no fabricated result rows.

## Verification
Executed on Linux/Python 3.13.5: `python -m pytest -q` → 19 passed, 1 skipped (Streamlit test module unavailable). 10 Phase 2 regression tests and 9 new tests passed. API tests use explicit synthetic HTTPX MockTransport fixtures only; they do not establish live connectivity. Synthetic PDF fixture tests validate extraction, section labels, empty page detection, original bytes, hash deduplication and cascade deletion. Migration tested against legacy schema with saved record. Python compileall passed. Live requests to all three providers attempted and failed as unreachable. No real scientific corpus was downloaded. Windows/Python 3.11 runtime, visual appearance and UI tests remain unverified.

## Limitations and safeguards
Provider availability, credentials, quotas and terms can change. Basic request spacing is not a guaranteed quota or spending cap; use a free-only key or no key. API cache is process-local; raw metadata is persisted only for saved results. User-selected PDF association and heuristic extraction need review. SQLite contains unencrypted PDFs: keep data directory private, delete papers to remove associated records logically (not secure erasure), back up before migration. PDF size and page limits reduce but do not eliminate parser resource risks. Do not expose the single-user app publicly. PyMuPDF is offered under AGPL/commercial licensing; review obligations before distributing or hosting a proprietary product. Do not purchase a license without approval. Semantic Scholar and Europe PMC remain planned optional sources; no claim of implementation. 

## Provider documentation
- https://help.openalex.org/api/authentication/
- https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- https://info.arxiv.org/help/api/user-manual.html
- https://pymupdf.readthedocs.io/

## Next approval gate
Phase 4: classical preprocessing, TF-IDF/BM25, classification, NER, topic models, scientific embeddings, semantic and hybrid retrieval, evaluation. No ML models downloaded yet. Proposed dependencies NLTK, spaCy, scikit-learn, NumPy, sentence-transformers/PyTorch (optional heavy model group). Validate Phase 3 live search and Streamlit locally first, or carry the blocker forward explicitly.
