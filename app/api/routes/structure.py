from fastapi import APIRouter, HTTPException, Query

from app.services.databases.alphafold_client import AlphaFoldClient

router = APIRouter(prefix="/api/structure", tags=["structure"])


@router.get("/{uniprot_accession}")
async def get_structure(
    uniprot_accession: str,
    max_structures: int = Query(10, ge=1, le=50),
):
    async with AlphaFoldClient() as client:
        info = await client.get_structure_info(uniprot_accession)
    if info is None:
        raise HTTPException(404, f"No structure found for '{uniprot_accession}'")

    pdbe = info.get("pdbe_structures", [])
    pdbe_sorted = sorted(
        [s for s in pdbe if s.get("resolution")],
        key=lambda x: x["resolution"],
    )
    info["pdbe_structures"] = pdbe_sorted[:max_structures]
    info["total_pdbe_count"] = len(pdbe)
    return info