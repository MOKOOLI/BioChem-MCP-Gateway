import asyncio
import httpx
import json


async def main():
    # Test 1: Search "aspirin" in ChEBI ontology
    url = "https://www.ebi.ac.uk/ols4/api/search"
    params = {
        "q": "aspirin",
        "ontology": "chebi",
        "rows": "3",
    }
    async with httpx.AsyncClient() as client:
        print("=== SEARCH: aspirin ===")
        r = await client.get(url, params=params)
        print("Status:", r.status_code)
        data = r.json()
        print(json.dumps(data, indent=2)[:3000])
        print("\n\n")

        # Test 2: Get details of aspirin (CHEBI:15365)
        print("=== DETAILS: CHEBI:15365 (aspirin) ===")
        url2 = "https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms"
        # OLS4 encodes IRIs: http://purl.obolibrary.org/obo/CHEBI_15365
        iri = "http://purl.obolibrary.org/obo/CHEBI_15365"
        encoded = iri.replace(":", "%3A").replace("/", "%2F")
        r2 = await client.get(f"{url2}/{encoded}")
        print("Status:", r2.status_code)
        print(json.dumps(r2.json(), indent=2)[:3000])


if __name__ == "__main__":
    asyncio.run(main())