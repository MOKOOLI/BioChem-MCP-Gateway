import asyncio
import httpx


async def main():
    async with httpx.AsyncClient(timeout=60) as client:
        # Test 1: metadata API
        print("=== Metadata: P00533 (EGFR) ===")
        r = await client.get("https://alphafold.ebi.ac.uk/api/prediction/P00533")
        print("Status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                entry = data[0]
                for key in ["uniprotAccession", "uniprotId", "entryId",
                            "pdbUrl", "cifUrl", "latestVersion",
                            "plddtDocUrl", "sequenceStart", "sequenceEnd"]:
                    print(f"  {key}: {entry.get(key)}")
        else:
            print("  Response:", r.text[:300])

        # Test 2: HEAD on PDB URL
        print("\n=== PDB file HEAD: P00533 ===")
        pdb_url = "https://alphafold.ebi.ac.uk/files/AF-P00533-F1-model_v4.pdb"
        r2 = await client.head(pdb_url)
        print(f"  Status: {r2.status_code}")
        print(f"  Content-Length: {r2.headers.get('content-length')} bytes")
        print(f"  Content-Type: {r2.headers.get('content-type')}")


if __name__ == "__main__":
    asyncio.run(main())