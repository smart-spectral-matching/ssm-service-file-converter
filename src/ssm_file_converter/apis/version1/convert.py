from fastapi import APIRouter, UploadFile, HTTPException
import pathlib
import scidatalib.io.jcamp
import scidatalib.io.rruff
import time

from ssm_file_converter.utils.file_formats import (
    INPUT_FILE_FORMAT_TYPES,
    OUTPUT_FILE_FORMAT_TYPES,
)

convert_router = APIRouter()


@convert_router.get("/")
async def format_info():
    response = {
        "input formats": INPUT_FILE_FORMAT_TYPES,
        "output formats": OUTPUT_FILE_FORMAT_TYPES
    }
    return response


@convert_router.post("/jsonld")
async def convert_file_to_json(file: UploadFile):
    # Read upload file to local file (required for scidatalib)
    filename = f'/tmp/{time.time()}-{file.filename}'
    with open(f'{filename}', 'wb') as f:
        content = await file.read()
        f.write(content)

    # Convert from file type to SciData JSON-LD
    scidata = None
    file_extension = pathlib.Path(filename).suffix
    if file_extension == ".rruff":
        scidata = scidatalib.io.rruff.read_rruff(filename)
    if file_extension in [".jdx", ".jcamp"]:
        scidata = scidatalib.io.jcamp.read_jcamp(filename)

    # Error handling if no file extension found
    if not scidata:
        raise HTTPException(
            status_code=400,
            detail="File format not supported"
        )

    return scidata.output
