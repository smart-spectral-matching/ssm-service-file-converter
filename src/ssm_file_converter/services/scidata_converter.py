import pathlib
import scidatalib.io.jcamp
import scidatalib.io.rruff
from scidatalib.scidata import SciData
from typing import Union


def filename_to_scidata(filename: str) -> Union[SciData, None]:
    # Convert from file type to SciData JSON-LD
    scidata = None
    file_extension = pathlib.Path(filename).suffix

    if file_extension == ".rruff":
        scidata = scidatalib.io.rruff.read_rruff(filename)

    if file_extension in [".jdx", ".jcamp"]:
        scidata = scidatalib.io.jcamp.read_jcamp(filename)

    return scidata
