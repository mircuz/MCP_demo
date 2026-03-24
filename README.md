# Databricks MCP Server

A lightweight MCP (Model Context Protocol) server that exposes three Databricks
capabilities as tools for Claude Code:

| Tool | Backend | Use case |
|------|---------|----------|
| `execute_sql` | SQL Warehouse (DBSQL) | Analytics queries, catalog browsing |
| `query_lakebase` | Lakebase (Postgres) | Transactional data, app backends |
| `invoke_model` | Model Serving | LLM/ML inference |

---

## Prerequisites

1. **Python 3.10+**
2. **Databricks CLI** — for OAuth authentication
3. **Claude Code** — to consume the MCP server

---

## Setup

### 1. Install dependencies

```bash
cd MCP_demo
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Authenticate with Databricks (OAuth U2M)

```bash
databricks auth login --host https://YOUR-WORKSPACE.cloud.databricks.com
```

This caches OAuth tokens locally. The SDK picks them up automatically — no
tokens in code or env vars.

### 3. Edit configuration

Open `server.py` and fill in the top section:

```python
DATABRICKS_HOST        = "https://your-workspace.cloud.databricks.com"
SQL_WAREHOUSE_ID       = "abc123def456"
LAKEBASE_HOST          = "your-lakebase-host.cloud.databricks.com"
LAKEBASE_PORT          = 5432
LAKEBASE_DATABASE      = "my_database"
MODEL_SERVING_ENDPOINT = "my-llm-endpoint"
```

### 4. Register the MCP server in Claude Code

```bash
claude mcp add --transport stdio databricks-demo -- \
  /path/to/MCP_demo/.venv/bin/python /path/to/MCP_demo/server.py
```

Or for the current directory:

```bash
claude mcp add --transport stdio databricks-demo -- \
  "$(pwd)/.venv/bin/python" "$(pwd)/server.py"
```

### 5. Verify

Inside Claude Code, run `/mcp` to confirm the server is connected and the three
tools are visible.

---

## Usage examples

Once registered, just ask Claude naturally:

- *"Show me the top 10 tables in the main catalog"*
  → Claude calls `execute_sql`
- *"Query the users table in Lakebase"*
  → Claude calls `query_lakebase`
- *"Summarize this text using the serving endpoint"*
  → Claude calls `invoke_model`

---

## Extending the server

Adding a new tool is a three-step process:

### 1. Write the function

```python
@mcp.tool()
def my_new_tool(param: str, count: int = 10) -> str:
    """One-line description shown to Claude.

    Args:
        param: What this parameter does.
        count: How many results to return.
    """
    # Your logic here — use `w` (WorkspaceClient) for Databricks APIs
    result = w.some_api.some_method(param)
    return json.dumps({"data": result})
```

### 2. Add any new dependencies to `requirements.txt`

### 3. Restart Claude Code (or re-run `/mcp`)

That's it. The MCP SDK discovers `@mcp.tool()` decorated functions automatically.

### Extension ideas

| Tool idea | Databricks API | SDK method |
|-----------|---------------|------------|
| List jobs / trigger a run | Jobs API | `w.jobs.list()`, `w.jobs.run_now()` |
| Read a notebook | Workspace API | `w.workspace.export()` |
| Manage clusters | Clusters API | `w.clusters.list()` |
| Search Unity Catalog | UC API | `w.tables.list()`, `w.schemas.list()` |
| Query a Vector Search index | Vector Search API | `w.vector_search_indexes.query()` |
| Read DBFS files | DBFS API | `w.dbfs.read()` |

The full Databricks SDK reference:
https://databricks-sdk-py.readthedocs.io/

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "No Authorization header" | Run `databricks auth login --host ...` |
| SQL timeout | Increase `wait_timeout` in `execute_sql` or check warehouse is running |
| Lakebase connection refused | Verify `LAKEBASE_HOST` and that your IP is allowed |
| Model 404 | Check `MODEL_SERVING_ENDPOINT` matches the endpoint name (not URL) |
| MCP not showing in Claude | Run `claude mcp list` to verify registration |
