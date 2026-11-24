# Streamlit Community Cloud deployment — v0.9.0

## 1. Local smoke test (Windows PowerShell)
Open the inner ResearchMind directory containing cloud_app.py in PyCharm.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q tests/test_cloud.py tests/test_cloud_ui.py
.\.venv\Scripts\python.exe -m streamlit run cloud_app.py --server.address=127.0.0.1
```

Open http://localhost:8501. Accept demo consent. Save public metadata in Library; upload a small authorized public PDF, run BM25 and inspect evidence. Open a separate private/incognito browser window and verify the library is empty. Reset the first workspace; verify data and consent disappear. Navigate all 14 pages. If Streamlit or the host rejects a dependency, inspect the actual error before changing versions.

## 2. GitHub (only when ready)
Create a PRIVATE empty repository manually at https://github.com/new. Open PowerShell in the inner ResearchMind directory (not the parent containing Portfolio). Do not upload the ZIP itself or a virtual environment. Review licenses, especially PyMuPDF AGPL/commercial terms, before distribution or hosting. Review staged files to ensure there are no documents, credentials, models or databases.

```powershell
git init
git add .
git status
git diff --cached --stat
git commit -m "ResearchMind Cloud Edition v0.9.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ResearchMind.git
git push -u origin main
```

Replace YOUR_USERNAME. No remote repository was created by the assistant.

## 3. Deploy manually
Open https://share.streamlit.io/ and connect GitHub. Choose Create app / deploy from GitHub. Repository: YOUR_USERNAME/ResearchMind; branch: main; main file path: **cloud_app.py**; advanced settings Python: **3.11**. Choose an available subdomain. Keep app visibility private and verify sharing settings before inviting anyone. Private repository alone does not replace checking app sharing settings. Do not select app.py, which is the persistent local entrypoint.

The explicit requirements.txt is the lightweight cloud dependency manifest; pyproject.toml retains local package extras. cloud_app.py adds src to the Python path. No external OS packages are expected for baseline functionality. No paid AI API required. No key is needed for local retrieval. Live literature API access depends on provider rules; if OpenAlex requires a key, use a free-budget-only key in Streamlit Secrets as a root-level OPENALEX_API_KEY string. Never commit secrets.toml. Provider quota or account billing remains your responsibility. Search terms are sent to providers; do not submit sensitive queries.

## 4. Acceptance checks after deployment
Check logs, consent gate, all pages, independent sessions, workspace reset, PDF upload and source citations, graph, lightweight retrieval and error handling. Try a public scientific record from arXiv or Crossref. Confirm no unexpected external AI requests. Do not claim live functionality until verified. Streamlit hosting is free subject to its resource/usage policies; no guaranteed capacity or persistence. If limits are exceeded, reduce corpus and number of concurrent viewers. This is an invite-only portfolio demo, not a public multi-user service.

## 5. Local full edition
Use the original v0.8.0 ZIP for the unchanged local setup, or install this edition with `python -m pip install -e ".[dev]"` and launch `python -m streamlit run app.py --server.address=127.0.0.1 --server.maxUploadSize=20`. Optional models and full benchmark CLI remain local. Do not expose app.py to the Internet. Docker config is inherited for local use only and has not been run here.

Official references: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies ; https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy ; https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
