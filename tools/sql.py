"""SQL Warehouse tools — analytics queries on Databricks."""

from __future__ import annotations

import json
from databricks.sdk.service.sql import StatementParameterListItem
from config import SQL_WAREHOUSE_ID


def register(mcp, w):
    """Register SQL-related tools with the MCP server."""

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
                StatementParameterListItem(
                    name="min_score",
                    value=str(min_sentiment_score),
                    type="DOUBLE",
                ),
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
