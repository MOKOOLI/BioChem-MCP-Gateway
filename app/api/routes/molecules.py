from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.cheminformatics.rdkit_service import RDKitService

router = APIRouter(prefix="/api/molecules", tags=["molecules"])


class AnalyzeRequest(BaseModel):
    smiles: str


class SimilarityRequest(BaseModel):
    smiles_a: str
    smiles_b: str


@router.post("/analyze")
async def analyze_molecule(req: AnalyzeRequest):
    canonical = RDKitService.to_canonical_smiles(req.smiles)
    if canonical is None:
        raise HTTPException(400, f"Invalid SMILES: {req.smiles}")
    dl = RDKitService.compute_drug_likeness(req.smiles)
    return {
        "input_smiles": req.smiles,
        "canonical_smiles": canonical,
        "drug_likeness": RDKitService.to_dict(dl) if dl else None,
    }


@router.post("/similarity")
async def similarity(req: SimilarityRequest):
    score = RDKitService.similarity(req.smiles_a, req.smiles_b)
    return {
        "smiles_a": req.smiles_a,
        "smiles_b": req.smiles_b,
        "tanimoto": score,
    }