# NLP concepts used in ResearchMind

| Concept | Meaning | Where it appears |
|---|---|---|
| Unicode normalization | Standardizes equivalent Unicode representations without changing the original source. | NLP preprocessing |
| Tokenization | Splits text into words or sentences. | NLP laboratory, lexical retrieval |
| Stopword filtering | Removes low-information terms; preserve negation where appropriate. | Lexical processing |
| Stemming | Heuristic reduction to word stems. | NLP laboratory |
| Lemmatization | Linguistic reduction to dictionary form. | Optional language resources |
| POS tagging | Assigns grammatical categories to tokens. | Optional spaCy model |
| NER | Identifies named entities; scientific terminology requires domain-specific methods. | General model and separate dictionary matching |
| N-grams | Adjacent groups of tokens; capture short phrases. | NLP laboratory |
| Bag of Words | Term-count representation. | Representation experiments |
| TF-IDF | Frequency weighted by inverse document frequency. | Retrieval and classification |
| Word2Vec | Learns word vectors from surrounding context; small corpora are unreliable. | Optional exploratory training |
| Logistic regression | Predicts class probabilities from features. | Scientific text classification experiment |
| LDA / NMF | Discover exploratory topics from document-term patterns. | Topic modeling |
| BM25 | Lexical ranking with term saturation and document length normalization. | Search and passage evidence |
| Transformer | Attention-based contextual representation. | Optional embedding and local reasoning models |
| Cosine similarity | Normalized vector dot product. | Semantic search |
| Reciprocal rank fusion | Combines retrieval rankings rather than incompatible raw scores. | Hybrid retrieval |
| Extractive summarization | Selects original sentences rather than generating new wording. | Paper intelligence |
| RAG | Retrieves context before generating an answer. | Optional local research assistant |
| NLI | Predicts entailment, contradiction or neutral for a text pair. | Optional claim assessment |
| Knowledge graph | Entities and typed relationships with provenance. | Citation and scientific relationship exploration |

## Formulas worth learning
- Cosine similarity: (a dot b) / (norm(a) × norm(b)).
- Weighted rank fusion: (1−w)/(60+lexical rank) + w/(60+semantic rank); absent matches contribute zero.
- Precision@K: relevant hits / K. Recall@K: relevant hits / known relevant documents.
- F1: 2PR/(P+R) when the denominator is positive.
- MRR: mean reciprocal rank of first relevant result; zero when none is retrieved at the cutoff.
- nDCG: discounted cumulative gain divided by ideal discounted cumulative gain; BEIR-format runner uses linear graded gains.

## Learning order
1. Understand text preprocessing and bag-of-words representations.
2. Reproduce TF-IDF and BM25 on a small corpus with known relevance.
3. Learn contextual embeddings and compare actual model results.
4. Study evidence chunking, provenance and RAG fallback behavior.
5. Evaluate claims and factual support independently of citation ID correctness.

The core algorithms and optional adapters are included in the application; scientific quality, pretrained inference and model compatibility still need verification.
