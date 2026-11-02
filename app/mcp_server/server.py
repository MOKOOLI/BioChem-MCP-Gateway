"""
BioChem MCP Server — exposes biochemical tools to AI agents via Model Context Protocol.
"""
import json
from typing import Any

from loguru import logger
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from app.mcp_server.schemas import ALL_TOOLS
from app.mcp_server.tools.rhea_tools import handle_search_rhea_reactions
from app.mcp_server.tools.chebi_tools import handle_get_chebi_compound
from app.mcp_server.tools.uniprot_tools import handle_search_uniprot_by_ec
from app.mcp_server.tools.structure_tools import handle_get_structure
from app.mcp_server.tools.rdkit_tools import (
    handle_analyze_molecule,
    handle_compute_similarity,
)


app = Server("biochem-mcp-gateway")

# Map tool name → async handler
HANDLERS = {
    "search_rhea_reactions": handle_search_rhea_reactions,
    "get_chebi_compound": handle_get_chebi_compound,
    "search_uniprot_by_ec": handle_search_uniprot_by_ec,
    "get_structure": handle_get_structure,
    "analyze_molecule": handle_analyze_molecule,
    "compute_similarity": handle_compute_similarity,
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return all available tools."""
    return [
        Tool(name=t["name"], description=t["description"], inputSchema=t["inputSchema"])
        for t in ALL_TOOLS
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Dispatch tool call to the appropriate handler."""
    if name not in HANDLERS:
        raise ValueError(f"Unknown tool: {name}")

    logger.info(f"MCP tool call: {name} args={arguments}")
    handler = HANDLERS[name]
    result = await handler(arguments or {})

    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def run_stdio():
    """Run MCP server over stdio (for Claude Desktop, etc.)."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_stdio())