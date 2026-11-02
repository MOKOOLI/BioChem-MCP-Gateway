import asyncio
from app.services.databases.chebi_client import ChebiClient


async def main():
    async with ChebiClient() as client:
        print("=== Search 'glucose' ===")
        results = await client.search_compounds("glucose", limit=3)
        for c in results:
            print(f"  {c.chebi_id} | {c.label}")

        print("\n=== Details of aspirin (CHEBI:15365) ===")
        aspirin = await client.get_compound("CHEBI:15365")
        if aspirin:
            print(f"  ID:        {aspirin.chebi_id}")
            print(f"  Label:     {aspirin.label}")
            print(f"  SMILES:    {aspirin.smiles}")
            print(f"  Formula:   {aspirin.formula}")
            print(f"  Mass:      {aspirin.mass}")
            print(f"  InChIKey:  {aspirin.inchi_key}")
            print(f"  Charge:    {aspirin.charge}")
            print(f"  Synonyms:  {len(aspirin.synonyms)} total")
            print(f"  DrugBank:  {aspirin.xrefs.get('drugbank')}")
        else:
            print("  NOT FOUND")

        print("\n=== Details of glucose (CHEBI:4167) ===")
        glucose = await client.get_compound("4167")
        if glucose:
            print(f"  {glucose.chebi_id} | {glucose.label} | SMILES={glucose.smiles}")


if __name__ == "__main__":
    asyncio.run(main())