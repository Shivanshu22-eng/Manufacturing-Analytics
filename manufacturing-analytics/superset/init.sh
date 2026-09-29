#!/bin/sh
# Superset initialization script — runs on first boot
set -e

echo "==> Upgrading Superset DB..."
superset db upgrade

echo "==> Creating admin user..."
superset fab create-admin \
  --username "${SUPERSET_ADMIN_USER:-admin}" \
  --firstname "MFG" \
  --lastname  "Admin" \
  --email     "${SUPERSET_ADMIN_EMAIL:-admin@mfg.local}" \
  --password  "${SUPERSET_ADMIN_PASSWORD:-admin123}" || true

echo "==> Initializing Superset..."
superset init

echo "==> Superset ready!"
exec superset run -p 8088 --with-threads --reload --debugger
