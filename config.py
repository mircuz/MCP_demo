"""
Centralised configuration for the Databricks MCP Server.
Each section groups settings for a specific domain.
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Databricks Workspace
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATABRICKS_HOST        = "https://e2-demo-field-eng.cloud.databricks.com"
SQL_WAREHOUSE_ID       = "4b9b953939869799"
MODEL_SERVING_ENDPOINT = "databricks-gpt-5-mini"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Lakebase (Postgres-wire)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAKEBASE_HOST     = "ep-polished-cloud-d1w1d99q.database.us-west-2.cloud.databricks.com"
LAKEBASE_USER     = "mirco.meazzo@databricks.com"
LAKEBASE_PORT     = 5432
LAKEBASE_DATABASE = "databricks_postgres"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Vita Insurance API  (placeholders — replace with real values)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VITA_API_BASE_URL = "https://PLACEHOLDER.example.com/api/compagnie"
VITA_API_TOKEN    = "PLACEHOLDER_JWT_TOKEN"
# Default company code used in path parameters
VITA_DEFAULT_COMPAGNIA = "PLACEHOLDER_COMPAGNIA"
