# ResearchMind Cloud Edition v0.9.0

**For Streamlit Community Cloud, deploy `cloud_app.py`, NOT `app.py`.** The cloud entrypoint creates an isolated, temporary in-memory database for each Streamlit session. No login system or durable multi-user storage is provided. Use private app sharing and public/non-sensitive authorized materials only. See [cloud deployment instructions](docs/cloud-deployment.md) and [cloud verification report](docs/cloud-status.md).

The following original local-edition instructions remain available. For local persistent use, always launch with `--server.address=127.0.0.1 --server.maxUploadSize=20` because the shared cloud configuration no longer forces loopback and limits upload size to 5 MB. The original v0.8.0 release remains unchanged separately.

## Local edition reference (v0.8.0 baseline)
Local-first scientific research workspace. This release adds public academic metadata search and local PDF extraction to the Phase 2 foundation. Phase 4 adds classical NLP, local corpus search and optional pretrained model adapters. No automatic model downloads, paid services or public deployment are enabled.

## Windows / PyCharm quick start
Extract the ZIP, open the ResearchMind folder (the one containing app.py) in PyCharm and open its PowerShell terminal. Install Python 3.11 from python.org if `py -3.11 --version` fails.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1 --server.maxUploadSize=20
```
Open http://127.0.0.1:8501 if the browser does not open automatically. In PyCharm select `.venv\Scripts\python.exe` as the project interpreter. The commands do not require activating the virtual environment or changing PowerShell execution policy. Internet is needed for the initial dependency installation. Stop the app with Ctrl+C.

## Verify the workflow
1. Welcome → Open research workspace. Overview starts at zero.
2. Library → Create collection; give it a name such as `My research`.
3. Add metadata from a real paper you have permission to use (title, year, DOI and optional abstract). Manual metadata is not externally verified.
4. Assign the saved paper to your collection. Search its title with the library filter.
5. Return to Overview; verify counts and activity. Restart the application; verify persistence.
6. Confirm deletion of the test record in Library; verify collection membership is removed.
7. Visit the remaining research modules; optional models require local weights and scientific results require source data.

## Files
- `app.py`: Streamlit entry point.
- `src/researchmind/config.py`: local storage configuration.
- `schemas.py`: Pydantic validation and DOI normalization.
- `db/models.py`, `db/engine.py`: SQLAlchemy tables, SQLite initialization and session factory.
- `services/library.py`: transactional application services, counts, filtering and collection membership.
- `ui/workspace.py`: styled navigation, welcome, overview, library and methodology screens.
- `tests/`: backend and Streamlit smoke tests.
- `docs/phase1/`: approved architecture and requirements. `docs/phase2-status.md`: verification and approval gate.

## Storage & privacy
The database is created in `data/researchmind.sqlite3`, relative to the launch directory. Set `$env:RESEARCHMIND_DATA_DIR = 'C:\path\to\private-folder'` before launch to change it. No .env loader is used. Data is local and unencrypted; do not place sensitive documents in a shared directory. Local loopback binding is intentional; do not expose this single-user app to the public. No login. Discovery sends search queries to the selected academic API; uploaded PDFs remain local. Keep the database out of Git. Stop the app before copying the data folder for backup; keep SQLite sidecar files together. Additive SQLite migrations run automatically on startup. Back up the data folder before upgrading.

## Troubleshooting
- `py -3.11` not recognized: install Python 3.11 and the Python launcher, or select the installed interpreter in PyCharm.
- `No module named researchmind`: run the editable install from this folder using the same interpreter.
- Port occupied: append `--server.port 8502` to the Streamlit command.
- Dependency installation fails: check internet / package-index access; do not bypass TLS.
- Database error: check writable storage and available space; do not delete existing data to fix it.

## Version control
To start your own local Git repository after extracting: `git init`, `git add .`, `git commit -m "ResearchMind v0.8.0 release candidate"`. No remote repository or public deployment is created. The archive does not include Git history or the virtual environment.

## Phase 3 workflow
1. Discover papers → choose OpenAlex, Crossref or arXiv → enter a topic → Search literature. Results are provider metadata, not necessarily verified full text.
2. Save a result to Library. Raw and normalized records and retrieval time are stored separately.
3. Paper analyzer → select the matching saved paper → upload an authorized PDF → Extract locally. Verify page labels against the original.
4. Review section-filtered passages and download the original PDF. Image-only pages are flagged, not OCRed.
5. Optional PowerShell settings: `$env:OPENALEX_API_KEY = 'your-free-key'`; `$env:CROSSREF_MAILTO = 'your-email'`. Do not use a paid-enabled key without approval. `.env.example` is reference only.

## Updating Phase 2
Stop the old app and back up its entire data directory. Extract Phase 3 into a separate directory. Copy the backed-up data directory into Phase 3 (or point RESEARCHMIND_DATA_DIR at a copied database). Reinstall dependencies using the quick-start commands. Start the new app; migration preserves the four foundational tables. Do not open an upgraded database with the old app.

See `docs/phase3-status.md` for test evidence, limitations and next approval gate.

## Phase 4 workflow
- NLP laboratory: paste scientific text, inspect normalization, tokens, stems, n-grams and (when installed) language-model outputs. Scientific entities uses a user-provided JSON terminology dictionary, not trained scientific NER.
- Representations and Topics use saved titles, abstracts and provider author/topic metadata. Word2Vec is exploratory; tiny corpora give poor vectors.
- Classification: enter a JSON object mapping saved paper IDs to human labels, e.g. `{"1":"AI","2":"Biology"}` (format example only; at least four distinct papers per class). The classifier trains on a stratified training split and reports held-out results. Avoid near-duplicate publications and leakage. No pre-trained topic classifier is bundled.
- Semantic search: choose Keyword, TF-IDF or BM25 for offline retrieval; Semantic and Hybrid require an installed local model. Filter by year, author or provider topic. Related-paper seed excludes itself. Hybrid uses weighted reciprocal rank fusion with constant 60. Scores are not confidence. The index is rebuilt in memory from the saved metadata; PDFs remain available in the analyzer but passage retrieval is reserved for later evidence Q&A.
- Evaluation: enter a JSON array of judged queries, e.g. `[{"query":"your topic","relevant_ids":[1,2]}]` (format only). Use your own genuine saved IDs and independently assigned relevance labels. Run the comparison and export actual metrics. MRR is truncated at K; precision divides by K even if fewer results are returned. No real scientific benchmark scores are bundled.

### Optional NLP resources (download explicitly; no private document text is sent)
```powershell
.\.venv\Scripts\python.exe -m nltk.downloader punkt_tab wordnet
.\.venv\Scripts\python.exe -m spacy download en_core_web_sm
.\.venv\Scripts\python.exe -m pip install -e ".[word2vec]"
```
spaCy model installation: https://spacy.io/usage/models . The generic model does not reliably extract scientific methods/datasets. Without its weights, POS/NER are explicitly unavailable; WordNet can provide a basic lemmatization fallback. Punkt has a simple sentence-boundary fallback.

### Optional transformer setup
The model downloads can be large. Run only when you have internet, disk space, and wish to enable local CPU inference. Review each model's license. Install the optional dependencies and download the models you need:
```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[ai]"
.\.venv\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
.\.venv\Scripts\python.exe -c "from transformers import AutoTokenizer,AutoModel; n='allenai/scibert_scivocab_uncased'; AutoTokenizer.from_pretrained(n); AutoModel.from_pretrained(n)"
```
SPECTER2 uses distinct short-query and paper adapters (paper-to-paper recommendations use the proximity adapter). Model card: https://huggingface.co/allenai/specter2 . Install the compatible adapters extra and explicitly download the base and adapters:
```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[ai,specter]"
.\.venv\Scripts\python.exe -c "from transformers import AutoTokenizer; from adapters import AutoAdapterModel; n='allenai/specter2_base'; AutoTokenizer.from_pretrained(n); AutoAdapterModel.from_pretrained(n)"
.\.venv\Scripts\python.exe -c "from huggingface_hub import snapshot_download; snapshot_download('allenai/specter2_adhoc_query',local_dir='models/specter-query'); snapshot_download('allenai/specter2_proximity',local_dir='models/specter-paper')"
$env:RESEARCHMIND_SPECTER_QUERY = (Resolve-Path 'models/specter-query').Path
$env:RESEARCHMIND_SPECTER_PAPER = (Resolve-Path 'models/specter-paper').Path
```
Launch the app in the same terminal. These model installation and inference steps are unverified in the sandbox; exact package compatibility may need adjustment. All inference is local; a missing model produces an error, never a substituted lexical result. SciBERT mean pooling is an experimental baseline, not a model specifically trained for similarity. Inputs are truncated to model limits. Keep downloaded weights out of Git.

### Update from Phase 3
Stop the app, back up `data/`, extract this release into a separate directory, copy the data backup into it, reinstall dependencies and run tests. Phase 4 does not alter the database schema. See `docs/phase4-status.md` for verification and limitations.

## Phase 5 workflow
1. Save genuine paper metadata and upload an authorized PDF in Paper analyzer.
2. Select the document version, inspect extractive full-text, abstract, section or technical summaries and expand structured fields.
3. Compare 2–10 saved papers in Compare papers; inspect original excerpts and export CSV.
4. In Knowledge graph, select papers and optionally enter method and dataset names. Inspect provider citations, authorship, topics, affiliations and exact terminology mentions. Filter node types, pan/zoom, inspect edge evidence, export JSON.
5. Citation counts are provider snapshots; unresolved references retain their identifiers. Graphs and summaries are computed from persistent records, not separately stored.

See docs/phase5-status.md for testing and limitations. No new schema migration is necessary. Back up your previous data directory before upgrading.

## Phase 6 — Evidence intelligence
After installing the core dependencies, save papers and upload matching PDFs, select papers in Research assistant, choose BM25 and enter a question. Extractive mode returns original evidence passages, not a generated conclusion. Select TF-IDF or optional MiniLM semantic/hybrid ranking. The index uses the latest uploaded document version per paper, keeps page/section/source identifiers, excludes references and splits passages into overlapping exact substrings. Dense vectors are cached in process memory (not a persistent vector database). Restart clears the cache.

Optional local generation: install `.[ai]`, obtain a compatible trusted causal LM in a local directory (review its license and hardware requirements), and enter that path in Research assistant. No automatic downloads or remote inference occur. The adapter expects JSON output; invalid output/citations fall back to extractive passages. Citation validation checks IDs and provenance, not whether a generated sentence is entailed by evidence. Local generation has not been tested with model weights here.

Claim verification defaults to exact textual matching only; it abstains on paraphrases or disagreement unless an optional local NLI classifier is supplied. The NLI model directory must expose explicit entailment, neutral and contradiction labels. Mixed evidence is reported separately. Scores are uncalibrated, not scientific confidence. NLI inference has not been verified with real weights. Use the research analytics page for selected-corpus publication years, indexed topics, author/institution names, user-specified terminology mentions, and reported limitations/future work as candidate leads. These are not global literature coverage or validated research gaps.

Upgrade: stop the old app, back up `data/`, extract the new archive separately, copy the backup, install `.[dev]`, run `python -m pytest -q` and `python -m streamlit run app.py` using your virtual environment. No schema migration is needed for Phase 6. See docs/phase6-status.md.

## Phase 7 — Quality and evaluation
Shared workspace styling and expanded Evaluation page are included. Run the offline SciFact CLI or upload labeled benchmark files in Evaluation. See `docs/phase7-status.md` for commands, actual test results and limitations, and `docs/phase7-acceptance-audit.md` for all 38 original criteria. Model loaders now request safetensors; actual model compatibility remains unverified. No schema changes; stop the old app and back up data before upgrading. No public deployment.

## Phase 8 — Release preparation
58 backend tests passed; one Streamlit test module skipped in the sandbox. Docker, Windows, live APIs and scientific benchmarks remain unverified. See `docs/deployment.md`, `docs/phase8-status.md` and `docs/phase8-acceptance-audit.md`. Offline BEIR-format evaluation is available through `scripts/evaluate_beir.py`. No public deployment or remote repository has been created.

## Local scientific named-entity recognition (optional)

The NLP laboratory now offers two clearly separated approaches:

- **Local scientific NER (GLiNER):** zero-shot extraction from user-selected labels, suitable for trying multiple scientific domains. It is a model prediction, not a verified annotation or a guarantee of coverage for every discipline.
- **User terminology dictionary:** exact, boundary-aware matching against terms you supply. This remains useful for controlled vocabularies but is not trained NER.

Install the optional dependency in the project PowerShell terminal:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[ner]"
```

Download a compatible GLiNER model separately from its official model page, review its license and storage requirements, and keep its files in a local folder. ResearchMind does **not** download model weights automatically. In NLP laboratory → Scientific entities, choose **Local scientific NER (GLiNER)**, enter that folder path, and provide comma-separated labels such as:

`method, dataset, disease, gene, protein, chemical, task, material, metric, organism`

The label set is editable; use labels appropriate to the paper's field. Start with the default confidence threshold and inspect the returned text, type, character offsets and score. Predictions can be wrong or miss entities; manually review them before using them in analysis. If the model is not installed or the folder is invalid, the app reports an actionable error rather than silently falling back to the dictionary.

To run the new focused tests after installing the development dependencies:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_nlp.py -q
```
