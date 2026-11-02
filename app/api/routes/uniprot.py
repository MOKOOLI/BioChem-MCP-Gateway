from fastapi import APIRouter, HTTPException, Query

from app.services.databases.uniprot_client import UniProtClient

router = APIRouter(prefix="/api/uniprot", tags=["uniprot"])


@router.get("/search")
async def search_uniprot(
    ec: str | None = Query(None, description="EC number, e.g. '2.7.11.1'"),
    organism_id: int | None = Query(None, description="NCBI taxon ID"),
    limit: int = Query(10, ge=1, le=50),
):
    if not ec:
        raise HTTPException(400, "'ec' parameter is required")
    async with UniProtClient() as client:
        proteins = await client.search_by_ec(ec, organism_id=organism_id, limit=limit)
    return {
        "ec_number": ec,
        "organism_id": organism_id,
        "count": len(proteins),
        "proteins": [p.model_dump() for p in proteins],
    }


@router.get("/{accession}")
async def get_uniprot_protein(accession: str):
    async with UniProtClient() as client:
        protein = await client.get_protein(accession)
    if protein is None:
        raise HTTPException(404, f"UniProt accession '{accession}' not found")
    return protein.model_dump()