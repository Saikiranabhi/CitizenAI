# # Dockerfile
# # ─────────────────────────────────────────────
# # Stage 1: Builder — install deps in isolation
# # ─────────────────────────────────────────────
# FROM python:3.11-slim AS builder

# WORKDIR /app

# # Install build dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

# # Install Python dependencies into a prefix
# COPY requirements.txt .
# RUN pip install --upgrade pip \
#     && pip install --prefix=/install --no-cache-dir -r requirements.txt

# # ─────────────────────────────────────────────
# # Stage 2: Runtime — lean final image
# # ─────────────────────────────────────────────
# FROM python:3.11-slim AS runtime

# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     FLASK_ENV=production \
#     PORT=5000

# WORKDIR /app

# # Copy installed packages from builder
# COPY --from=builder /install /usr/local

# # Create non-root user for security
# RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# # Copy application source
# COPY . .

# # Ensure NLTK data is available at runtime
# RUN python -c "import nltk; nltk.download('vader_lexicon', quiet=True)"

# # Fix ownership
# RUN chown -R appuser:appgroup /app

# USER appuser

# EXPOSE ${PORT}

# # Gunicorn: 4 workers, timeout 120s, bind to dynamic port
# CMD ["sh", "-c", "gunicorn app:app --workers 4 --timeout 120 --bind 0.0.0.0:${PORT} --access-logfile - --error-logfile -"]


# ─────────────────────────────
# Stage 1: Builder
# ─────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────
# Stage 2: Runtime — lean final image
# ─────────────────────────────────────────────

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

WORKDIR /app

COPY --from=builder /install /usr/local

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

RUN mkdir -p /home/appuser/nltk_data \
    && mkdir -p /home/appuser/.cache/huggingface \
    && chown -R appuser:appgroup /home/appuser

ENV HOME=/home/appuser \
    NLTK_DATA=/home/appuser/nltk_data \
    TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface

COPY . .

RUN python -c "import nltk; nltk.download('vader_lexicon', download_dir='/home/appuser/nltk_data', quiet=True)"

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE ${PORT}

# CMD ["sh", "-c", "gunicorn app:app --workers 4 --timeout 120 --bind 0.0.0.0:${PORT} --access-logfile - --error-logfile -"]
CMD ["python", "app.py"]
