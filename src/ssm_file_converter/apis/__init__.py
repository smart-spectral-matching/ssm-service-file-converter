from fastapi import APIRouter

from ssm_file_converter.apis.version1.root import root_router
from ssm_file_converter.apis.version1.convert import convert_router


api_router = APIRouter()
api_router .include_router(
    root_router,
    prefix="",
    tags=["application"],
)
api_router .include_router(
    convert_router,
    prefix="/convert",
    tags=["converter"],
)
