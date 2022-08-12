from fastapi.testclient import TestClient
import json

from ssm_file_converter import app

FILE_ARG = "upload_file"
client = TestClient(app)


def test_merge():
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

