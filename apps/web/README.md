# AdInfra Web (Next.js + React + TypeScript)

PostgreSQL に統合された広告配信実績を可視化するフロントエンドです。

## 起動

```bash
# 1) PostgreSQL + API
cd C:\devlop\DataInfrastructureSystem
docker compose up -d postgres
# API（別ターミナル）
.\.venv\Scripts\activate
uvicorn apps.api.main:app --reload --port 8000

# 2) データ投入（初回）
python scripts\run_pipeline.py --date 2026-07-13 --load-db

# 3) Web
cd apps\web
npm install
npm run dev
```

http://localhost:3000

PostgreSQL ホストポート: `5433`（`DATABASE_URL=...@localhost:5433/adinfra`）

## 環境変数

| Key | Default |
|-----|---------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` |
