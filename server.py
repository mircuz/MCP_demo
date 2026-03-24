#!/usr/bin/env python3
"""
Databricks MCP Server
=====================
A Model Context Protocol server exposing Databricks capabilities:
  1. execute_sql       — Run queries on a Databricks SQL Warehouse
  2. query_lakebase    — Run queries on a Lakebase (Postgres) instance
  3. invoke_model      — Call a Model Serving endpoint
  4. get_high_sentiment_articles — Query financial sentiment data
  5. fetch_weather     — Fetch live weather from Open-Meteo REST API
  6. write_to_lakebase — Persist a JSON payload into a Lakebase table

Auth: Databricks SDK OAuth (U2M) — run `databricks auth login` first.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementParameterListItem

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CONFIGURATION — edit these values for your workspace
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATABRICKS_HOST        = "https://e2-demo-field-eng.cloud.databricks.com"
SQL_WAREHOUSE_ID       = "4b9b953939869799"
LAKEBASE_HOST          = "ep-polished-cloud-d1w1d99q.database.us-west-2.cloud.databricks.com"
LAKEBASE_USER          = "mirco.meazzo@databricks.com"
LAKEBASE_PORT          = 5432
LAKEBASE_DATABASE      = "databricks_postgres"
MODEL_SERVING_ENDPOINT = "databricks-gpt-5-mini"
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ---------------------------------------------------------------------------
#  MCP Server & Databricks client
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "databricks-demo",
    instructions=(
        "Databricks assistant. Use execute_sql for analytics queries, "
        "query_lakebase for transactional/Postgres data, and invoke_model "
        "to call LLMs or ML models hosted on Databricks."
    ),
)

w = WorkspaceClient(host=DATABRICKS_HOST)


def _get_oauth_token() -> str:
    """Extract the current OAuth access token from the Databricks SDK."""
    result = w.config.authenticate()
    # SDK may return a callable (header factory) or a dict directly
    headers = result() if callable(result) else result
    auth = headers.get("Authorization", "")
    if not auth:
        raise RuntimeError(
            "No Authorization header — have you run `databricks auth login`?"
        )
    return auth.removeprefix("Bearer ")


# ---------------------------------------------------------------------------
#  Tool 1 — Databricks SQL Warehouse
# ---------------------------------------------------------------------------
@mcp.tool()
def execute_sql(query: str, max_rows: int = 100) -> str:
    """Execute a SQL query on the Databricks SQL Warehouse.

    Args:
        query: The SQL statement to run (SELECT, SHOW, DESCRIBE, etc.).
        max_rows: Maximum number of rows to return (default 100).
    """
    result = w.statement_execution.execute_statement(
        warehouse_id=SQL_WAREHOUSE_ID,
        statement=query,
        row_limit=max_rows,
        wait_timeout="30s",
    )

    if result.status and result.status.error:
        return json.dumps({"error": result.status.error.message})

    columns = [c.name for c in result.manifest.schema.columns]
    rows = result.result.data_array or []

    return json.dumps(
        {"columns": columns, "rows": rows, "row_count": len(rows)},
        indent=2,
    )


# ---------------------------------------------------------------------------
#  Tool 2 — Lakebase (Postgres-wire compatible)
# ---------------------------------------------------------------------------
@mcp.tool()
def query_lakebase(query: str) -> str:
    """Execute a SQL query on the Lakebase Postgres instance.

    Args:
        query: A standard PostgreSQL query.
    """
    import psycopg2  # imported here to keep it optional

    token = _get_oauth_token()

    conn = psycopg2.connect(
        host=LAKEBASE_HOST,
        port=LAKEBASE_PORT,
        database=LAKEBASE_DATABASE,
        user=LAKEBASE_USER,
        password=token,
        sslmode="require",
    )
    try:
        with conn.cursor() as cur:
            cur.execute(query)

            if cur.description:  # SELECT-like query
                columns = [desc[0] for desc in cur.description]
                rows = [[str(v) for v in row] for row in cur.fetchall()]
                return json.dumps(
                    {"columns": columns, "rows": rows, "row_count": len(rows)},
                    indent=2,
                )

            conn.commit()  # DML (INSERT/UPDATE/DELETE)
            return json.dumps({"status": "ok", "rows_affected": cur.rowcount})
    finally:
        conn.close()


# ---------------------------------------------------------------------------
#  Tool 3 — Model Serving
# ---------------------------------------------------------------------------
@mcp.tool()
def invoke_model(prompt: str, max_tokens: int = 512) -> str:
    """Send a prompt to a model hosted on Databricks Model Serving.

    Args:
        prompt: The user message to send to the model.
        max_tokens: Maximum tokens in the response (default 512).
    """
    response = w.serving_endpoints.query(
        name=MODEL_SERVING_ENDPOINT,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
#  Tool 4 — Financial Sentiment Analysis
# ---------------------------------------------------------------------------
@mcp.tool()
def get_high_sentiment_articles(min_sentiment_score: float) -> str:
    """Return the last 10 news articles with sentiment_score >= the given threshold.

    Queries mircom_test.financial_sentiment.news_articles_analyzed and returns
    scrape_timestamp, analyzed_at, and sentiment for matching rows, ordered by
    most recent first.

    Args:
        min_sentiment_score: Minimum sentiment score (inclusive) to filter on.
    """
    query = (
        "SELECT title, source, scrape_timestamp, analyzed_at, sentiment "
        "FROM mircom_test.financial_sentiment.news_articles_analyzed "
        "WHERE sentiment_score >= :min_score "
        "ORDER BY scrape_timestamp DESC "
        "LIMIT 10"
    )

    result = w.statement_execution.execute_statement(
        warehouse_id=SQL_WAREHOUSE_ID,
        statement=query,
        parameters=[
            StatementParameterListItem(name="min_score", value=str(min_sentiment_score), type="DOUBLE"),
        ],
        wait_timeout="30s",
    )

    if result.status and result.status.error:
        return json.dumps({"error": result.status.error.message})

    columns = [c.name for c in result.manifest.schema.columns]
    rows = result.result.data_array or []

    return json.dumps(
        {"columns": columns, "rows": rows, "row_count": len(rows)},
        indent=2,
    )


# ---------------------------------------------------------------------------
#  Tool 5 — Fetch Weather from Open-Meteo REST API
# ---------------------------------------------------------------------------
@mcp.tool()
def fetch_weather(latitude: float = 45.4642, longitude: float = 9.1900) -> str:
    """Fetch current weather data from the Open-Meteo API for a given location.

    Returns temperature, wind speed, humidity, and conditions with a UTC
    timestamp. Defaults to Milan, Italy.

    Args:
        latitude:  Latitude of the location (default 45.4642 — Milan).
        longitude: Longitude of the location (default 9.1900 — Milan).
    """
    import urllib.request

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,relative_humidity_2m,"
        f"wind_speed_10m,weather_code"
        f"&timezone=auto"
    )

    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode())

    current = data.get("current", {})
    units = data.get("current_units", {})

    payload = {
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "timezone": data.get("timezone"),
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "temperature": f"{current.get('temperature_2m')} {units.get('temperature_2m', '')}",
        "relative_humidity": f"{current.get('relative_humidity_2m')} {units.get('relative_humidity_2m', '')}",
        "wind_speed": f"{current.get('wind_speed_10m')} {units.get('wind_speed_10m', '')}",
        "weather_code": current.get("weather_code"),
        "observation_time": current.get("time"),
    }
    return json.dumps(payload, indent=2)


# ---------------------------------------------------------------------------
#  Tool 6 — Write a JSON payload into a Lakebase table
# ---------------------------------------------------------------------------
LAKEBASE_WRITE_TABLE = "api_payloads"


@mcp.tool()
def write_to_lakebase(payload: str, table_name: str = LAKEBASE_WRITE_TABLE) -> str:
    """Write a JSON payload into a Lakebase Postgres table.

    The target table is created automatically if it does not exist.
    Each row stores the raw JSON payload and an ingestion timestamp.

    Args:
        payload:    A JSON string to persist (e.g. output of fetch_weather).
        table_name: Destination table name (default 'api_payloads').
    """
    import psycopg2

    # Validate that payload is valid JSON
    try:
        json.loads(payload)
    except json.JSONDecodeError as exc:
        return json.dumps({"error": f"Invalid JSON payload: {exc}"})

    token = _get_oauth_token()
    conn = psycopg2.connect(
        host=LAKEBASE_HOST,
        port=LAKEBASE_PORT,
        database=LAKEBASE_DATABASE,
        user=LAKEBASE_USER,
        password=token,
        sslmode="require",
    )
    try:
        with conn.cursor() as cur:
            # Create table if it doesn't exist
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id          SERIAL PRIMARY KEY,
                    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    payload     JSONB       NOT NULL
                )
            """)
            conn.commit()

            # Insert the payload
            cur.execute(
                f"INSERT INTO {table_name} (payload) VALUES (%s) RETURNING id, ingested_at",
                (payload,),
            )
            row = cur.fetchone()
            conn.commit()

        return json.dumps({
            "status": "ok",
            "table": table_name,
            "id": row[0],
            "ingested_at": row[1].isoformat(),
        })
    finally:
        conn.close()


# ---------------------------------------------------------------------------
#  Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
