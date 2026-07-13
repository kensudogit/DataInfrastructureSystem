# syntax=docker/dockerfile:1

# --- Build Next.js static export ---
FROM node:22-alpine AS web-builder
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
ENV NEXT_PUBLIC_API_BASE_URL=
RUN npm run build

# --- Runtime: FastAPI + static UI ---
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    AI_PROVIDER=mock \
    COLLECTOR_USE_MOCK=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
COPY --from=web-builder /web/out /app/apps/web/out

# Ensure frontend exists (fail build early if missing)
RUN test -f /app/apps/web/out/index.html

EXPOSE 8000

# Railway injects PORT — bind 0.0.0.0:$PORT
CMD ["python", "-m", "apps.api.server"]
