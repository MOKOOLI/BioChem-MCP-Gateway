import asyncio

from app.services.databases.alphafold_client import AlphaFoldClient


async def main():
    async with AlphaFoldClient() as client:
        for acc in ["P00533", "P04637", "O00506"]:
            print(f"\n=== {acc} ===")
            info = await client.get_structure_info(acc)
            if not info:
                print("  NOT FOUND")
                continue
            print(f"  Source:        {info['source']}")
            print(f"  AlphaFold URL: {info['alphafold_url']}")
            print(f"  PDBe entries:  {len(info['pdbe_structures'])}")
            for s in info["pdbe_structures"][:2]:
                print(f"    - {s['pdb_id']} | {s['method']} | res={s['resolution']} | cov={s['coverage']}")


if __name__ == "__main__":
    asyncio.run(main())