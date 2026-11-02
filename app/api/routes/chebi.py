from fastapi import APIRouter, HTTPException, Query

from app.services.databases.chebi_client import ChebiClient
from app.services.cheminformatics.rdkit_service import RDKitService

router = APIRouter(prefix="/api/chebi", tags=["chebi"])


@router.get("/search")
async def search_chebi(
    q: str = Query(..., description="Name / synonym / keyword"),
    limit: int = Query(10, ge=1, le=50),
):
    async with ChebiClient() as client:
        results = await client.search_compounds(q, limit=limit)
    return {"query": q, "count": len(results), "compounds": [c.model_dump() for c in results]}


@router.get("/{chebi_id}")
async def get_chebi(
    chebi_id: str,
    include_druglikeness: bool = Query(True),
):
    async with ChebiClient() as client:
        compound = await client.get_compound(chebi_id)
    if compound is None:
        raise HTTPException(404, f"ChEBI compound '{chebi_id}' not found")

    result = compound.model_dump()
    if include_druglikeness and compound.smiles:
        dl = RDKitService.compute_drug_likeness(compound.smiles)
        if dl:
            result["drug_likeness"] = RDKitService.to_dict(dl)
    return result