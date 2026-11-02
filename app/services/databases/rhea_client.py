import csv
import io

from loguru import logger

from app.core.config import settings
from app.services.databases.base_client import BaseHTTPClient
from app.services.databases.models import RheaReaction


class RheaClient(BaseHTTPClient):
    """
    Rhea REST API client.

    Docs: https://www.rhea-db.org/help/api
    """

    def __init__(self):
        super().__init__(base_url=settings.RHEA_BASE_URL)

    async def search_reactions(self, query: str, limit: int = 25) -> list[RheaReaction]:
        """
        Search reactions by keyword, ChEBI name, EC, etc.

        Example queries:
          - "glucose"
          - "2.7.11.1"
          - "chebi:4167"
        """
        params = {
            "query": query,
            "columns": "rhea-id,equation,ec,chebi",
            "format": "tsv",
            "limit": str(limit),
        }
        response = await self.get("/", params=params)
        return self._parse_tsv(response.text)

    async def get_reaction(self, rhea_id: str) -> RheaReaction | None:
        """Fetch a single reaction by RHEA ID, e.g. 'RHEA:10000'."""
        reactions = await self.search_reactions(f"rhea-id:{rhea_id}", limit=1)
        return reactions[0] if reactions else None

    def _parse_tsv(self, text: str) -> list[RheaReaction]:
        """Parse Rhea TSV response into models."""
        reader = csv.DictReader(io.StringIO(text), delimiter="\t")
        results: list[RheaReaction] = []
        for row in reader:
            try:
                # Strip "EC:" prefix and split multi-EC
                ec_raw = row.get("EC number") or ""
                ec_numbers = [
                    e.replace("EC:", "").strip()
                    for e in ec_raw.split(";")
                    if e.strip()
                ]
                # First one as primary, others as list
                primary_ec = ec_numbers[0] if ec_numbers else None

                # ChEBI column returns names, not IDs — store as chebi_names
                chebi_names_raw = row.get("ChEBI name") or ""
                chebi_names = [c.strip() for c in chebi_names_raw.split(";") if c.strip()]

                results.append(
                    RheaReaction(
                        rhea_id=row.get("Reaction identifier") or "",
                        equation=row.get("Equation") or "",
                        ec_number=primary_ec,
                        chebi_ids=[],  # not available in this endpoint
                        status=None,
                        direction=None,
                    )
                )
                # Log extra info for debugging
                if chebi_names:
                    logger.debug(f"Reaction {row.get('Reaction identifier')} | ChEBI names: {chebi_names}")
            except Exception as e:
                logger.warning(f"Failed to parse Rhea row: {e} | row={row}")
        return results