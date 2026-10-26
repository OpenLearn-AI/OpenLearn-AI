FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --wheel-dir=/wheels -r requirements.txt


FROM python:3.11-slim

WORKDIR /app

# System runtime libraries required by the full opencv-python distribution
# (pulled transitively via docling -> docling-slim[standard] -> rapidocr):
# its bundled Qt/FFmpeg libraries link libxcb.so.1, libGL.so.1,
# libglib-2.0.so.0, and libgthread-2.0.so.0, none of which ship with
# python:3.11-slim. libxcb1 is pulled transitively by libgl1.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0t64 \
    && rm -rf /var/lib/apt/lists/*

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
