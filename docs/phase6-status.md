# Phase 6 — 0.6.0

Implemented section-preserving exact substring chunking with overlap, in-memory BM25/TF-IDF and optional MiniLM semantic/hybrid passage index, bounded in-process vector cache, source reference validation, extractive evidence response, optional local causal LM JSON generation, optional local NLI, exact-match baseline with abstention, mixed-evidence aggregation, selected-corpus analytics and candidate leads derived from extracted limitations/future work. Existing database used read-only; no new schema. UI routes wired for assistant, claims and analytics. Evaluation helpers report citation-ID validity, citation coverage, human-rated faithfulness and unsupported-claim rate, passage retrieval metrics and claim classification report. No measured benchmark claims are made.

## Verification limits
- Streamlit not installed in sandbox: all UI tests skipped, including prior phases; Windows/PyCharm and visual browser inspection remain unverified.
- Live academic APIs remain unverified from previous phases.
- Optional local causal LM, NLI and scientific transformer weights unavailable; controlled test doubles test ranking, schema, citation and classification logic only.
- Exact matching is not scientific claim verification. NLI is experimental and uncalibrated; contradictory or mixed evidence does not establish scientific truth.
- Citation validity is not semantic entailment. Extractive snippets can omit important context. No retrieval relevance threshold has been validated for dense similarity.
- Passage cache is in-memory and bounded by entries, not bytes. Corpus limited to 100 papers/10,000 chunks; persistent vector storage, stronger reranking and performance measurements remain outstanding.
- Analytics reflect selected papers only; terminology mentions do not establish methodology use; author/institution names can conflate entities; research leads are not proven gaps. Automated underexplored combinations and emerging-topic validation remain future enhancements.
- Scientific benchmarks, real document extraction quality, OCR, scientific NER, table/equation parsing, model accuracy and human evaluation remain pending. Evaluation helpers are not a full benchmark UI.
- No paid service, external document transmission, public deployment or GitHub upload performed.
