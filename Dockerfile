# syntax=docker/dockerfile:1

# --- Build Next.js static export ---
FROM node:22-alpine AS web-builder
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
# Same-origin API calls on Railway
ENV NEXT_PUBLIC_API_BASE_URL=
RUN npm run build

# --- Runtime: FastAPI + static UI ---
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
COPY --from=web-builder /web/out /app/apps/web/out

EXPOSE 8000

CMD ["sh", "-c", "uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
