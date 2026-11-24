# Knowledge graph and UI/UX specification
## Scientific graph
Use NetworkX MultiDiGraph, stable typed IDs; nodes for papers, authors, institutions, methods, algorithms, datasets, topics, research questions, venues. Directed edge types CITES, WROTE, AFFILIATED_WITH, PUBLISHED_BY (venue or verified publisher), USES_METHOD, EVALUATES_DATASET, INVESTIGATES, EXTENDS, COMPARES. Citations come from verified provider reference IDs; method/dataset edges require explicit extracted evidence; EXTENDS and COMPARES require explicit passages rather than similarity. Edge metadata includes source record or chunk ID, extraction method, timestamp and review status. Unknown relationship omitted. Visual filters by edge/node type, year and collection; default max 100 nodes, expand on demand; layout seeded; display degree/citation counts with missing values distinct from zero, timelines and provenance. PyVis HTML must escape untrusted labels and disallow external scripts where feasible; Plotly graph fallback.

## Design system
Light research workspace; navy #17283C, primary blue #345F8E, teal #3A8A7A, background #F2F5F9, white surface, slate #536473, dark body #233D54; use darker teal for small text and verify contrast. Status colors accompanied by text and icons. Inter/Manrope headings, Inter body, IBM Plex Mono for technical labels (local/system font fallback). Font scale 12/14/16/20/28/36 px; spacing 4/8/12/16/24/32; radii 6/10/14; restrained shadow; focus outlines 2 px. Persistent sidebar, descriptive labels, responsive columns with stack on narrow viewport, accessible inputs, semantic headings, no fake metric cards. Native Streamlit widgets preferred; custom CSS scoped; no unsafe user HTML. Use spinners/progress for long tasks, empty states with action, concise error with retry, success only after commit, confirm deletion. Charts use labels, legends, accessible palette and underlying table. Subtle transitions only where supported; respect reduced-motion settings.

| Screen | Content / interactions | Data source |
|---|---|---|
| Welcome | Hero, introduction, capabilities, workflow, tech overview, CTA, footer | Static documentation, clearly labeled |
| Dashboard | Papers, collections, recent uploads/searches/activity, domain chart, shortcuts | Repository counts/activity |
| Discovery | Query, provider, filters, relevance, abstracts, metadata, save and related | Provider + retrieval services |
| Library | Saved papers, collections, access labels, deletion, export | Repository |
| Analyzer | Upload, section extraction, metadata, field cards, summaries, page evidence | Document and analysis services |
| NLP lab | Text stages, tokens, stems, lemmas, POS, NER, n-grams, BoW/TF-IDF, classification, topics, embeddings | NLP services |
| Compare | Multi-select, side-by-side fields, metrics and evidence | Comparison service |
| Semantic search | Similarity-ranked results, explanations, related papers | Retrieval service |
| Graph | Typed nodes/edges, filters, details, citations and timelines | Graph builder |
| Assistant | Conversation, collection scope, answer mode, passages, abstention | Evidence assistant |
| Verification | Claim, labels, evidence, uncertainty, explanation | Verification service |
| Analytics | Publications, methods, datasets, topics, authors/institutions, candidate gaps | Analytics service |
| Evaluation | Model/data versions, run controls, metrics, comparisons, error cases | Evaluation runs |
| About | Architecture, models, sources, methodology, limitations, docs | Versioned documentation |

## Wireframe (logical)
```
┌──────────────────┬──────────────────────────────────────────┐
│ ResearchMind     │ Research overview                         │
│ Discover         │ [Search topic / title / DOI] [Search]     │
│ Library          │ [Papers] [Collections] [Domains]           │
│ Analyze          │ Publication trend | Recent activity      │
│ Compare          │ Recent papers and quick actions           │
│ NLP Lab          │                                          │
│ Graph            │ Selected record → metadata → evidence    │
│ Assistant        │                                          │
│ Verify / Trends  │ Local processing • source access labels  │
│ Evaluation       │                                          │
└──────────────────┴──────────────────────────────────────────┘
```
Acceptance: keyboard operation, meaningful empty/loading/error states, no horizontal clipping at common desktop/mobile widths, source passage reachable from result, real backend values only. Streamlit AppTest plus actual browser manual checks; Playwright optional for browser flows if needed.
