"""Lakebase (Postgres-wire) tools — transactional queries and writes."""

from __future__ import annotations

import json
from config import LAKEBASE_HOST, LAKEBASE_USER, LAKEBASE_PORT, LAKEBASE_DATABASE

LAKEBASE_WRITE_TABLE = "api_payloads"


def _connect(token: str):
    """Return a psycopg2 connection to Lakebase."""
    import psycopg2

    return psycopg2.connect(
        host=LAKEBASE_HOST,
        port=LAKEBASE_PORT,
        database=LAKEBASE_DATABASE,
        user=LAKEBASE_USER,
        password=token,
        sslmode="require",
    )


def register(mcp, w):
    """Register Lakebase-related tools with the MCP server."""

    from server import get_oauth_token  # deferred to avoid circular import

    @mcp.tool()
    def query_lakebase(query: str) -> str:
        """Execute a SQL query on the Lakebase Postgres instance.

        Args:
            query: A standard PostgreSQL query.
        """
        token = get_oauth_token()
        conn = _connect(token)
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

    @mcp.tool()
    def write_to_lakebase(payload: str, table_name: str = LAKEBASE_WRITE_TABLE) -> str:
        """Write a JSON payload into a Lakebase Postgres table.

        The target table is created automatically if it does not exist.
        Each row stores the raw JSON payload and an ingestion timestamp.

        Args:
            payload:    A JSON string to persist (e.g. output of fetch_weather).
            table_name: Destination table name (default 'api_payloads').
        """
        try:
            json.loads(payload)
        except json.JSONDecodeError as exc:
            return json.dumps({"error": f"Invalid JSON payload: {exc}"})

        token = get_oauth_token()
        conn = _connect(token)
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id          SERIAL PRIMARY KEY,
                        ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                        payload     JSONB       NOT NULL
                    )
                """)
                conn.commit()

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
