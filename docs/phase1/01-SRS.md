# Software requirements specification
## Scope
ResearchMind supports individual students and researchers discovering, organizing and comparing scientific literature. Start with AI/computer science papers; benchmark scientific verification separately on SciFact biomedical abstracts. Support professors and R&D users later. Competitors: Elicit (review workflows), Consensus (evidence answers), Scite (citation context), ResearchRabbit/Connected Papers (mapping), Semantic Scholar (discovery), SciSpace (PDF assistance). Differentiation hypothesis: inspectable classical vs dense retrieval, provenance and local-first research workspace; not a claim of market uniqueness.

## Functional requirements and acceptance
| ID | Requirement | Acceptance demonstration |
|---|---|---|
| F01 | Discovery: topic, title, author, question, domain, method, dataset and metadata filters | Search genuine provider records; show origin, access type, pagination and failures |
| F02 | Library and ingestion | Save, deduplicate by normalized DOI/provider ID/hash, upload and delete authorized PDF; preserve raw metadata and timestamps |
| F03 | Document intelligence | Extract page text, sections, metadata, paragraphs, references; flag scanned or malformed pages; retain page locations |
| F04 | NLP lab | Inspect normalization, sentence/word tokens, stopwords, stemming, lemmas, POS, NER, n-grams; preserve raw technical expressions |
| F05 | Representations and ML | BoW, TF-IDF, word/contextual/scientific embeddings; classification, topic modeling, scientific stance; report measured metrics |
| F06 | Retrieval and recommendations | Exact, TF-IDF, BM25, dense and hybrid rankings; filters; explain matched terms and similarity; related paper search |
| F07 | Paper intelligence | Extract problem, objectives, questions, background, methodology, algorithms, datasets, setup, results, contributions, limitations, future work; label unavailable or inferred fields |
| F08 | Comparison and summaries | Abstract/full/section/technical/simplified/multi-paper summaries; compare objectives, methods, models, datasets, metrics, results, domains, dates and limitations with citations |
| F09 | Citation and graph | Explore papers, authors, institutions, methods, algorithms, datasets, topics and questions with typed evidence-backed links and filters |
| F10 | Assistant | Retrieve passages from selected collection, generate or extract answer, link each claim to real passage and page/section; abstain when insufficient |
| F11 | Verification | Supported/contradicted/insufficient evidence plus mixed-evidence flag; source passages and uncertainty; never treat as definitive truth |
| F12 | Analytics and gaps | Real publication, topic, method, dataset, author/institution trends; candidate gaps tied to corpus, limits and cited evidence |
| F13 | UI and export | Welcome, dashboard, discovery, library, analyzer, NLP lab, comparison, semantic search, graph, assistant, verification, analytics, evaluation, about; CSV/BibTeX and evidence report export |
| F14 | Evaluation | Run versioned benchmarks; compare baselines, report measured metrics and failures; no fabricated numbers |
| F15 | Persistence and operations | Transactions, migrations, input validation, cache, retry, logging, secrets, local processing disclosure and deletion |
| F16 | Delivery | Tests, reproducible installation, Docker/CI configuration, deployment instructions, portfolio and interview materials; public release only after approval |

## Nonfunctional requirements
Proposed baseline: 16 GB Windows laptop, Python 3.11, CPU mode. On a documented reference machine aim for warm local search p95 under 2 s on 1,000 abstracts; process a 20-page text PDF under 30 s excluding OCR; cap upload at 25 MB/200 pages initially. Measure rather than promise. No paid APIs by default. No external transmission of PDFs without informed approval. Local data survives restart; deletion removes derived chunks/index entries. WCAG-oriented contrast, keyboard navigation, actionable errors; verify with manual browser tests. Maintain typed interfaces and separate UI from storage. No global research novelty or correctness claims.

## Out of scope for first release
Multi-tenant accounts, training foundation models, automatic paywall bypass, automated academic authorship, public deployment, large-scale indexing. Any optional integration requires approval. All F01–F16 remain in full project scope; advanced implementation may need weeks 9–12.
