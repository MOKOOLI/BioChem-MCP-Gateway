from app.services.databases.uniprot_client import UniProtClient


async def handle_search_uniprot_by_ec(args: dict) -> dict:
    """Handler for `search_uniprot_by_ec` tool."""
    ec_number = args["ec_number"]
    organism_id = args.get("organism_id")
    limit = int(args.get("limit", 10))

    async with UniProtClient() as client:
        proteins = await client.search_by_ec(
            ec_number=ec_number,
            organism_id=organism_id,
            limit=limit,
        )

    return {
        "ec_number": ec_number,
        "organism_id": organism_id,
        "count": len(proteins),
        "proteins": [p.model_dump() for p in proteins],
    }