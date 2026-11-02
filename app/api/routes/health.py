from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "biochem-mcp-gateway"}


@router.get("/")
async def root():
    return {
        "service": "BioChem MCP Gateway",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/healthz",
    }