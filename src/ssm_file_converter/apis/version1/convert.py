from fastapi import APIRouter

convert_router = APIRouter()


@convert_router.get("/")
async def format_info():
    input_formats = ["rruff", "jcamp"]
    output_formats = ["json"]
    return {"input formats": input_formats, "output formats": output_formats}
