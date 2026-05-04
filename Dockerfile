FROM python:3.12-slim

LABEL io.modelcontextprotocol.server.name="io.github.prakhargour10/utility-mcp-server"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/huggingface \
    EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
    RAG_RAW_DOCS_DIR=/app/docs/doc_list \
    RAG_EMBEDDINGS_PATH=/app/data/embeddings.json

WORKDIR /app

# Install CPU-only torch first (avoids the multi-GB CUDA wheels pulled in
# by the default sentence-transformers dependency tree on Linux).
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
        torch==2.4.1

COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt

COPY main.py .
COPY utility_mcp_server/ utility_mcp_server/
COPY docs/ docs/

# Pre-download the embedding model so the container starts offline-ready
# and pre-build the FAISS vector store so the first request is fast.
RUN python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('${EMBEDDING_MODEL}')" \
    && python -m utility_mcp_server.rag.cli rebuild

EXPOSE 8000

ENTRYPOINT ["python", "main.py"]
