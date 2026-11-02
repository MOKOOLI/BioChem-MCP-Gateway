from app.services.cheminformatics.rdkit_service import RDKitService


async def handle_analyze_molecule(args: dict) -> dict:
    """Handler for `analyze_molecule` tool."""
    smiles = args["smiles"]

    canonical = RDKitService.to_canonical_smiles(smiles)
    if canonical is None:
        return {"error": f"Invalid SMILES: {smiles}"}

    dl = RDKitService.compute_drug_likeness(smiles)

    return {
        "input_smiles": smiles,
        "canonical_smiles": canonical,
        "drug_likeness": RDKitService.to_dict(dl) if dl else None,
    }


async def handle_compute_similarity(args: dict) -> dict:
    """Handler for `compute_similarity` tool."""
    a = args["smiles_a"]
    b = args["smiles_b"]

    score = RDKitService.similarity(a, b)

    return {
        "smiles_a": a,
        "smiles_b": b,
        "tanimoto": score,
        "interpretation": _interpret_similarity(score),
    }


def _interpret_similarity(score: float) -> str:
    if score >= 0.85:
        return "Very high similarity (likely same scaffold)"
    if score >= 0.6:
        return "High similarity (likely analog)"
    if score >= 0.3:
        return "Moderate similarity (related compounds)"
    return "Low similarity (different chemotypes)"