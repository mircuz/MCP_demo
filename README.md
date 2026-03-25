# Databricks MCP Server

A modular MCP server exposing Databricks capabilities and customer API integrations as tools for Claude Code.

## Tools

| Domain | Tools | Backend |
|--------|-------|---------|
| **SQL** | `execute_sql`, `get_high_sentiment_articles` | SQL Warehouse (DBSQL) |
| **Lakebase** | `query_lakebase`, `write_to_lakebase` | Lakebase (Postgres-wire) |
| **Models** | `invoke_model` | Model Serving |
| **External** | `fetch_weather` | Open-Meteo REST API |
| **Vita API** | `vita_list_polizze`, `vita_get_polizza`, `vita_get_beneficiari`, ... (12 tools) | Customer REST API |

---

## Quick start

```bash
# 1. Install
cd MCP_demo
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Authenticate
databricks auth login --host https://YOUR-WORKSPACE.cloud.databricks.com

# 3. Configure — edit config.py with your values

# 4. Register in Claude Code
claude mcp add --transport stdio databricks-demo -- \
  "$(pwd)/.venv/bin/python" "$(pwd)/server.py"
```

---

## Configuration

All settings live in **`config.py`**:

```python
# Databricks
DATABRICKS_HOST        = "https://your-workspace.cloud.databricks.com"
SQL_WAREHOUSE_ID       = "abc123def456"
MODEL_SERVING_ENDPOINT = "my-llm-endpoint"

# Lakebase
LAKEBASE_HOST     = "your-lakebase-host.cloud.databricks.com"
LAKEBASE_USER     = "you@company.com"
LAKEBASE_PORT     = 5432
LAKEBASE_DATABASE = "my_database"

# Vita API (replace PLACEHOLDERs to activate)
VITA_API_BASE_URL      = "https://your-api-host/api/compagnie"
VITA_API_TOKEN         = "your-jwt-token"
VITA_DEFAULT_COMPAGNIA = "your-company-code"
```

Vita tools return a clear error until placeholders are replaced — all other tools work independently.

---

## Project structure

```
├── server.py              # Entrypoint — creates MCP server, registers domains
├── config.py              # All configuration
├── tools/
│   ├── sql.py             # SQL Warehouse queries
│   ├── lakebase.py        # Lakebase read/write
│   ├── models.py          # Model Serving inference
│   ├── external_apis.py   # Weather and external REST APIs
│   └── vita_api.py        # Vita insurance policy API
└── requirements.txt
```

---

## Adding a new domain

1. Create `tools/my_domain.py`:

```python
import json

def register(mcp, w):
    @mcp.tool()
    def my_tool(param: str) -> str:
        """One-line description shown to Claude.

        Args:
            param: What this parameter does.
        """
        return json.dumps({"data": "result"})
```

2. Register it in `server.py`:

```python
from tools import my_domain
my_domain.register(mcp, w)
```

3. Restart Claude Code or re-run `/mcp`.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "No Authorization header" | Run `databricks auth login --host ...` |
| SQL timeout | Increase `wait_timeout` or check warehouse is running |
| Lakebase connection refused | Verify `LAKEBASE_HOST` and IP allowlist |
| Model 404 | Check `MODEL_SERVING_ENDPOINT` name matches exactly |
| Vita "not configured" error | Replace `PLACEHOLDER` values in `config.py` |
| MCP not showing in Claude | Run `claude mcp list` to verify registration |
