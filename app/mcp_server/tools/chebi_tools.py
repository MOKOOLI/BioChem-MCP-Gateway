from loguru import logger

from app.services.databases.chebi_client import ChebiClient
from app.services.cheminformatics.rdkit_service import RDKitService


async def handle_get_chebi_compound(args: dict) -> dict:
    """Handler for `get_chebi_compound` tool."""
    chebi_id = args["chebi_id"]
    include_dl = bool(args.get("include_druglikeness", True))

    async with ChebiClient() as client:
        compound = await client.get_compound(chebi_id)

    if compound is None:
        return {"error": f"ChEBI compound '{chebi_id}' not found"}

    result = compound.model_dump()

    if include_dl and compound.smiles:
        dl = RDKitService.compute_drug_likeness(compound.smiles)
        if dl:
            result["drug_likeness"] = RDKitService.to_dict(dl)

    return result