# ResearchMind — Technical interview guide
## Architecture and engineering
**1. What problem does it solve?** Fragmented literature discovery and analysis, with particular focus on traceable evidence rather than unsupported summaries.

**2. Why a modular monolith?** A single-user local app benefits from simpler deployment and transactions. Modules separate UI, acquisition, persistence, retrieval, graph and reasoning. FastAPI is unnecessary until external clients need a contract.

**3. Why SQLite and SQLAlchemy?** SQLite is embedded and convenient for local storage. SQLAlchemy separates query logic and provides parameter binding. PostgreSQL is a future concurrency option.

**4. What are the database entities?** Papers, collections, collection memberships, activity, source records, documents and passages. Source records retain provider metadata; passages retain document and page coordinates.

**5. How do migrations work?** Forward-only additive revisions use SQLite user_version and a transaction. Backups are required before upgrades.

**6. How do you handle duplicate data?** Normalize DOI and provider identifiers for metadata; use SHA-256 for identical PDF bytes. Different versions may still need review.

**7. What about API failures?** Bounded retries, rate spacing, cache, explicit error states and manual metadata/PDF fallback. No fake success.

**8. How is privacy handled?** Uploaded PDFs are stored and processed locally. Public search terms go to academic providers. Local storage is unencrypted and not multi-tenant.

## NLP and retrieval
**9. What is tokenization?** Splitting text into meaningful units; scientific terms such as IL-6 require careful preservation.

**10. Stemming vs lemmatization?** Stemming strips word endings heuristically; lemmatization maps to linguistic base forms. Optional resources are needed for some stages.

**11. Why preserve negation?** Removing not/no/never can reverse scientific meaning.

**12. What is TF-IDF?** Term frequency weighted by inverse document frequency. It emphasizes distinctive terms but does not model contextual meaning.

**13. What is BM25?** A lexical ranking function with term-frequency saturation and document-length normalization. The implementation uses k1=1.5, b=0.75.

**14. What are n-grams?** Consecutive sequences of n tokens; bigrams and trigrams capture local phrases.

**15. What is Word2Vec?** A learned distributional word representation. Small corpora give unreliable vectors.

**16. What is semantic retrieval?** Rank embeddings by similarity, typically cosine. Similarity is not factual support.

**17. Why SciBERT and SPECTER2?** SciBERT represents scientific language; SPECTER2 targets document-level tasks with distinct query and paper adapters. Actual model weights have not been verified here.

**18. How does hybrid search work?** Weighted reciprocal rank fusion combines lexical and semantic ranks using a constant of 60 rather than directly combining incomparable scores.

**19. What is NER?** Identifying named entities. Generic spaCy models do not reliably identify scientific datasets and methods; dictionary matching is a distinct baseline.

**20. What are LDA and NMF?** LDA models probabilistic topics; NMF factorizes a nonnegative document-term matrix. Their clusters are exploratory.

**21. How does classification work?** TF-IDF plus logistic regression with human-assigned labels and a stratified held-out split. Prevent near-duplicate leakage.

## Scientific reasoning
**22. What is RAG?** Retrieve relevant passages, construct context, generate a response and validate citations. The default mode returns original excerpts without a generator.

**23. Why chunk documents?** To retrieve focused evidence within context limits. Default chunks use 120 words and 20 overlap while retaining page and offset provenance.

**24. How are hallucinations handled?** Restrict context, validate citation IDs and original substrings, reject invalid generated output and fall back to extractive evidence. This does not guarantee entailment.

**25. What is NLI?** Classify passage/claim pairs as entailment, contradiction or neutral. Without a local model, the application uses exact matching and abstains otherwise.

**26. Why mixed evidence?** Different retrieved passages may support and contradict the same claim; hiding that disagreement would be misleading.

**27. What is a knowledge graph?** A directed multigraph of entities and typed edges. Metadata-backed citations differ from mere terminology mentions.

**28. How are research gaps identified?** Extract reported limitations and future work as candidate leads, not proven novel topics.

## Evaluation and delivery
**29. Explain precision, recall, MRR and nDCG.** Precision measures relevant results per K; recall measures coverage of known relevant documents; MRR uses first relevant rank; nDCG rewards good ordering, including graded relevance in BEIR-format runner.

**30. How is RAG evaluated?** Citation validity and coverage are mechanical; factual support needs independent human labels or validated entailment methods.

**31. Why macro-F1?** It averages per-class F1 and exposes weakness on minority classes better than accuracy alone.

**32. What have you verified?** 58 controlled tests passed, one Streamlit module skipped in Linux sandbox. These are software checks, not scientific benchmark scores. Real models, Windows, live APIs and Docker remain unverified.

**33. Why Docker?** A consistent runtime configuration with non-root user, local port binding and persistent volume. Image build and health checks still need execution.

**34. What would you improve next?** Verify local UI, run genuine benchmark datasets, measure latency/memory, improve scientific NER and parser quality, add persistent indexes and independent security review.

## References for study
SciBERT: https://arxiv.org/abs/1903.10676 ; SPECTER: https://arxiv.org/abs/2004.07180 ; Sentence-BERT: https://arxiv.org/abs/1908.10084 ; RAG: https://arxiv.org/abs/2005.11401 ; BEIR: https://arxiv.org/abs/2104.08663 ; SciFact: https://aclanthology.org/2020.emnlp-main.609/ .
