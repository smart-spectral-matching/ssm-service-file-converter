from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ssm_file_converter.apis import api_router
from ssm_file_converter.config import settings


def start_application():
    app = FastAPI(
        title=settings.project_name,
        version=settings.project_version
    )

    origin_regex = "http*://localhost*"

    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=origin_regex,
    )
    app.include_router(api_router)
    return app


app = start_application()
