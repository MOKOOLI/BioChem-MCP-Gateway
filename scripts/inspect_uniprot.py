import asyncio
import httpx
import json


async def main():
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": "ec:2.7.11.1 AND organism_id:9606",  # human
        "format": "json",
        "size": "3",
        "fields": "accession,id,protein_name,gene_names,organism_name,ec,sequence",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        print("Status:", r.status_code)
        data = r.json()
        results = data.get("results", [])
        print(f"Total: {len(results)}\n")
        for i, entry in enumerate(results[:2], 1):
            print(f"--- Entry {i} ---")
            print(json.dumps(entry, indent=2)[:2500])
            print()


if __name__ == "__main__":
    asyncio.run(main())