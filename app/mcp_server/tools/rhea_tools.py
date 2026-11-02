from loguru import logger

from app.services.databases.rhea_client import RheaClient


async def handle_search_rhea_reactions(args: dict) -> dict:
    """Handler for `search_rhea_reactions` tool."""
    query = args["query"]
    limit = int(args.get("limit", 10))

    async with RheaClient() as client:
        reactions = await client.search_reactions(query, limit=limit)

    return {
        "query": query,
        "count": len(reactions),
        "reactions": [r.model_dump() for r in reactions],
    }