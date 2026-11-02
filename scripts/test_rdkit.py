from app.services.cheminformatics.rdkit_service import RDKitService


def main():
    svc = RDKitService()

    print("=== Aspirin (CC(=O)Oc1ccccc1C(=O)O) ===")
    dl = svc.compute_drug_likeness("CC(=O)Oc1ccccc1C(=O)O")
    print(f"  MW:          {dl.molecular_weight}")
    print(f"  LogP:        {dl.logp}")
    print(f"  HBD:         {dl.h_donors}")
    print(f"  HBA:         {dl.h_acceptors}")
    print(f"  Rotatable:   {dl.rotatable_bonds}")
    print(f"  TPSA:        {dl.tpsa}")
    print(f"  Rings:       {dl.num_rings}")
    print(f"  Passes:      {dl.passes_lipinski}")
    print(f"  Violations:  {dl.violations}")

    print("\n=== Glucose (OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O) ===")
    dl = svc.compute_drug_likeness("OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O")
    print(f"  MW:          {dl.molecular_weight}")
    print(f"  HBD:         {dl.h_donors}")
    print(f"  HBA:         {dl.h_acceptors}")
    print(f"  Passes:      {dl.passes_lipinski} (violations: {dl.violations})")

    print("\n=== Similarity: Aspirin vs Ibuprofen ===")
    # Ibuprofen SMILES
    ibu = "CC(C)Cc1ccc(cc1)C(C)C(=O)O"
    sim = svc.similarity("CC(=O)Oc1ccccc1C(=O)O", ibu)
    print(f"  Tanimoto: {sim}")

    print("\n=== Substructure: Aspirin contains benzene ring ===")
    has_ring = svc.contains_substructure("CC(=O)Oc1ccccc1C(=O)O", "c1ccccc1")
    print(f"  Has benzene: {has_ring}")

    print("\n=== Find similar in local library ===")
    library = [
        {"name": "Aspirin", "smiles": "CC(=O)Oc1ccccc1C(=O)O"},
        {"name": "Ibuprofen", "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O"},
        {"name": "Paracetamol", "smiles": "CC(=O)Nc1ccc(O)cc1"},
        {"name": "Caffeine", "smiles": "Cn1cnc2c1c(=O)n(C)c(=O)n2C"},
    ]
    hits = svc.find_similar("CC(=O)Oc1ccccc1C(=O)O", library, top_k=3, min_similarity=0.1)
    for h in hits:
        print(f"  {h.smiles} | Tanimoto={h.tanimoto}")

    print("\n=== Invalid SMILES ===")
    bad = svc.compute_drug_likeness("this is not a smiles")
    print(f"  Result: {bad}")


if __name__ == "__main__":
    main()