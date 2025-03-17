"""
MySQL MCP Server

A server for interacting with MySQL databases through MCP.
"""

from .server import mcp


def main() -> None:
    """Run the MySQL MCP server"""
    mcp.run()


__all__ = ['mcp', 'main']
