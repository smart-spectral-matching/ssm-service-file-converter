from fastapi.testclient import TestClient
import json
import pathlib

from ssm_file_converter import app

FILE_ARG = "upload_files"
client = TestClient(app)


def test_merge() -> None:
    response = client.get("/merge")
    assert response.status_code == 200
    assert response.json() == {
        "options": [
            {
                "new data format": "json",
                "original data format": "json-ld",
                "output data format": "json-ld"
            },
        ]
    }


def test_merge_jsonld_with_json(
    raman_soddyite_ssm_json_file: pathlib.Path,
    raman_soddyite_scidata_jsonld_file: pathlib.Path,
) -> None:
    # post ssm json file to convert to jsonld
    with open(raman_soddyite_scidata_jsonld_file.absolute(), 'rb') as fjsonld:
        with open(raman_soddyite_ssm_json_file.absolute(), "rb") as fjson:
            files = [
                (FILE_ARG, (raman_soddyite_ssm_json_file.name, fjson)),
                (FILE_ARG, (raman_soddyite_scidata_jsonld_file.name, fjsonld)),
            ]
            response = client.post("/merge/jsonld", files=files)
    assert response.status_code == 200
    output = response.json()

    with open(raman_soddyite_scidata_jsonld_file.absolute(), 'rb') as f:
        target = json.load(f)

    assert output == target
