from fastapi import APIRouter, UploadFile
import time
from typing import List

from ssm_file_converter.services import merge_data_from_filenames

merge_router = APIRouter()


@merge_router.get("/")
async def options_info():
    response = {
        "options": [
            {
                "new data format": "json",
                "original data format": "json-ld",
                "output data format": "json-ld"
            },
        ]
    }
    return response


async def write_files(upload_files: List[UploadFile]) -> List[str]:
    # Read upload file to local file (required for scidatalib)
    filenames = list()
    for upload_file in upload_files:
        filename = f'/tmp/{time.time()}-{upload_file.filename}'
        with open(f'{filename}', 'wb') as f:
            content = await upload_file.read()
            f.write(content)
        filenames.append(filename)
    return filenames


@merge_router.post("/jsonld")
async def merge_to_scidata_jsonld(upload_files: List[UploadFile]) -> dict:
    filenames = await write_files(upload_files)
    merged = merge_data_from_filenames(filenames)
    return merged
