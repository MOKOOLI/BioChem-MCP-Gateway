from loguru import logger

from app.core.config import settings
from app.services.databases.base_client import BaseHTTPClient
from app.services.databases.models import ChebiCompound


class ChebiClient(BaseHTTPClient):
    """
    ChEBI client using OLS4 REST API.

    Endpoints:
      - Search: /search?q=...&ontology=chebi&rows=N
      - Lookup: /ontologies/chebi/terms?obo_id=CHEBI:xxxxx
    """

    def __init__(self):
        super().__init__(base_url=settings.CHEBI_BASE_URL)

    async def search_compounds(self, query: str, limit: int = 10) -> list[ChebiCompound]:
        """Search ChEBI by name / synonym / keyword."""
        params = {
            "q": query,
            "ontology": "chebi",
            "rows": str(limit),
            "exact": "false",
        }
        response = await self.get("/search", params=params)
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        results: list[ChebiCompound] = []
        for doc in docs:
            # search endpoint returns shallow info; try to build minimal object
            obo_id = doc.get("obo_id") or ""
            if not obo_id:
                continue
            results.append(
                ChebiCompound(
                    chebi_id=obo_id,
                    label=doc.get("label") or "",
                    description=(doc.get("description") or [None])[0],
                    is_obsolete=False,
                )
            )
        return results

    async def get_compound(self, chebi_id: str) -> ChebiCompound | None:
        """
        Fetch full details for a ChEBI ID.

        Accepts formats: 'CHEBI:15365', '15365', 'CHEBI_15365'
        """
        normalized = self._normalize_chebi_id(chebi_id)
        params = {"obo_id": normalized}
        response = await self.get("/ontologies/chebi/terms", params=params)
        data = response.json()

        terms = data.get("_embedded", {}).get("terms", [])
        if not terms:
            logger.warning(f"No ChEBI term found for {chebi_id}")
            return None

        return self._parse_term(terms[0])

    @staticmethod
    def _normalize_chebi_id(chebi_id: str) -> str:
        """Convert various formats to 'CHEBI:NNNNN'."""
        s = chebi_id.strip().upper()
        if s.startswith("CHEBI:"):
            return s
        if s.startswith("CHEBI_"):
            return s.replace("CHEBI_", "CHEBI:", 1)
        if s.isdigit():
            return f"CHEBI:{s}"
        return s

    @staticmethod
    def _first(value):
        """Get first element of a list-valued annotation, or None."""
        if isinstance(value, list) and value:
            return value[0]
        return value

    def _parse_term(self, term: dict) -> ChebiCompound:
        ann = term.get("annotation") or {}

        mass_raw = self._first(ann.get("mass"))
        mono_raw = self._first(ann.get("monoisotopic_mass"))
        charge_raw = self._first(ann.get("charge"))

        # group xrefs by database
        xrefs_grouped: dict[str, list[str]] = {}
        for xref in ann.get("database_cross_reference") or []:
            if ":" in xref:
                db, ident = xref.split(":", 1)
                xrefs_grouped.setdefault(db, []).append(ident)

        return ChebiCompound(
            chebi_id=term.get("obo_id") or "",
            label=term.get("label") or "",
            description=self._first(term.get("description")),
            smiles=self._first(ann.get("smiles_string")),
            formula=self._first(ann.get("generalized_empirical_formula")),
            mass=float(mass_raw) if mass_raw is not None else None,
            monoisotopic_mass=float(mono_raw) if mono_raw is not None else None,
            charge=float(charge_raw) if charge_raw is not None else None,
            inchi=self._first(ann.get("inchi_string")),
            inchi_key=self._first(ann.get("inchi_key_string")),
            synonyms=term.get("synonyms") or [],
            xrefs=xrefs_grouped,
            is_obsolete=bool(term.get("is_obsolete")),
        )