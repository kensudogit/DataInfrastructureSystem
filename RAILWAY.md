# Railway デプロイ（502 回避）

## ログから分かったこと

Deploy Logs に次が出ている場合、**アプリ自体は起動成功**しています。

```text
[adinfra] env.PORT='8080'
[adinfra] binding 0.0.0.0:8080
INFO:     Uvicorn running on http://0.0.0.0:8080
```

この状態で公開 URL だけ 502 なら、原因はほぼ確実に次です。

> **Public Domain の Target Port がアプリ待受ポートと不一致**

（例: アプリは 8080、ドメインは 3000）

## ダッシュボードでの修正（推奨）

1. Railway → 対象サービス → **Settings → Networking**
2. 公開ドメインの **Target Port を `8080` に変更**（ログの PORT と一致）
3. **Custom Start Command は空**
4. Variables に手動の `PORT=` があれば削除（自動注入に任せる）

## コード側の緩和策

`apps/api/port_bridge.py` が `3000` / `8000` / `8080` へのリクエストを
実際の `$PORT` へ転送します（Target Port の取り違え対策）。

## 確認

- Deploy Logs に `port-bridge 0.0.0.0:3000 -> 127.0.0.1:8080` など
- https://\<domain\>/health → `{"status":"ok",...}`
