# Phase 8 release candidate — v0.8.0
## Delivered
Cumulative Phase 7 source retained; version labels updated. Added Dockerfile, loopback-only Compose configuration, non-root runtime, health check, build exclusions and Windows/Linux CI plus container smoke job. Added offline BEIR-format evaluator and CLI with graded relevance and validated IDs. Updated installation, deployment and acceptance audit. Portfolio artifacts accompany this application.

## Executed verification
Python 3.13.5 Linux sandbox: 58 passed, 1 skipped in 4.34s. The skip is the Streamlit test module. Compilation succeeded. Three new tests cover BEIR-format loading/graded metrics, unknown judgments and no-positive judgments. Synthetic fixtures only, not real scientific performance. Phase 7 baseline rerun: 55 passed, 1 skipped. Docker binary and Streamlit absent. No remote actions performed.

## Remaining blockers
- Windows/PyCharm, all 14 Streamlit pages and visual/accessibility checks require local execution.
- Live OpenAlex/Crossref/arXiv access not verified; Semantic Scholar and Europe PMC not implemented.
- Optional NLP resources, SciBERT/SPECTER2/MiniLM, local LLM and NLI weights not verified; scientific NER, stance calibration and trained relationship extraction pending.
- OCR, complex PDF tables/equations/figures, robust layout parsing, persistent vector storage and independent reranking pending.
- Extractive summaries and candidate leads are heuristic; simplified generative explanation, scientific novelty, recurring limitation clustering and broader coverage require further work.
- Real SciFact/BEIR dataset benchmarks, human RAG faithfulness and extraction evaluation, latency/memory and scalability measurements not executed. Citation validity does not imply entailment.
- Local single-user security only; no authentication, encryption at rest, tenant isolation, isolated parser, dependency vulnerability scan or independent security review. Dependency/license review required before distribution.
- Docker and CI configuration not executed; no live URL, remote GitHub repository or paid API. Public hosting remains prohibited without explicit approval.

The release is a source-complete baseline for the implemented modules, not a production-certified or scientifically validated final product. See phase8-acceptance-audit.md and original requirements for detail.
