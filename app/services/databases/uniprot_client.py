from loguru import logger

from app.core.config import settings
from app.services.databases.base_client import BaseHTTPClient
from app.services.databases.models import UniProtProtein


class UniProtClient(BaseHTTPClient):
    """
    UniProt REST API client.

    Docs: https://www.uniprot.org/help/api
    Search: /uniprotkb/search?query=...&format=json
    Entry:  /uniprotkb/{accession}.json
    """

    def __init__(self):
        super().__init__(base_url=settings.UNIPROT_BASE_URL)

    async def search_by_ec(
        self,
        ec_number: str,
        organism_id: int | None = None,
        limit: int = 10,
        reviewed_only: bool = True,
    ) -> list[UniProtProtein]:
        """
        Search proteins by EC number.

        Args:
            ec_number: e.g. "2.7.11.1"
            organism_id: NCBI taxon ID, e.g. 9606 for human
            limit: max results
            reviewed_only: only Swiss-Prot (reviewed) entries
        """
        query_parts = [f"ec:{ec_number}"]
        if organism_id:
            query_parts.append(f"organism_id:{organism_id}")
        if reviewed_only:
            query_parts.append("reviewed:true")
        query = " AND ".join(query_parts)

        params = {
            "query": query,
            "format": "json",
            "size": str(limit),
            "fields": "accession,id,protein_name,gene_names,organism_name,ec,sequence",
        }
        response = await self.get("/uniprotkb/search", params=params)
        data = response.json()
        results = data.get("results", [])
        logger.debug(f"UniProt search ec:{ec_number} → {len(results)} results")
        return [self._parse_entry(e) for e in results]

    async def get_protein(self, accession: str) -> UniProtProtein | None:
        """Fetch a single protein by accession."""
        response = await self.get(f"/uniprotkb/{accession}.json")
        return self._parse_entry(response.json())

    @staticmethod
    def _parse_entry(entry: dict) -> UniProtProtein:
        # Protein name
        prot_desc = entry.get("proteinDescription") or {}
        rec_name = prot_desc.get("recommendedName") or {}
        protein_name = (rec_name.get("fullName") or {}).get("value")

        # EC numbers
        ec_numbers = [e.get("value") for e in rec_name.get("ecNumbers") or [] if e.get("value")]

        # Genes
        genes = entry.get("genes") or []
        gene_name = None
        gene_synonyms: list[str] = []
        if genes:
            gn = genes[0].get("geneName") or {}
            gene_name = gn.get("value")
            for syn in genes[0].get("synonyms") or []:
                v = syn.get("value")
                if v:
                    gene_synonyms.append(v)

        # Organism
        org = entry.get("organism") or {}
        organism_name = org.get("scientificName")
        taxon_id = org.get("taxonId")

        # Sequence
        seq = entry.get("sequence") or {}

        entry_type = entry.get("entryType") or ""

        return UniProtProtein(
            accession=entry.get("primaryAccession") or "",
            uniprot_id=entry.get("uniProtkbId"),
            protein_name=protein_name,
            gene_name=gene_name,
            gene_synonyms=gene_synonyms,
            organism=organism_name,
            taxon_id=taxon_id,
            ec_numbers=ec_numbers,
            sequence_length=seq.get("length"),
            sequence_mass=seq.get("molWeight"),
            sequence=seq.get("value"),
            reviewed="reviewed" in entry_type.lower(),
        )