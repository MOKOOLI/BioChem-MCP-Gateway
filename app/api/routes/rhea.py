from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.databases.rhea_client import RheaClient

router = APIRouter(prefix="/api/rhea", tags=["rhea"])


class RheaReactionOut(BaseModel):
    rhea_id: str
    equation: str
    ec_number: str | None
    chebi_ids: list[str]


class RheaSearchResponse(BaseModel):
    query: str
    count: int
    reactions: list[RheaReactionOut]


@router.get("/search", response_model=RheaSearchResponse)
async def search_rhea(
    q: str = Query(..., description="Search keyword"),
    limit: int = Query(10, ge=1, le=50),
):
    async with RheaClient() as client:
        reactions = await client.search_reactions(q, limit=limit)
    return RheaSearchResponse(
        query=q,
        count=len(reactions),
        reactions=[RheaReactionOut(**r.model_dump()) for r in reactions],
    )


@router.get("/{rhea_id}", response_model=RheaReactionOut)
async def get_rhea_reaction(rhea_id: str):
    async with RheaClient() as client:
        reaction = await client.get_reaction(rhea_id)
    if reaction is None:
        raise HTTPException(404, f"Rhea reaction '{rhea_id}' not found")
    return RheaReactionOut(**reaction.model_dump())