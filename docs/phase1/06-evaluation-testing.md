# Evaluation, quality and testing
## Experimental protocol
Use BEIR SciFact for retrieval and original SciFact for evidence labels; preserve official splits and corpus, no test tuning. Separate manually annotated AI/CS set (target 50 queries, 30 QA/claims, 20 papers) with relevance and source judgments; label annotator limitations. arXiv categories for classification; select balanced labeled subset and record license. Maintain corpus hash, split, model revision, random seed, settings, hardware, latency and actual output. Report macro-F1, per-class scores, error cases and sample size. No fabricated metrics or claims of superiority. Compare exact/TF-IDF/BM25/dense/hybrid, general vs scientific embeddings, extractive vs approved generation, basic vs evidence-aware RAG. Same split and candidate pool; tune on dev only.

| Task | Metrics and rationale | Proposed gate (not measured) |
|---|---|---|
| Classification | accuracy, macro precision/recall/F1, confusion matrix for imbalance | beat majority baseline or document why not |
| NER / graph | entity/edge precision, recall, F1 on labeled subset | 100% displayed edges have provenance; manual precision target 0.85 |
| Retrieval | precision@k, recall@k, MRR, nDCG@10 | report all baselines; aim hybrid >= best baseline, otherwise select best |
| Recommendations | human relevance, precision@k | explain each suggestion, report judgment coverage |
| Summaries | ROUGE/BERTScore where reference exists; manual factuality/completeness | no unsupported numerical claims in reviewed demo sample |
| QA/RAG | answer relevance, context relevance, faithfulness, citation correctness/coverage, unsupported claim rate | 100% valid citation IDs; target >=90% manual citation correctness, disclose failures |
| Verification | macro F1, per-label precision/recall, evidence recall, human review | outperform majority baseline or mark experimental; abstain on missing evidence |
| Performance | p50/p95 latency, peak memory, corpus size | warm search p95 <2s on 1k abstracts target; report hardware |
| UX | completion rate, time, user feedback | target 5 users and 4/5 complete search/upload/evidence tasks without assistance |

## Test plan
Unit: DOI normalization, dedup, page offsets, parser malformed/scanned file, section rules, tokens, negation, BM25/rank fusion, similarity, citation ID validation, stance aggregation, graph provenance, gaps scope. Integration: mocked provider responses clearly test fixtures (200/429/500/timeout/pagination), SQLite transaction rollback/constraints, upload→persist→index→search, index invalidation after delete, real authorized PDF fixture, retrieval→answer→source mapping, model-unavailable fallback, analytics denominator and filtering. Live provider smoke tests only with budget and approval; report separately from mock tests. UI: AppTest navigation, inputs, no-data/error states; manual browser upload/graph/export, keyboard and responsive checks. E2E: search genuine record, save, upload authorized PDF, analyze, compare, retrieve question, inspect original page, graph, verify claim, export and delete; restart and confirm persistence. Security: malicious filenames, oversized files, invalid magic, prompt injection, HTML escaping, traversal, log redaction, external URL SSRF controls, no secret commits. Performance: cold/warm model load, batches, index rebuild and memory profiling.

Proposed commands after implementation: `python -m pytest -q`, `python -m pytest -m integration`, `python -m pytest -m benchmark`; CI will use offline deterministic fixtures; model and live tests explicitly marked. Test results must record executed command, date, environment and failures. No application tests have been run during design.
