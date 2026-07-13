# Railway デプロイ（502 回避チェックリスト）

## 必須設定

### 1. Custom Start Command を空にする
**Settings → Deploy → Custom Start Command**  
→ 空（Dockerfile の `CMD` を使う）

### 2. PORT をサービス変数で上書きしない
**Variables** に `PORT=8000` などを自分で入れない  
（Railway が自動注入する値を使う）

### 3. 公開ドメインの Target Port
**Settings → Networking → Public Networking**

- Target Port が **3000 / 8000 などに固定**されていると 502 になりやすい
- **空 / 未設定（Railway 既定）**にするか、Deploy Logs の  
  `binding 0.0.0.0:XXXX` の XXXX と一致させる

### 4. 正常起動のログ例
```
[adinfra] env.PORT='XXXX'
[adinfra] binding 0.0.0.0:XXXX
INFO:     Uvicorn running on http://0.0.0.0:XXXX
```

## 確認 URL
- `/health` → `{"status":"ok",...}`
- `/` → AdInfra 画面
