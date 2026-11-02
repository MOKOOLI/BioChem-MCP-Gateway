from dataclasses import dataclass, asdict

from loguru import logger
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, Descriptors, Draw, Lipinski


@dataclass
class DrugLikeness:
    """Lipinski Rule of Five + extra drug-likeness metrics."""
    molecular_weight: float
    logp: float
    h_donors: int
    h_acceptors: int
    rotatable_bonds: int
    tpsa: float
    num_rings: int
    num_heavy_atoms: int
    # Lipinski compliance
    passes_lipinski: bool
    violations: list[str]


@dataclass
class SimilarCompound:
    smiles: str
    tanimoto: float


class RDKitService:
    """
    Local cheminformatics operations using RDKit.
    No external API — always available offline.
    """

    @staticmethod
    def parse_smiles(smiles: str) -> Chem.Mol | None:
        """Parse SMILES to RDKit Mol object. Returns None if invalid."""
        if not smiles:
            return None
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            logger.warning(f"Invalid SMILES: {smiles}")
        return mol

    @classmethod
    def compute_drug_likeness(cls, smiles: str) -> DrugLikeness | None:
        """
        Compute Lipinski Rule of Five + extra metrics.
        Lipinski's rules:
          - MW ≤ 500
          - LogP ≤ 5
          - H-bond donors ≤ 5
          - H-bond acceptors ≤ 10
        """
        mol = cls.parse_smiles(smiles)
        if mol is None:
            return None

        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        rotb = Descriptors.NumRotatableBonds(mol)
        tpsa = Descriptors.TPSA(mol)
        rings = Descriptors.RingCount(mol)
        heavy = mol.GetNumHeavyAtoms()

        violations = []
        if mw > 500:
            violations.append(f"MW {mw:.1f} > 500")
        if logp > 5:
            violations.append(f"LogP {logp:.2f} > 5")
        if hbd > 5:
            violations.append(f"HBD {hbd} > 5")
        if hba > 10:
            violations.append(f"HBA {hba} > 10")

        return DrugLikeness(
            molecular_weight=round(mw, 2),
            logp=round(logp, 2),
            h_donors=hbd,
            h_acceptors=hba,
            rotatable_bonds=rotb,
            tpsa=round(tpsa, 2),
            num_rings=rings,
            num_heavy_atoms=heavy,
            passes_lipinski=len(violations) == 0,
            violations=violations,
        )

    @staticmethod
    def morgan_fingerprint(smiles: str, radius: int = 2, n_bits: int = 2048):
        """Generate Morgan fingerprint for similarity comparison."""
        mol = RDKitService.parse_smiles(smiles)
        if mol is None:
            return None
        generator = AllChem.GetMorganGenerator(radius=radius, fpSize=n_bits)
        return generator.GetFingerprint(mol)

    @classmethod
    def similarity(cls, smiles_a: str, smiles_b: str) -> float:
        """Tanimoto similarity between two SMILES (0.0 to 1.0)."""
        fp_a = cls.morgan_fingerprint(smiles_a)
        fp_b = cls.morgan_fingerprint(smiles_b)
        if fp_a is None or fp_b is None:
            return 0.0
        return round(DataStructs.TanimotoSimilarity(fp_a, fp_b), 4)

    @classmethod
    def find_similar(
        cls,
        query_smiles: str,
        library: list[dict],  # [{"name": ..., "smiles": ...}, ...]
        top_k: int = 5,
        min_similarity: float = 0.3,
    ) -> list[SimilarCompound]:
        """
        Screen a local library for compounds similar to query_smiles.
        Returns top_k hits with tanimoto >= min_similarity.
        """
        query_fp = cls.morgan_fingerprint(query_smiles)
        if query_fp is None:
            return []

        hits = []
        for entry in library:
            fp = cls.morgan_fingerprint(entry.get("smiles", ""))
            if fp is None:
                continue
            score = DataStructs.TanimotoSimilarity(query_fp, fp)
            if score >= min_similarity:
                hits.append(SimilarCompound(smiles=entry["smiles"], tanimoto=round(score, 4)))

        hits.sort(key=lambda x: x.tanimoto, reverse=True)
        return hits[:top_k]

    @staticmethod
    def contains_substructure(smiles: str, smarts: str) -> bool:
        """Check if SMILES contains a SMARTS pattern."""
        mol = RDKitService.parse_smiles(smiles)
        if mol is None:
            return False
        pattern = Chem.MolFromSmarts(smarts)
        if pattern is None:
            return False
        return mol.HasSubstructMatch(pattern)

    @staticmethod
    def to_canonical_smiles(smiles: str) -> str | None:
        """Return canonical SMILES form."""
        mol = RDKitService.parse_smiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol, canonical=True)

    @classmethod
    def to_dict(cls, obj) -> dict:
        """Convert dataclass to dict (for JSON serialization)."""
        return asdict(obj)