from pydantic import BaseModel, Field


class RheaReaction(BaseModel):
    rhea_id: str = Field(..., description="Rhea reaction ID, e.g. RHEA:10000")
    equation: str = Field(..., description="Reaction equation")
    ec_number: str | None = Field(None, description="EC number if available")
    chebi_ids: list[str] = Field(default_factory=list, description="ChEBI IDs involved")
    status: str | None = Field(None, description="Status, e.g. approved")
    direction: str | None = Field(None, description="Direction, e.g. LR, RL, etc.")


class ChebiCompound(BaseModel):
    chebi_id: str = Field(..., description="e.g. CHEBI:15365")
    label: str = Field(..., description="Preferred name")
    description: str | None = None
    smiles: str | None = None
    formula: str | None = None
    mass: float | None = None
    monoisotopic_mass: float | None = None
    charge: float | None = None
    inchi: str | None = None
    inchi_key: str | None = None
    synonyms: list[str] = Field(default_factory=list)
    xrefs: dict[str, list[str]] = Field(default_factory=dict)
    is_obsolete: bool = False
class UniProtProtein(BaseModel):
    accession: str = Field(..., description="e.g. P00533")
    uniprot_id: str | None = Field(None, description="e.g. EGFR_HUMAN")
    protein_name: str | None = None
    gene_name: str | None = None
    gene_synonyms: list[str] = Field(default_factory=list)
    organism: str | None = None
    taxon_id: int | None = None
    ec_numbers: list[str] = Field(default_factory=list)
    sequence_length: int | None = None
    sequence_mass: int | None = None
    sequence: str | None = None
    reviewed: bool = False