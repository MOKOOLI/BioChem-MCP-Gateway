import asyncio
from app.services.databases.rhea_client import RheaClient


async def main():
    async with RheaClient() as client:
        print("Searching Rhea for 'glucose'...")
        reactions = await client.search_reactions("glucose", limit=5)
        print(f"Found {len(reactions)} reactions\n")
        for r in reactions:
            print(f"  {r.rhea_id} | EC={r.ec_number} | {r.equation[:80]}")


if __name__ == "__main__":
    asyncio.run(main())