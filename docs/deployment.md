# Installation and deployment — v0.8.0
## Windows / PyCharm (recommended)
Open the folder containing app.py. Python 3.11 is recommended. In PowerShell:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev,word2vec]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```
Select the same interpreter in PyCharm. Browse http://127.0.0.1:8501. Stop with Ctrl+C. Install optional NLP/model resources using README.md. A local database is created in data/. A fresh installation starts empty. No API keys required for local workflows. Network is needed for installing dependencies and public literature discovery.

## Docker Desktop (prepared, not executed)
Use Linux containers. From the project root:
```powershell
docker compose config
docker compose up --build -d
docker compose ps
docker compose logs -f
Invoke-WebRequest http://127.0.0.1:8501/_stcore/health
```
Open the local URL. Stop with `docker compose down` (retains named volume). Do not use `down -v` unless intentionally deleting local research data. The container runs as a non-root user; only loopback is published. Health endpoint checks Streamlit availability, not full scientific functionality. Baseline container excludes optional model weights. To use existing Windows data, prefer native setup; migrate only a stopped and backed-up database with ownership/permissions checked. Docker image uses a version range, not a fully locked reproducible supply chain. Do not publish the port publicly: no authentication or tenant isolation. No Docker daemon available in the verification sandbox.

## GitHub-ready local repository
```powershell
git init
git add .
git status
git commit -m "ResearchMind v0.8.0 release candidate"
```
Inspect staged files before commit. Data, secrets, models and virtual environments are ignored. Remote creation/push is not authorized. Review dependency licenses (especially PyMuPDF AGPL/commercial) and choose a compatible project license before distribution. CI is configured for Windows/Linux and a Docker health smoke check; it has not run on GitHub. No live URL, API URL or remote repository exists. Streamlit is the only interface; no REST server is required.

## Backup and upgrade
Stop both old and new apps. Back up the complete data directory, including SQLite sidecars if present. Copy into a separate extracted project or point RESEARCHMIND_DATA_DIR at a copy. Run tests, start the new app and verify library, PDFs, collections and counts. No schema change in Phase 8. Do not downgrade an upgraded database. Docker volumes and native data are separate.

## Evaluation
Use genuine labeled dataset files; never substitute synthetic fixtures for benchmark evidence. For SciFact see phase7-status.md. For BEIR, extract an official dataset folder with corpus.jsonl, queries.jsonl and qrels/test.tsv. Run:
```powershell
.\.venv\Scripts\python.exe scripts/evaluate_beir.py data/beir/scifact --split test --method BM25 --k 10 --output beir-bm25.json
```
Repeat with TF-IDF or optional Semantic/Hybrid; same split and K. BEIR runner uses graded linear-gain nDCG and binary relevance for precision, recall and MRR; no-positive queries excluded. This is a local comparison protocol, not an official BEIR reproduction. Real dataset evaluation and full-corpus resource measurements remain unverified. Review results and document hardware/model versions.

## Troubleshooting
Missing Python: install the official Python launcher. Missing module: repeat editable install with the same interpreter. Port busy: append `--server.port 8502`. Missing model: use BM25/extractive mode or install trusted local weights explicitly. API failure: check access, rate limits and provider settings; manual metadata + authorized PDF workflow remains available. Database failure: check writable folder, space and backup; never delete data blindly. Docker build failure: inspect build logs, package resolution and Docker Desktop Linux engine.
