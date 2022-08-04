from fastapi.testclient import TestClient
import json
import pathlib
import pytest

from ssm_file_converter import app
from tests import TEST_DATA_DIR

FILE_ARG = "upload_file"
client = TestClient(app)


@pytest.fixture
def raman_soddyite_rruff_file():
    """
    Raman RRUFF file for Soddyite for wavelength 780 nm
    Retrieved on 1/12/2021 from:
        https://rruff.info/tmp_rruff/Soddyite__R060361__Broad_Scan__780__0__unoriented__Raman_Data_RAW__21504.rruff  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "rruff", "raman_soddyite.rruff")
    return p


@pytest.fixture
def raman_soddyite_jcamp_file():
    """
    Raman RRUFF file for Soddyite for wavelength 780 nm (in JCAMP format)
    Retrieved RRUFF file on 1/12/2021 from:
        https://rruff.info/tmp_rruff/Soddyite__R060361__Broad_Scan__780__0__unoriented__Raman_Data_RAW__21504.rruff  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "raman_soddyite.jdx")
    return p


@pytest.fixture
def raman_soddyite_scidata_jsonld_file():
    """
    SciData JSON-LD conversion of Soddyite RRUFF file above using SciDataLib
    """
    p = pathlib.Path(TEST_DATA_DIR, "scidata-jsonld", "raman_soddyite.jsonld")
    return p


@pytest.fixture
def raman_soddyite_ssm_json_file():
    """
    SSM abbreviated JSON conversion of Soddyite RRUFF file above
    """
    p = pathlib.Path(TEST_DATA_DIR, "ssm-json", "raman_soddyite.json")
    return p


def test_convert():
    response = client.get("/convert")
    assert response.status_code == 200
    assert response.json() == {
        "input formats": ["rruff", "jcamp", "json-ld"],
        "output formats": ["json", "json-ld"]
    }


def test_convert_rruff_to_jsonld(raman_soddyite_rruff_file):
    with open(raman_soddyite_rruff_file.absolute(), 'rb') as f:
        files = {FILE_ARG: (raman_soddyite_rruff_file.name, f)}
        response = client.post("/convert/jsonld", files=files)
    assert response.status_code == 200

    scidata = response.json().get("@graph")
    assert scidata.get("title") == "Soddyite"
    assert scidata.get("uid") == "rruff:R060361"
    assert "scidata" in scidata
    assert "methodology" in scidata.get("scidata")
    assert "system" in scidata.get("scidata")
    assert "dataset" in scidata.get("scidata")


def test_convert_jcamp_to_jsonld(
    raman_soddyite_jcamp_file,
    raman_soddyite_scidata_jsonld_file,
):
    # target ssm json file
    with open(raman_soddyite_scidata_jsonld_file.absolute(), "rb") as f:
        target = json.load(f)

    # post jcamp file to convert to scidata jsonld
    with open(raman_soddyite_jcamp_file.absolute(), 'rb') as f:
        files = {FILE_ARG: (raman_soddyite_jcamp_file.name, f)}
        response = client.post("/convert/jsonld", files=files)
    assert response.status_code == 200
    output = response.json()

    # have to remove create and modified date since won't match
    for key in ["generatedAt"]:
        output.pop(key)
        target.pop(key)

    # Hack to get around SciDataLib error
    target["@graph"]["scidata"]["methodology"]["aspects"][0]["@id"] = "measurement/1/1/"

    assert sorted(output.items()) == sorted(target.items())


def test_convert_jcamp_to_abbreviated_json(
    raman_soddyite_jcamp_file,
    raman_soddyite_ssm_json_file,
):
    # target ssm json file
    with open(raman_soddyite_ssm_json_file.absolute(), "rb") as f:
        target = json.load(f)

    # post jcamp file to convert to ssm json
    with open(raman_soddyite_jcamp_file.absolute(), 'rb') as f:
        files = {FILE_ARG: (raman_soddyite_jcamp_file.name, f)}
        response = client.post("/convert/json", files=files)
    assert response.status_code == 200
    output = response.json()

    # have to remove create and modified date since won't match
    for key in ["created", "modified"]:
        output.pop(key)
        target.pop(key)

    assert sorted(output.items()) == sorted(target.items())


def test_convert_jsonld_to_abbreviated_json(
    raman_soddyite_scidata_jsonld_file,
    raman_soddyite_ssm_json_file,
):
    # target ssm json file
    with open(raman_soddyite_ssm_json_file.absolute(), "rb") as f:
        target = json.load(f)

    # post jsonld file to convert to ssm json
    with open(raman_soddyite_scidata_jsonld_file.absolute(), 'rb') as f:
        files = {FILE_ARG: (raman_soddyite_scidata_jsonld_file.name, f)}
        response = client.post("/convert/json", files=files)
    assert response.status_code == 200
    output = response.json()

    # have to remove create and modified date since won't match
    for key in ["created", "modified"]:
        output.pop(key)
        target.pop(key)

    assert sorted(output.items()) == sorted(target.items())


def test_convert_abbreviated_json_to_jsonld(
    raman_soddyite_ssm_json_file,
    raman_soddyite_scidata_jsonld_file,
):
    # target jsonld file
    with open(raman_soddyite_scidata_jsonld_file.absolute(), 'rb') as f:
        target = json.load(f)

    # post ssm json file to convert to jsonld
    with open(raman_soddyite_ssm_json_file.absolute(), "rb") as f:
        files = {FILE_ARG: (raman_soddyite_ssm_json_file.name, f)}
        response = client.post("/convert/jsonld", files=files)
    assert response.status_code == 200
    output = response.json()

    # have to remove create and modified date since won't match
    for key in ["generatedAt"]:
        output.pop(key)
        target.pop(key)

    assert output.get("title") == target.get("title")

    output_scidata = output.get("@graph").get("scidata")
    target_scidata = target.get("@graph").get("scidata")

    output_methodology = output_scidata.get("methodology")
    target_methodology = target_scidata.get("methodology")
    assert output_methodology == target_methodology

    output_dataseries = output_scidata. get("dataset").get("dataseries")
    target_dataseries = target_scidata.get("dataset").get("dataseries")
    for output_ds, target_ds in zip(output_dataseries, target_dataseries):
        checked_keys = [key for key in output_ds if key not in ["parameter"]]
        for key in checked_keys:
            assert output_ds.get(key) == target_ds.get(key)
