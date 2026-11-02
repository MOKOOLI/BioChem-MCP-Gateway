from loguru import logger

from app.services.databases.base_client import BaseHTTPClient


class AlphaFoldClient(BaseHTTPClient):
    """
    Structure fetcher for proteins.

    Strategy:
      1. Try 3D-Beacons (EBI) for experimental PDBe structures.
      2. Try Google Cloud AlphaFold mirror for predicted structures.
      3. If both fail, return None.

    3D-Beacons: https://www.ebi.ac.uk/pdbe/pdbe-kb/3dbeacons/api
    AlphaFold GCS: https://storage.googleapis.com/public-datasets-deepmind-alphafold-v4
    """

    BEACONS_BASE = "https://www.ebi.ac.uk/pdbe/pdbe-kb/3dbeacons/api"
    ALPHAFOLD_GCS_BASE = "https://storage.googleapis.com/public-datasets-deepmind-alphafold-v4"

    def __init__(self):
        super().__init__(base_url=self.BEACONS_BASE, timeout=60.0)

    async def get_structure_info(self, uniprot_accession: str) -> dict | None:
        """
        Fetch structure info for a UniProt accession.
        Returns dict with keys: uniprot_accession, alphafold_url,
        pdbe_structures (list), source.
        """
        result = {
            "uniprot_accession": uniprot_accession,
            "alphafold_url": None,
            "pdbe_structures": [],
            "source": None,
        }

        # 1) Try Google Cloud AlphaFold mirror
        alphafold_url = await self._try_alphafold_gcs(uniprot_accession)
        if alphafold_url:
            result["alphafold_url"] = alphafold_url
            result["source"] = "AlphaFold (GCS)"
            logger.info(f"AlphaFold GCS hit for {uniprot_accession}")

        # 2) Try 3D-Beacons for experimental structures
        pdbe = await self._try_beacons(uniprot_accession)
        if pdbe:
            result["pdbe_structures"] = pdbe
            if not result["source"]:
                result["source"] = "PDBe (3D-Beacons)"
                logger.info(f"PDBe structures found for {uniprot_accession}: {len(pdbe)}")

        if not result["alphafold_url"] and not result["pdbe_structures"]:
            logger.warning(f"No structure found for {uniprot_accession}")
            return None

        return result

    async def _try_alphafold_gcs(self, accession: str) -> str | None:
        """Check if AlphaFold model exists on GCS public bucket."""
        import httpx
        url = f"{self.ALPHAFOLD_GCS_BASE}/AF-{accession}-F1-model_v4.pdb"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.head(url, follow_redirects=True)
                if r.status_code == 200:
                    return url
        except Exception as e:
            logger.debug(f"GCS head failed for {accession}: {e}")
        return None

    async def _try_beacons(self, accession: str) -> list[dict]:
        """Fetch experimental structures from 3D-Beacons."""
        try:
            response = await self.get(f"/uniprot/summary/{accession}.json")
            data = response.json()
        except Exception as e:
            logger.debug(f"3D-Beacons failed for {accession}: {e}")
            return []

        results = []
        for entry in data.get("structures", []):
            s = entry.get("summary", {})
            results.append({
                "pdb_id": s.get("model_identifier"),
                "provider": s.get("provider"),
                "category": s.get("model_category"),
                "method": s.get("experimental_method"),
                "resolution": s.get("resolution"),
                "coverage": s.get("coverage"),
                "url": s.get("model_url"),
                "page_url": s.get("model_page_url"),
            })
        return results