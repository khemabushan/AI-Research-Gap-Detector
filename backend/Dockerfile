FROM python:3.11-slim

WORKDIR /app

# System deps needed for faiss-cpu / sentence-transformers wheels at build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p /app/data/faiss_indexes

ENV PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////app/data/app.db \
    FAISS_INDEX_DIR=/app/data/faiss_indexes

EXPOSE 8000

# Shell form (not exec-form JSON array) so ${PORT} is actually expanded —
# Render injects PORT at runtime and requires the container to bind to it;
# the 8000 fallback keeps `docker run` / docker-compose working unchanged
# for local use where PORT isn't set.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
