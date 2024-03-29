from fastapi.testclient import TestClient

from ssm_file_converter.version import __version__
from ssm_file_converter import app

client = TestClient(app)


def test_info():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "name": "SSM File Converter Service",
        "version": __version__,
    }


def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}
