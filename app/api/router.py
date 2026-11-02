from fastapi import APIRouter

from app.api.routes import chebi, docking, health, molecules, rhea, structure, uniprot

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(rhea.router)
api_router.include_router(chebi.router)
api_router.include_router(uniprot.router)
api_router.include_router(structure.router)
api_router.include_router(molecules.router)
api_router.include_router(docking.router)
