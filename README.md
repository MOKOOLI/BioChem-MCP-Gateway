# 🧬 BioChem MCP Gateway

A full-stack platform connecting biochemical databases (Rhea, ChEBI, UniProt, PDBe) to AI agents via the Model Context Protocol (MCP), with molecular docking capabilities.

## 🚀 Features
- **4 Biochemical Databases:** Rhea, ChEBI, UniProt, PDBe.
- **Cheminformatics:** RDKit (Lipinski, similarity).
- **Molecular Docking:** AutoDock Vina with async Celery tasks.
- **MCP Server:** 6 tools exposed to LLMs.
- **REST API:** FastAPI + SSE.
- **Fully Dockerized.**

## 🛠 Tech Stack
- Python 3.11, FastAPI, Celery, Redis
- RDKit, Meeko, AutoDock Vina
- Docker, Docker Compose

## 🚀 Quick Start

cd docker
docker compose up -d

API Docs: http://localhost:8000/docs

## 🧪 Example Docking

curl -X POST "http://localhost:8000/api/docking/submit" -H "Content-Type: application/json" -d "{\"smiles\":\"COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1\",\"pdb_id\":\"4i22\",\"exhaustiveness\":8}"