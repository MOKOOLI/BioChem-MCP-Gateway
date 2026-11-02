"""JSON schemas for all MCP tools."""

SEARCH_RHEA_REACTIONS = {
    "name": "search_rhea_reactions",
    "description": (
        "Search Rhea biochemical reactions by keyword (compound name, EC number, ChEBI ID). "
        "Returns reactions with equation, EC numbers, and involved ChEBI names. "
        "Use this when the user asks about enzymatic reactions, metabolic pathways, or how a compound is transformed."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search keyword: compound name (e.g. 'glucose'), EC number (e.g. '2.7.11.1'), or 'chebi:4167'",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of reactions to return (default 10)",
                "default": 10,
                "minimum": 1,
                "maximum": 50,
            },
        },
        "required": ["query"],
    },
}


GET_CHEBI_COMPOUND = {
    "name": "get_chebi_compound",
    "description": (
        "Fetch detailed information about a ChEBI chemical compound: SMILES, formula, mass, "
        "InChIKey, synonyms, and drug-likeness metrics (Lipinski rules). "
        "Use this when the user asks about a specific chemical substance or wants its properties."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "chebi_id": {
                "type": "string",
                "description": "ChEBI identifier, e.g. 'CHEBI:15365' (aspirin) or 'CHEBI:4167' (glucose). Also accepts plain integers.",
            },
            "include_druglikeness": {
                "type": "boolean",
                "description": "If true (default), compute Lipinski drug-likeness via RDKit",
                "default": True,
            },
        },
        "required": ["chebi_id"],
    },
}


SEARCH_UNIPROT_BY_EC = {
    "name": "search_uniprot_by_ec",
    "description": (
        "Search UniProt proteins by Enzyme Commission (EC) number. "
        "Returns protein accessions, names, genes, organisms, and sequences. "
        "Optionally filter by organism taxon ID (9606=human, 10090=mouse, 559292=yeast)."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "ec_number": {
                "type": "string",
                "description": "EC number without prefix, e.g. '2.7.11.1'",
            },
            "organism_id": {
                "type": "integer",
                "description": "NCBI taxonomy ID to filter by (e.g. 9606 for human). Optional.",
            },
            "limit": {
                "type": "integer",
                "description": "Max results (default 10)",
                "default": 10,
            },
        },
        "required": ["ec_number"],
    },
}


GET_STRUCTURE = {
    "name": "get_structure",
    "description": (
        "Fetch 3D protein structures for a UniProt accession. "
        "Returns top experimental PDB structures from PDBe (best resolution first) "
        "and, when available, an AlphaFold predicted model URL. "
        "Use this when the user asks for 3D structure, docking targets, or visualizations."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "uniprot_accession": {
                "type": "string",
                "description": "UniProt accession, e.g. 'P00533' (EGFR) or 'P04637' (p53)",
            },
            "max_structures": {
                "type": "integer",
                "description": "Maximum number of PDBe structures to return (default 10, best resolution first)",
                "default": 10,
            },
        },
        "required": ["uniprot_accession"],
    },
}


ANALYZE_MOLECULE = {
    "name": "analyze_molecule",
    "description": (
        "Analyze a molecule from SMILES: compute drug-likeness (Lipinski Rule of Five: "
        "MW, LogP, H-bond donors/acceptors), TPSA, rings, and substructure checks. "
        "Use this when the user provides a SMILES string and wants cheminformatics analysis."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "smiles": {
                "type": "string",
                "description": "Valid SMILES string, e.g. 'CC(=O)Oc1ccccc1C(=O)O' (aspirin)",
            },
        },
        "required": ["smiles"],
    },
}


COMPUTE_SIMILARITY = {
    "name": "compute_similarity",
    "description": (
        "Compute Tanimoto similarity between two molecules given their SMILES strings. "
        "Returns a score from 0.0 (no similarity) to 1.0 (identical). "
        "Useful for finding analogs or comparing compounds."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "smiles_a": {"type": "string", "description": "First molecule (SMILES)"},
            "smiles_b": {"type": "string", "description": "Second molecule (SMILES)"},
        },
        "required": ["smiles_a", "smiles_b"],
    },
}


ALL_TOOLS = [
    SEARCH_RHEA_REACTIONS,
    GET_CHEBI_COMPOUND,
    SEARCH_UNIPROT_BY_EC,
    GET_STRUCTURE,
    ANALYZE_MOLECULE,
    COMPUTE_SIMILARITY,
]