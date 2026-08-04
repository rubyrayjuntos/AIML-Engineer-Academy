from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from app.store import Store

mcp = FastMCP("customer-success-readonly")
DB_PATH = Path(os.environ.get("CUSTOMER_SUCCESS_DB", "customer_success.db"))


def _store() -> Store:
    store = Store(DB_PATH)
    store.initialize()
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


if __name__ == "__main__":
    mcp.run(transport="stdio")
