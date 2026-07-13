# DataInfrastructureSystem

広告媒体データの収集・統合・分析・AI最適化向けデータ基盤パッケージです。

Google / Yahoo! / Meta / X / LINE / TikTok など複数媒体の配信実績を取得し、共通スキーマへ正規化したうえで、DWH・BI・AI に連携します。

## アーキテクチャ概要

```
[Ad Platform APIs]
  Google Ads / Yahoo! Ads / Meta / X / LINE / TikTok
        │
        ▼
[Collectors]  Python adapters（モック対応）
        │
        ▼
[Landing / Raw]  object storage or staging tables
        │
        ▼
[ETL/ELT]  Airflow + Pandas / Spark / dbt
        │
        ▼
[Warehouse]  PostgreSQL（ローカル） / Snowflake / BigQuery / Redshift
        │
        ├─► [BI] Tableau / Power BI / Looker Studio / QuickSight
        ├─► [API] FastAPI（レポート・メトリクス）
        └─► [AI] OpenAI / Azure OpenAI / Bedrock / Vertex + LangChain
```

## 主な機能

| 領域 | 内容 |
|------|------|
| データ収集 | インプレッション、クリック、CV、広告費、CPC/CPM/CPA、CTR、ROAS 等 |
| 正規化 | 媒体横断の共通ディメンション・ファクトモデル |
| 変換 | Pandas / Spark / dbt |
| 配信 | FastAPI、BI 接続ビュー |
| AI | 入札・予算配分の最適化提案 |

## ディレクトリ構成

```
DataInfrastructureSystem/
├── apps/
│   ├── api/                  # FastAPI API（PostgreSQL 優先）
│   └── web/                  # Next.js + React + TypeScript フロント
├── packages/
│   ├── collectors/           # 媒体別コレクタ
│   ├── common/               # 共通スキーマ・設定・DB
│   ├── transformers/         # Pandas / Spark 変換
│   └── ai_optimizer/         # AI 最適化
├── dbt_project/              # dbt モデル
├── airflow/dags/             # Airflow DAG
├── spark/jobs/               # Spark ジョブ
├── sql/                      # DDL（PostgreSQL）
├── bi/                       # BI 接続メモ
├── infra/                    # クラウド構成テンプレート
├── docker-compose.yml
└── requirements.txt
```

## クイックスタート（ローカル）

### 前提

- Python 3.11+
- Node.js 20+
- Docker Desktop（PostgreSQL）

### セットアップ

```bash
cd C:\devlop\DataInfrastructureSystem
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
copy .env.example .env
```

### PostgreSQL 起動 & データ投入

```bash
docker compose up -d postgres
python scripts\run_pipeline.py --date 2026-07-13 --load-db
```

PostgreSQL はホストの `5433` ポートで公開します（既存の 5432 と衝突回避）。
接続文字列: `postgresql+psycopg2://adinfra:adinfra@localhost:5433/adinfra`

### API 起動

```bash
uvicorn apps.api.main:app --reload --port 8000
```

- OpenAPI: http://localhost:8000/docs
- メトリクス: `GET /api/v1/metrics?start_date=2026-07-01&end_date=2026-07-13`（PostgreSQL 優先）
- AI 提案: `POST /api/v1/ai/optimize`

### Railway デプロイ

ルート Dockerfile が Next.js を静的ビルドし、FastAPI が同一ポートで配信します。

- `/` … サービス画面（AdInfra コンソール）
- `/api/v1/*` … API
- `/docs` … OpenAPI
- `/health` … ヘルスチェック

Railway では `DATABASE_URL` を PostgreSQL サービス接続に設定してください。再デプロイ後、公開 URL のルートで画面が表示されます。


### 収集〜統合（バッチ）

```bash
python -m packages.collectors.cli collect --date 2026-07-13 --media all
python -m packages.transformers.cli transform --date 2026-07-13 --load-db
```

## 環境変数

`.env.example` を参照してください。媒体 API キー未設定時はモックデータで収集できます。

## クラウド連携

- **AWS**: Glue / Redshift / QuickSight / Bedrock（`infra/aws`）
- **Azure**: Data Factory 相当フロー / Azure OpenAI（`infra/azure`）
- **GCP**: Dataflow / BigQuery / Vertex AI（`infra/gcp`）
- **Snowflake**: dbt profile `snowflake`（`dbt_project/profiles.yml.example`）

## ライセンス

Private / Internal use.
"# DataInfrastructureSystem" 
