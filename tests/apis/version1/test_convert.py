from fastapi.testclient import TestClient
import pathlib
import pytest

from ssm_file_converter import app
from tests import TEST_DATA_DIR

client = TestClient(app)


@pytest.fixture
def raman_soddyite_file():
    """
    Raman RRUFF file for Soddyite for wavelength 780 nm
    Retrieved on 1/12/2021 from:
        https://rruff.info/tmp_rruff/Soddyite__R060361__Broad_Scan__780__0__unoriented__Raman_Data_RAW__21504.rruff  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "rruff", "raman_soddyite.rruff")
    return p


def test_convert():
    response = client.get("/convert")
    assert response.status_code == 200
    assert response.json() == {
        "input formats": ["rruff", "jcamp"],
        "output formats": ["json"]
    }


def test_convert_rruff_to_json(raman_soddyite_file):
    with open(raman_soddyite_file.absolute(), 'rb') as f:
        files = {"file": ("filename", f)}
        response = client.post("/convert/json", files=files)
    assert response.status_code == 200
