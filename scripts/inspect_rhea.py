import asyncio
import httpx


async def main():
    url = "https://www.rhea-db.org/rhea/"
    params = {
        "query": "glucose",
        "columns": "rhea-id,equation,ec,chebi,status,direction",
        "format": "tsv",
        "limit": "2",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        print("Status:", r.status_code)
        print("--- RAW TSV ---")
        print(r.text[:1500])


if __name__ == "__main__":
    asyncio.run(main())