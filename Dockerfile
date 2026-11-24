FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 RESEARCHMIND_DATA_DIR=/workspace/data
WORKDIR /workspace
RUN groupadd --gid 10001 research && useradd --uid 10001 --gid 10001 --create-home research
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY app.py ./
COPY .streamlit ./.streamlit
RUN mkdir -p /workspace/data && chown -R research:research /workspace/data
USER research
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3).close()"
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.headless=true"]
