from fastapi import APIRouter

from ssm_file_converter.apis.version1.root import root_router


api_router = APIRouter()
api_router .include_router(
    root_router,
    prefix="",
    tags=["application"],
)
