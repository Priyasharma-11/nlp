# Phase 4 — implementation and verification
Version 0.4.0. Phase 1–3 documentation and functionality retained. No schema change, paid API, or public deployment.

## Implemented
- NLP pipeline: NFC normalization, whitespace, casefolding, word and sentence segmentation, stopwords with negation preservation, Porter stemming, n-grams, optional spaCy POS/NER/lemmas and WordNet fallback; user-provided scientific terminology spans. Original inputs are preserved. Not a scientific equation parser.
- Count and TF-IDF features, NMF and LDA topics, optional Word2Vec, supervised logistic regression with stratified holdout and classification report/confusion matrix.
- Keyword counts, TF-IDF cosine, BM25 (k1=1.5,b=.75), optional MiniLM/SciBERT/SPECTER2 dense cosine, weighted reciprocal rank fusion, related-paper search excluding seed. Search uses saved titles/abstracts/provider authors/topics; no full-text retrieval yet. No independent reranker or persistent vector index; in-memory indexing on each request. No automatic domain classification or scientific stance classifier.
- NLP Laboratory, Semantic search, Evaluation page wiring. Evaluation reports precision@K, recall@K, MRR@K, nDCG@K from user judgments; classification metrics from user labels. No synthetic performance presented as real.

## Test evidence
`python -m pytest -q`: 34 passed, 1 skipped in 3.84s. Includes 19 prior regression tests, 15 Phase 4 tests. UI module skipped because Streamlit missing. Compilation passed. Controlled encoder fixture exercises semantic and hybrid ranking math, not real pretrained inference. Word2Vec tested on explicitly synthetic data. No pretrained transformer or spaCy language weights available; WordNet and Punkt resources missing. Full scientific NER/stance models, genuine dataset benchmarks, live academic API connections, UI runtime, Windows installation, model compatibility and performance remain unverified. Existing Phase 3 limitations (OCR, tables/figures/equations, heuristic section extraction) remain. No private PDFs transmitted.

## Next approval gate
Phase 5: structured paper analysis with source-linked extractive summaries, multi-paper comparisons, citation analysis and evidence-backed graph. Proposed dependencies NetworkX and Plotly; graph source provenance required. Avoid guessing relationships. No new implementation before approval.
