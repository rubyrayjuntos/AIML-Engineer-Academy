from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from app.sql_store import AnalyticsStore
from app.store import Store

mcp = FastMCP("academy-readonly-tools")
DB_PATH = Path(os.environ.get("CUSTOMER_SUCCESS_DB", "customer_success.db"))
ANALYTICS_DB_PATH = Path(os.environ.get("ANALYTICS_DB", "analytics.db"))


def _store() -> Store:
    store = Store(DB_PATH)
    store.initialize()
    return store


def _analytics() -> AnalyticsStore:
    store = AnalyticsStore(ANALYTICS_DB_PATH)
    store.initialize()
    store.seed()
    return store


@mcp.tool()
def get_customer(account_id: str) -> str:
    """Read one customer account. This tool cannot mutate customer data."""
    customer = _store().customer(account_id)
    return json.dumps(customer or {"error": "not_found"}, sort_keys=True)


@mcp.tool()
def search_interactions(account_id: str, query: str, limit: int = 3) -> str:
    """Retrieve cited interactions for one account (limit 1..10)."""
    return json.dumps(_store().search(account_id, query, limit), sort_keys=True)


@mcp.tool()
def get_table_schema(table_name: str) -> str:
    """Return DDL for one analytics table (users or orders). Read-only."""
    try:
        return _analytics().schema_for(table_name)
    except ValueError as exc:
        return json.dumps({"error": str(exc)})


@mcp.tool()
def execute_readonly_sql(sql: str) -> str:
    """Execute a single read-only SELECT/WITH against the analytics SQLite DB."""
    try:
        rows = _analytics().execute_readonly(sql)
        return json.dumps({"rows": rows}, sort_keys=True)
    except Exception as exc:  # noqa: BLE001 - surface firewall errors to the client
        return json.dumps({"error": str(exc)}, sort_keys=True)


if __name__ == "__main__":
    mcp.run(transport="stdio")
