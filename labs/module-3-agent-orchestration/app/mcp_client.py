from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def inspect_account(account_id: str) -> dict:
    """Exercise a real MCP initialize/list/call lifecycle over stdio."""
    env = os.environ.copy()
    root = Path(__file__).resolve().parent.parent
    env.setdefault("CUSTOMER_SUCCESS_DB", str(root / "customer_success.db"))
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "app.mcp_server"], env=env, cwd=root
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            tools = await session.list_tools()
            customer = await session.call_tool("get_customer", {"account_id": account_id})
            return {
                "transport": "stdio",
                "tools": sorted(t.name for t in tools.tools),
                "customer": json.loads(customer.content[0].text),
            }


if __name__ == "__main__":
    print(json.dumps(asyncio.run(inspect_account("ACME-001")), indent=2))
