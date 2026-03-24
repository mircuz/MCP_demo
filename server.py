#!/usr/bin/env python3
"""
Databricks MCP Server
=====================
A Model Context Protocol server exposing Databricks capabilities
plus customer-specific API integrations.

Tools are split by domain under the `tools/` package:
  - tools/sql.py           — SQL Warehouse analytics queries
  - tools/lakebase.py      — Lakebase (Postgres-wire) read & write
  - tools/models.py        — Model Serving (LLM / ML inference)
  - tools/external_apis.py — External REST APIs (weather, etc.)
  - tools/vita_api.py      — Vita insurance policy API (customer)

Auth: Databricks SDK OAuth (U2M) — run `databricks auth login` first.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from databricks.sdk import WorkspaceClient
from config import DATABRICKS_HOST

# ---------------------------------------------------------------------------
#  MCP Server & Databricks client
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "databricks-demo",
    instructions=(
        "Databricks assistant. Use execute_sql for analytics queries, "
        "query_lakebase for transactional/Postgres data, invoke_model "
        "to call LLMs or ML models hosted on Databricks, and the "
        "vita_* tools to query life-insurance policies and proposals."
    ),
)

w = WorkspaceClient(host=DATABRICKS_HOST)


def get_oauth_token() -> str:
    """Extract the current OAuth access token from the Databricks SDK."""
    result = w.config.authenticate()
    headers = result() if callable(result) else result
    auth = headers.get("Authorization", "")
    if not auth:
        raise RuntimeError(
            "No Authorization header — have you run `databricks auth login`?"
        )
    return auth.removeprefix("Bearer ")


# ---------------------------------------------------------------------------
#  Register all domain tools
# ---------------------------------------------------------------------------
from tools import sql, lakebase, models, external_apis, vita_api  # noqa: E402

sql.register(mcp, w)
lakebase.register(mcp, w)
models.register(mcp, w)
external_apis.register(mcp, w)
vita_api.register(mcp, w)


# ---------------------------------------------------------------------------
#  Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
