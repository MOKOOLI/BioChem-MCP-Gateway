"""
Quick test: directly invoke MCP tool handlers (bypassing stdio transport).
"""
import asyncio
import json

from app.mcp_server.server import HANDLERS


async def main():
    tests = [
        ("search_rhea_reactions", {"query": "glucose", "limit": 2}),
        ("get_chebi_compound", {"chebi_id": "CHEBI:15365"}),
        ("search_uniprot_by_ec", {"ec_number": "2.7.11.1", "organism_id": 9606, "limit": 2}),
        ("get_structure", {"uniprot_accession": "P00533"}),
        ("analyze_molecule", {"smiles": "CC(=O)Oc1ccccc1C(=O)O"}),
        ("compute_similarity", {
            "smiles_a": "CC(=O)Oc1ccccc1C(=O)O",
            "smiles_b": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
        }),
    ]

    for name, args in tests:
        print(f"\n{'='*60}")
        print(f"TOOL: {name}  args={args}")
        print("=" * 60)
        try:
            result = await HANDLERS[name](args)
            text = json.dumps(result, indent=2, ensure_ascii=False)
            print(text[:800])
            if len(text) > 800:
                print(f"... ({len(text) - 800} more chars)")
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())