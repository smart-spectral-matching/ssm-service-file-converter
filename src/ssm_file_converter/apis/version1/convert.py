from fastapi import APIRouter, UploadFile, HTTPException
import time

from ssm_file_converter.utils.file_formats import (
    INPUT_FILE_FORMAT_TYPES,
    OUTPUT_FILE_FORMAT_TYPES,
)
from ssm_file_converter.services import (
    filename_to_scidata,
    scidata_to_ssm_json,
)

convert_router = APIRouter()


async def write_file(upload_file: UploadFile) -> str:
    # Read upload file to local file (required for scidatalib)
    filename = f'/tmp/{time.time()}-{upload_file.filename}'
    with open(f'{filename}', 'wb') as f:
        content = await upload_file.read()
        f.write(content)
    return filename


@convert_router.get("/")
async def format_info() -> dict:
    response = {
        "input formats": INPUT_FILE_FORMAT_TYPES,
        "output formats": OUTPUT_FILE_FORMAT_TYPES
    }
    return response


@convert_router.post("/jsonld")
async def convert_file_to_scidata_jsonld(upload_file: UploadFile) -> dict:
    filename = await write_file(upload_file)
    scidata = filename_to_scidata(filename)

    # Error handling if no file extension found
    if not scidata:
        raise HTTPException(
            status_code=400,
            detail="File format not supported"
        )

    return scidata.output


@convert_router.post("/json")
async def convert_file_to_abbreviated_jsonld(upload_file: UploadFile) -> dict:
    filename = await write_file(upload_file)
    scidata = filename_to_scidata(filename)

    # Error handling if no file extension found
    if not scidata:
        raise HTTPException(
            status_code=400,
            detail="File format not supported"
        )

    output = scidata_to_ssm_json(scidata)

    return output
