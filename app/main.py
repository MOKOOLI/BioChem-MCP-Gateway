from fastapi import FastAPI
from loguru import logger

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    debug=settings.DEBUG,
)

app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.APP_NAME} starting in {settings.APP_ENV} mode")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )