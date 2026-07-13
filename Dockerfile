# syntax=docker/dockerfile:1

FROM node:22-alpine AS web-builder
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
ENV NEXT_PUBLIC_API_BASE_URL=
RUN npm run build

FROM python:3.11-slim

WORKDIR /app

# Do NOT set PORT here — Railway injects PORT at runtime.
# Setting PORT in the image often causes 502 (proxy/target port mismatch).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    AI_PROVIDER=mock \
    COLLECTOR_USE_MOCK=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.docker.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY apps ./apps
COPY packages ./packages
COPY sql ./sql
COPY scripts ./scripts
COPY pyproject.toml ./
COPY --from=web-builder /web/out /app/apps/web/out

RUN test -f /app/apps/web/out/index.html \
    && python -c "from apps.api.main import app; print('import-ok', app.title)"

# Hint for Railway networking detection (actual bind uses $PORT at runtime)
EXPOSE 8080 3000 8000

CMD ["python", "-m", "apps.api.server"]
