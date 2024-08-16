from fastapi import FastAPI

from ssm_file_converter.apis import api_router
from ssm_file_converter.config import settings


def start_application():
    app = FastAPI(
        title=settings.project_name,
        version=settings.project_version
    )

    app.include_router(api_router)
    return app


app = start_application()
