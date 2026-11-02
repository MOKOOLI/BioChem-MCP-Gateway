import httpx

urls = {
    "AlphaFold API (main)": "https://alphafold.ebi.ac.uk/api/prediction/P00533",
    "3D-Beacons API": "https://www.ebi.ac.uk/pdbe/pdbe-kb/3dbeacons/api/uniprot/summary/P00533.json",
    "AlphaFold PDB (direct)": "https://alphafold.ebi.ac.uk/files/AF-P00533-F1-model_v4.pdb",
}

for name, url in urls.items():
    try:
        r = httpx.get(url, timeout=60, follow_redirects=True)
        print(f"{r.status_code} | {name}")
    except Exception as e:
        print(f"FAILED | {name} | {type(e).__name__}: {e}")