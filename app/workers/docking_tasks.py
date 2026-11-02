import subprocess
import tempfile
from pathlib import Path

import httpx
from loguru import logger
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation, PDBQTWriterLegacy

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="dock_ligand")
def dock_ligand_task(self, smiles: str, pdb_id: str, exhaustiveness: int = 8) -> dict:
    self.update_state(state="PROGRESS", meta={"step": "start"})
    logger.info(f"Starting docking: SMILES={smiles}, PDB={pdb_id}")

    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            receptor_cif = tmp_path / f"{pdb_id}.cif"
            receptor_pdb = tmp_path / f"{pdb_id}.pdb"
            cleaned_pdb = tmp_path / "cleaned.pdb"
            ligand_pdbqt = tmp_path / "ligand.pdbqt"
            receptor_basename = tmp_path / "receptor"
            receptor_pdbqt = tmp_path / "receptor.pdbqt"
            box_txt = tmp_path / "receptor.box.txt"
            out_pdbqt = tmp_path / "out.pdbqt"

            # 1. Download receptor from PDBe
            self.update_state(state="PROGRESS", meta={"step": "download_receptor"})
            cif_url = f"https://www.ebi.ac.uk/pdbe/static/entry/{pdb_id.lower()}_updated.cif"
            with httpx.stream("GET", cif_url, timeout=60) as r:
                r.raise_for_status()
                with open(receptor_cif, "wb") as f:
                    for chunk in r.iter_bytes():
                        f.write(chunk)

            # 2. Convert CIF → PDB via openbabel
            self.update_state(state="PROGRESS", meta={"step": "convert_receptor"})
            subprocess.run(
                ["obabel", str(receptor_cif), "-O", str(receptor_pdb), "-h"],
                check=True, capture_output=True,
            )

            # 3. استخراج فقط زنجیره A (حذف لیگاند، آب و یون‌های اضافی)
            self.update_state(state="PROGRESS", meta={"step": "clean_receptor"})
            with open(receptor_pdb, "r") as fin, open(cleaned_pdb, "w") as fout:
                for line in fin:
                    if line.startswith(("ATOM", "HETATM")):
                        if line[21] == "A":
                            res_name = line[17:20].strip()
                            if res_name not in ("HOH", "WAT"):
                                fout.write(line)

            # 4. Prepare ligand from SMILES using Meeko Python API
            self.update_state(state="PROGRESS", meta={"step": "prepare_ligand"})
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {"status": "error", "error": f"Invalid SMILES: {smiles}"}
            
            mol = Chem.AddHs(mol)
            result = AllChem.EmbedMolecule(mol, randomSeed=42)
            if result != 0:
                return {"status": "error", "error": "Failed to embed 3D coordinates"}
            
            AllChem.MMFFOptimizeMolecule(mol)

            preparator = MoleculePreparation()
            mol_setups = preparator.prepare(mol)
            if not mol_setups:
                return {"status": "error", "error": "Meeko failed to prepare molecule"}
            
            pdbqt_result = PDBQTWriterLegacy.write_string(mol_setups[0])
            pdbqt_string = pdbqt_result[0] if isinstance(pdbqt_result, tuple) else pdbqt_result
            
            with open(ligand_pdbqt, "w") as f:
                f.write(pdbqt_string)

            # 5. Meeko: receptor PDB → PDBQT + ساخت خودکار فایل box.txt
            self.update_state(state="PROGRESS", meta={"step": "prepare_receptor"})
            subprocess.run(
                [
                    "mk_prepare_receptor.py",
                    "-i", str(cleaned_pdb),
                    "-o", str(receptor_basename),
                    "-p",
                    "-v",
                    "--box_size", "22", "22", "22",
                    "--box_center", "0", "0", "0",
                    "-a",
                    "--delete_residues", "HOH"
                ],
                check=True, capture_output=True,
            )
            
            expected_box_file = tmp_path / "receptor.box.txt"
            if not expected_box_file.exists():
                with open(expected_box_file, "w") as f:
                    f.write("center_x = 0\ncenter_y = 0\ncenter_z = 0\nsize_x = 22\nsize_y = 22\nsize_z = 22\n")

            # 6. Run Vina با استفاده از فایل box.txt
            self.update_state(state="PROGRESS", meta={"step": "vina"})
            result = subprocess.run(
                [
                    "vina",
                    "--receptor", str(receptor_pdbqt),
                    "--ligand", str(ligand_pdbqt),
                    "--config", str(expected_box_file),
                    "--out", str(out_pdbqt),
                    "--exhaustiveness", str(exhaustiveness),
                    "--num_modes", "10",
                ],
                capture_output=True, text=True, timeout=540,
            )

            if result.returncode != 0:
                return {"status": "error", "error": result.stderr[:500]}

            # 7. Parse energies from stdout
            energies = []
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line and line[0].isdigit():
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            energies.append(float(parts[1]))
                        except ValueError:
                            pass

            self.update_state(state="PROGRESS", meta={"step": "done"})
            return {
                "status": "ok",
                "pdb_id": pdb_id,
                "smiles": smiles,
                "num_poses": len(energies),
                "energies": energies,
                "best_energy": min(energies) if energies else None,
            }

    except subprocess.CalledProcessError as e:
        logger.error(f"Docking failed at subprocess step: {e.stderr[:500]}")
        return {"status": "error", "error": e.stderr[:500]}
    except Exception as e:
        logger.exception(f"Docking crashed: {e}")
        return {"status": "error", "error": str(e)}