"""
Apache Superset Configuration
Loaded automatically by Superset at startup via SUPERSET_CONFIG_PATH.
"""
import os

# Secret key — MUST be overridden in production
SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "manufacturing-superset-dev-secret-change-in-prod")

# Database
SQLALCHEMY_DATABASE_URI = os.getenv(
    "SUPERSET_DB_URI",
    "postgresql+psycopg2://superset:superset@superset-db:5432/superset",
)

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS":   True,
    "DASHBOARD_CROSS_FILTERS":    True,
    "ENABLE_JAVASCRIPT_CONTROLS": True,
}

# Allow embedding
TALISMAN_ENABLED = False
WTF_CSRF_ENABLED = False

# Rows limit (raise so dashboards get useful data)
ROW_LIMIT = 100_000
VIZ_ROW_LIMIT = 100_000

# Allow users to create public links
PUBLIC_ROLE_LIKE = "Gamma"

# Default theme
APP_NAME = "Manufacturing Intelligence"
APP_ICON = ""

# Logging
LOG_LEVEL = "INFO"
