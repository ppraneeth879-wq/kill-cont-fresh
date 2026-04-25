# KillCont API — Cloud Run image.
#
# Slim Python 3.12 base with the FastAPI app + uvicorn. Cloud Run sets PORT
# at runtime; we honour it in the CMD so the same image runs locally with a
# different port.
#
# Build (from repo root)::
#
#   gcloud builds submit apps/api --tag gcr.io/<project>/killcont-api:latest
#
# Local sanity test::
#
#   docker build -t killcont-api apps/api
#   docker run --rm -p 8080:8080 -e PORT=8080 \\
#       -e RUNTIME_PROFILE=local \\
#       -e AUTH_BACKEND=demo \\
#       -e ALLOWED_ORIGINS=http://localhost:5173 killcont-api

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Pillow needs libjpeg + zlib at runtime; grab the minimum.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY app ./app

# Cloud Run mounts a writable in-memory filesystem at /tmp; route the
# local-mirror media dir there so PIL helpers can write even when the
# container image is read-only.
ENV MEDIA_DIR=/tmp/var/media \
    DB_PATH=/tmp/var/app.db \
    PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
