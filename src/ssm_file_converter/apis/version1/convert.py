from fastapi import APIRouter, UploadFile

convert_router = APIRouter()


@convert_router.get("/")
async def format_info():
    input_formats = ["rruff", "jcamp"]
    output_formats = ["json"]
    return {"input formats": input_formats, "output formats": output_formats}


@convert_router.post("/json")
async def convert_file_to_json(file: UploadFile):
    return {"filename": file.filename}
