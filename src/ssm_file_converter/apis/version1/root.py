from fastapi import APIRouter

from ssm_file_converter.config import settings

root_router = APIRouter()


@root_router.get("/")
async def info():
    return {
        "name": settings.project_name,
        "version": settings.project_version
    }


@root_router.get("/healthcheck")
async def health():
    return {"status": "UP"}
