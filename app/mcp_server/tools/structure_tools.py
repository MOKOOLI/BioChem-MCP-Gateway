from app.services.databases.alphafold_client import AlphaFoldClient


async def handle_get_structure(args: dict) -> dict:
    """Handler for `get_structure` tool."""
    accession = args["uniprot_accession"]
    max_structures = int(args.get("max_structures", 10))

    async with AlphaFoldClient() as client:
        info = await client.get_structure_info(accession)

    if info is None:
        return {"error": f"No structure found for '{accession}'"}

    pdbe = info.get("pdbe_structures", [])
    pdbe_sorted = sorted(
        [s for s in pdbe if s.get("resolution")],
        key=lambda x: x["resolution"],
    )
    info["pdbe_structures"] = pdbe_sorted[:max_structures]
    info["total_pdbe_count"] = len(pdbe)
    return info