FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --wheel-dir=/wheels -r requirements.txt


FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /tmp/requirements.cachekey

RUN --mount=type=bind,from=builder,source=/wheels,target=/wheels \
    pip install --no-cache-dir /wheels/*

COPY . .

# Non-root user for worker safety: celery worker must not run as root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Pre-create the model-cache dir (staging mounts a named volume at this path)
# so the volume inherits appuser ownership on first use instead of the
# default root:root — otherwise the non-root worker could not write the
# HuggingFace (BGE-M3) and Docling artifact caches.
RUN mkdir -p /home/appuser/.cache/huggingface /home/appuser/.cache/docling \
    && chown -R appuser:appuser /home/appuser/.cache
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
