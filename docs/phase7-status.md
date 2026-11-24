# Phase 7 — Quality, integration and evaluation (0.7.0)

## Delivered
- Shared CSS refinements applied to every page: sidebar, cards, buttons, focus outlines, typography and narrow-screen rules. Welcome and Overview updated with actual publication-year counts. Visual accessibility and browser layout are not verified.
- Evaluation page now includes citation coverage/validity, human support judgments, claim-label metrics and an offline SciFact-format runner. CLI available as scripts/evaluate_scifact.py. No dataset is bundled.
- PDF signature/size checked before hashing. Local causal, NLI and transformer adapters request safetensors and disable remote code where supported. Compatibility with actual weights remains unverified. Some older weights may be unavailable in this format. Use trusted local model and adapter directories only. Several untrusted text render paths changed to plain text; this is not a comprehensive sanitization audit.
- Hybrid zero-weight branch no longer unnecessarily loads a model; stopword-only evidence queries abstain before indexing inference. Existing in-memory caching retained; no speedup benchmark or persistent vector database claimed.
- End-to-end backend test: synthetic PDF ingestion → SQLite → evidence retrieval → source-linked extractive output → citation validation → deletion. All prior tests retained.

## Actual verification
55 passed, 1 skipped in 4.46 seconds (pytest). Skipped item is the Streamlit module, including all-page navigation tests. Python compileall succeeded. Synthetic fixture tests establish code behavior only. Attempt to install Streamlit failed (no accessible package distribution); attempt to retrieve SciFact from GitHub failed with ConnectError. No live provider, real SciFact/BEIR benchmark, local model inference, Windows runtime, browser rendering, load test or independent security audit has been verified. No public deployment or paid API.

## Benchmark protocol
Use the genuine SciFact corpus.jsonl and claims_dev.jsonl from the official dataset distribution (https://github.com/allenai/scifact). Do not use unlabeled test claims or the training set as independent validation. Run from project root after installation:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_scifact.py data/scifact/corpus.jsonl data/scifact/claims_dev.jsonl --method BM25 --k 5 --output scifact-bm25.json
```

Repeat for TF-IDF, Semantic, Hybrid; optional `--nli <trusted-local-model-directory>`. The runner ranks sentence chunks, deduplicates retrieved paper IDs and measures document relevance at passage cutoff; this is not the official SciFact sentence-level scoring protocol. Claim gold labels aggregate annotated evidence; no-evidence labels mean insufficient evidence. Retrieval metrics exclude no-evidence claims. Citation ID validity and coverage are computed; human faithfulness is deliberately null. Use the Evaluation page to enter independent human judgments. Compare same split, corpus, K and model versions. Do not interpret exact-match baseline as scientifically reliable. Full-corpus runtime/memory not tested; BEIR remains unimplemented as a dataset-specific runner.

## Security review and outstanding work
Local loopback binding, upload/page/text limits, ORM parameter binding, foreign keys, environment secrets, ignored data/models, bounded request retry/cache, no automatic PDF download or remote AI inference remain in place. No auth, multiuser isolation, encryption at rest, isolated PDF parser process, dependency vulnerability scan, penetration test or production security certification. Public hosting would require these additional controls as appropriate. Public metadata queries are sent to selected providers; private PDFs are not sent by the application. Model loader safety changes do not guarantee safe third-party weights or adapters. Generated citations are not factual entailment. No deployment configuration or live URL yet; Phase 8 requires approval.

See phase7-acceptance-audit.md for all original criteria. Back up data before upgrading. No schema changes in Phase 7.
