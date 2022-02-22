from fastapi.testclient import TestClient

from ssm_file_converter import app

client = TestClient(app)


def test_convert():
    response = client.get("/convert")
    assert response.status_code == 200
    assert response.json() == {
        "input formats": ["rruff", "jcamp"],
        "output formats": ["json"]
    }



