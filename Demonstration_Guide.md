# ResearchMind — 8-minute demonstration
## Before the demonstration
Install the project using docs/deployment.md, run tests, and launch the local app. Save real metadata and upload authorized PDFs for SciBERT (https://arxiv.org/abs/1903.10676), SPECTER (https://arxiv.org/abs/2004.07180), RAG (https://arxiv.org/abs/2005.11401), and SciFact (https://aclanthology.org/2020.emnlp-main.609/). Verify each PDF matches its metadata. Do not present synthetic fixtures as publications. Prepare a backup local corpus for unreliable internet. Rehearse the workflow and verify pages before presenting.

| Time | Action | Narration |
|---|---|---|
| 0:00–0:45 | Welcome and dashboard | Research workflows are fragmented; ResearchMind connects discovery, analysis and evidence. |
| 0:45–1:30 | Library and Discover Papers | Public APIs retrieve metadata; private documents stay local. If APIs fail, use saved records. |
| 1:30–2:30 | Paper Analyzer | Upload a PDF, show extracted sections and original page references. |
| 2:30–3:20 | NLP Laboratory | Show tokens, TF-IDF and topic modeling; explain negation preservation. |
| 3:20–4:10 | Semantic Search | Compare BM25 and TF-IDF; show semantic/hybrid only if real model inference was verified. |
| 4:10–5:00 | Comparison and Graph | Inspect methods, dataset mentions and citations; explain mention vs use. |
| 5:00–6:10 | Research Assistant | Ask about limitations and inspect original excerpts. Demonstrate insufficient evidence on an unrelated query. |
| 6:10–6:50 | Claim Verification | Show exact-match baseline and abstention; optional NLI only after verification. |
| 6:50–7:30 | Analytics and Evaluation | Show local counts, candidate leads and actual evaluation metrics if obtained. |
| 7:30–8:00 | Close | 58 controlled tests passed; browser, real model and scientific benchmarking remain pending until locally verified. |

## Failure recovery
If API calls fail, use saved papers. If embeddings are missing, explicitly choose BM25. If a PDF is scanned, use an authorized text-based version. If a question has weak evidence, acknowledge it. Never show fabricated scores or claim a failed step succeeded.
