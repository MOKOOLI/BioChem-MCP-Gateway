import asyncio
from app.services.databases.uniprot_client import UniProtClient


async def main():
    async with UniProtClient() as client:
        print("=== Search EC:2.7.11.1 in human ===")
        proteins = await client.search_by_ec("2.7.11.1", organism_id=9606, limit=5)
        for p in proteins:
            print(f"  {p.accession} | {p.uniprot_id} | {p.protein_name[:50]} | len={p.sequence_length}")

        print("\n=== Details: P00533 (EGFR) ===")
        egfr = await client.get_protein("P00533")
        if egfr:
            print(f"  Accession:  {egfr.accession}")
            print(f"  UniProt ID: {egfr.uniprot_id}")
            print(f"  Name:       {egfr.protein_name}")
            print(f"  Gene:       {egfr.gene_name}")
            print(f"  Organism:   {egfr.organism} (taxon {egfr.taxon_id})")
            print(f"  EC:         {egfr.ec_numbers}")
            print(f"  Length:     {egfr.sequence_length}")
            print(f"  Mass:       {egfr.sequence_mass} Da")
            print(f"  Reviewed:   {egfr.reviewed}")

        print("\n=== Details: P04637 (p53) ===")
        p53 = await client.get_protein("P04637")
        if p53:
            print(f"  {p53.accession} | {p53.protein_name} | gene={p53.gene_name}")


if __name__ == "__main__":
    asyncio.run(main())