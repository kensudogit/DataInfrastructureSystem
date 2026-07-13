#!/bin/sh
set -eu
echo "[adinfra] boot"
echo "[adinfra] PORT=${PORT:-unset}"
echo "[adinfra] PWD=$(pwd)"
ls -la /app/apps/api || true
ls -la /app/apps/web/out | head -n 20 || true
python -c "import apps.api.main; print('[adinfra] import apps.api.main OK')"
exec python -m apps.api.server