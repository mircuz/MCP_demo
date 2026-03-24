"""
Tool domain modules for the Databricks MCP Server.

Each module registers its own @mcp.tool() functions via a `register(mcp, w)` call.
To add a new domain, create a new file in this package and call its register()
function from server.py.
"""
