from fastapi.testclient import TestClient
import json
import math
import pathlib
import pytest

from ssm_file_converter import app

FILE_ARG = "upload_file"
client = TestClient(app)


# Template functions

def __test_convert_jsonld_to_abbreviated_json(
    scidata_jsonld_file: pathlib.Path,
    ssm_json_file: pathlib.Path,
) -> None:
    """Test utility function for JSON-LD -> SSM JSON"""

    # target ssm json file
    with open(ssm_json_file.absolute(), "rb") as f:
        target = json.load(f)

    # post jsonld file to convert to ssm json
    with open(scidata_jsonld_file.absolute(), "rb") as f:
        files = {FILE_ARG: (scidata_jsonld_file.name, f)}
        response = client.post("/convert/json", files=files)
    assert response.status_code == 200
    output = response.json()

    # have to remove create and modified date since won't match
    for key in ["created", "modified"]:
        output.pop(key)
        target.pop(key)

    output_methodology = output.get("scidata").get("methodology").items()
    target_methodology = target.get("scidata").get("methodology").items()
    assert sorted(output_methodology) == sorted(target_methodology)

    output_system = output.get("scidata").get("system").items()
    target_system = target.get("scidata").get("system").items()
    assert sorted(output_system) == sorted(target_system)

    output_dataseries = output.get("scidata").get("dataseries")[0].items()
    target_dataseries = target.get("scidata").get("dataseries")[0].items()
    assert sorted(output_dataseries) == sorted(target_dataseries)

    assert sorted(output.items()) == sorted(target.items())


def __test_convert_abbreviated_json_to_jsonld(
    ssm_json_file: pathlib.Path,
    scidata_jsonld_file: pathlib.Path,
) -> None:
    """Test utility function for SSM JSON -> JSON-LD"""
    # target jsonld file
    with open(scidata_jsonld_file.absolute(), "rb") as f:
        target = json.load(f)

    # post ssm json file to convert to jsonld
    with open(ssm_json_file.absolute(), "rb") as f:
        files = {FILE_ARG: (ssm_json_file.name, f)}
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

    output_dataseries = output_scidata.get("dataset").get("dataseries")
    target_dataseries = target_scidata.get("dataset").get("dataseries")
    for output_ds, target_ds in zip(output_dataseries, target_dataseries):
        checked_keys = [key for key in output_ds if key not in ["parameter"]]
        for key in checked_keys:
            assert output_ds.get(key) == target_ds.get(key)


def __test_convert_rruff_to_jsonld(
    rruff_file: pathlib.Path,
    scidata_jsonld_file: pathlib.Path,
) -> None:
    with open(rruff_file.absolute(), "rb") as f:
        files = {FILE_ARG: (rruff_file.name, f)}
        response = client.post("/convert/jsonld", files=files)
    assert response.status_code == 200

    scidata = response.json().get("@graph")
    assert "title" in scidata
    assert "uid" in scidata
    assert "scidata" in scidata
    assert "methodology" in scidata.get("scidata")
    assert "system" in scidata.get("scidata")
    assert "dataset" in scidata.get("scidata")


def __test_convert_rruff_to_abbreviated_json(
    rruff_file: pathlib.Path,
    ssm_json_file: pathlib.Path,
) -> None:
    # target ssm json file
    with open(ssm_json_file.absolute(), "rb") as f:
        target = json.load(f)

    # post rruff file to convert to ssm json
    with open(rruff_file.absolute(), "rb") as f:
        files = {FILE_ARG: (rruff_file.name, f)}
        response = client.post("/convert/json", files=files)
    assert response.status_code == 200
    output = response.json()

    # Get partial sources, compare separately and then remove sources key
    target_source = target["sources"][0]["citation"]
    output_source = output["sources"][0]["citation"]
    assert output_source == target_source
    target.pop("sources")
    output.pop("sources")

    # TODO: ignoring the description section, needs more attention for testing
    target.pop("description")
    output.pop("description")

    # Property isn't included so remove
    if "property" in target.get("scidata"):
        target["scidata"].pop("property")

    # have to remove create and modified date since won't match
    for key in ["created", "modified"]:
        output.pop(key)
        target.pop(key)

    # Methodology
    output_methodology = output.get("scidata").get("methodology")
    target_methodology = target.get("scidata").get("methodology")

    mismatched_keys = [
        "techniqueType",
        "instrument",
        "settings",
        "technique",
        "instrumentType"
    ]
    for key in mismatched_keys:
        if key in output_methodology:
            output_methodology.pop(key)
        if key in target_methodology:
            target_methodology.pop(key)

    output_methodology_sorted = sorted(output_methodology.items())
    target_methodology_sorted = sorted(target_methodology.items())
    assert output_methodology_sorted == target_methodology_sorted

    # System
    output_system = output.get("scidata").get("system")
    target_system = target.get("scidata").get("system")

    target_missing_keys = [
        "compound",
        "coordinationchemistry",
        "crystalsystem",
        "functionalgroup",
        "structuretype",
    ]
    for key in target_missing_keys:
        if key in target_system:
            target_system.pop(key)

    assert sorted(output_system.items()) == sorted(target_system.items())

    # Dataseries
    output_dataseries = output.get("scidata").get("dataseries")[0]
    target_dataseries = target.get("scidata").get("dataseries")[0]

    # - floor so floats are same sig figs
    output_xaxis = output_dataseries.pop('x-axis')
    output_xaxis = output_xaxis.get('parameter')
    output_xaxis = output_xaxis.get('numericValueArray')[0]
    output_xaxis = output_xaxis.get('numberArray')

    target_xaxis = target_dataseries.pop('x-axis')
    target_xaxis = target_xaxis.get('parameter')
    target_xaxis = target_xaxis.get('numericValueArray')[0]
    target_xaxis = target_xaxis.get('numberArray')

    output_xaxis = [math.floor(x) for x in output_xaxis]
    target_xaxis = [math.floor(x) for x in target_xaxis]

    assert output_xaxis == target_xaxis

    output_dataseries_sorted = sorted(output_dataseries.items())
    target_dataseries_sorted = sorted(target_dataseries.items())
    assert output_dataseries_sorted == target_dataseries_sorted


# Basic API tests

def test_convert() -> None:
    response = client.get("/convert")
    assert response.status_code == 200
    assert response.json() == {
        "input formats": ["rruff", "jcamp", "json-ld", "json"],
        "output formats": ["json", "json-ld"],
    }

# JCAMP


def test_convert_jcamp_to_jsonld(
    raman_soddyite_jcamp_file: pathlib.Path,
    raman_soddyite_scidata_jsonld_file: pathlib.Path,
) -> None:
    # target ssm json file
    with open(raman_soddyite_scidata_jsonld_file.absolute(), "rb") as f:
        target = json.load(f)

    # post jcamp file to convert to scidata jsonld
    with open(raman_soddyite_jcamp_file.absolute(), "rb") as f:
        files = {FILE_ARG: (raman_soddyite_jcamp_file.name, f)}
        response = client.post("/convert/jsonld", files=files)
    assert response.status_code == 200
    output = response.json()

    # Get partial sources, compare separately and then remove sources key
    target_source = target["@graph"]["sources"][0]["citation"]
    output_source = output["@graph"]["sources"][0]["citation"]
    assert output_source == target_source
    target["@graph"].pop("sources")
    output["@graph"].pop("sources")

    # have to remove create and modified date since won't match
    for key in ["generatedAt"]:
        output.pop(key)
        target.pop(key)

    # Removes system section from target since info not in JCAMP file
    target["@graph"]["scidata"].pop("system")

    # Property isn't included so remove
    target["@graph"]["scidata"].pop("property")

    # Hack to get around SciDataLib error
    target_aspects = target["@graph"]["scidata"]["methodology"]["aspects"]
    target_aspects[0]["@id"] = "measurement/1/1/"

    assert sorted(output.items()) == sorted(target.items())


def test_convert_jcamp_to_abbreviated_json(
    raman_soddyite_jcamp_file: pathlib.Path,
    raman_soddyite_ssm_json_file: pathlib.Path,
) -> None:
    # target ssm json file
    with open(raman_soddyite_ssm_json_file.absolute(), "rb") as f:
        target = json.load(f)

    # post jcamp file to convert to ssm json
    with open(raman_soddyite_jcamp_file.absolute(), "rb") as f:
        files = {FILE_ARG: (raman_soddyite_jcamp_file.name, f)}
        response = client.post("/convert/json", files=files)
    assert response.status_code == 200
    output = response.json()

    # Get partial sources, compare separately and then remove sources key
    target_source = target["sources"][0]["citation"]
    output_source = output["sources"][0]["citation"]
    assert output_source == target_source
    target.pop("sources")
    output.pop("sources")

    # Removes system section from target since info not in JCAMP file
    target["scidata"].pop("system")

    # Property isn't included so remove
    target["scidata"].pop("property")

    # have to remove create and modified date since won't match
    for key in ["created", "modified"]:
        output.pop(key)
        target.pop(key)

    assert sorted(output.items()) == sorted(target.items())


# RRUFF

def test_convert_rruff_to_jsonld_raman_soddyite(
    raman_soddyite_rruff_file: pathlib.Path,
    raman_soddyite_scidata_jsonld_file: pathlib.Path,
) -> None:
    __test_convert_rruff_to_jsonld(
        raman_soddyite_rruff_file,
        raman_soddyite_scidata_jsonld_file,
    )


def test_convert_rruff_to_abbreviated_json_raman_soddyite(
    raman_soddyite_rruff_file: pathlib.Path,
    raman_soddyite_ssm_json_file: pathlib.Path,
) -> None:
    __test_convert_rruff_to_abbreviated_json(
        raman_soddyite_rruff_file,
        raman_soddyite_ssm_json_file,
    )


def test_convert_rruff_to_abbreviated_json_raman_auc(
    raman_auc_rruff_file: pathlib.Path,
    raman_auc_ssm_json_file: pathlib.Path,
) -> None:
    __test_convert_rruff_to_abbreviated_json(
        raman_auc_rruff_file,
        raman_auc_ssm_json_file,
    )


# SSM JSON -> SciData JSON-LD


@pytest.mark.skip("Failing in SciDataLib dataseries parsing...")
def test_convert_abbreviated_json_to_jsonld_raman_soddyite(
    raman_soddyite_ssm_json_file: pathlib.Path,
    raman_soddyite_scidata_jsonld_file: pathlib.Path,
) -> None:
    __test_convert_abbreviated_json_to_jsonld(
        raman_soddyite_ssm_json_file,
        raman_soddyite_scidata_jsonld_file,
    )


@pytest.mark.skip("Failing in SciDataLib dataseries parsing...")
def test_convert_abbreviated_json_to_jsonld_raman_studtite(
    raman_studtite_ssm_json_file: pathlib.Path,
    raman_studtite_scidata_jsonld_file: pathlib.Path,
) -> None:
    __test_convert_abbreviated_json_to_jsonld(
        raman_studtite_ssm_json_file,
        raman_studtite_scidata_jsonld_file,
    )


@pytest.mark.skip("Failing in SciDataLib dataseries parsing...")
def test_convert_abbreviated_json_to_jsonld_nmr_limonene(
    nmr_limonene_ssm_json_file: pathlib.Path,
    nmr_limonene_scidata_jsonld_file: pathlib.Path,
) -> None:
    __test_convert_abbreviated_json_to_jsonld(
        nmr_limonene_ssm_json_file,
        nmr_limonene_scidata_jsonld_file,
    )


# SciData JSON-LD -> SSM JSON


def test_convert_jsonld_to_abbreviated_json_raman_soddyite(
    raman_soddyite_scidata_jsonld_file: pathlib.Path,
    raman_soddyite_ssm_json_file: pathlib.Path,
) -> None:
    __test_convert_jsonld_to_abbreviated_json(
        raman_soddyite_scidata_jsonld_file, raman_soddyite_ssm_json_file
    )


def test_convert_jsonld_to_abbreviated_json_ramad_studtite(
    raman_studtite_scidata_jsonld_file: pathlib.Path,
    raman_studtite_ssm_json_file: pathlib.Path,
) -> None:
    __test_convert_jsonld_to_abbreviated_json(
        raman_studtite_scidata_jsonld_file, raman_studtite_ssm_json_file
    )


def test_convert_jsonld_to_abbreviated_json_nmr_limonene(
    nmr_limonene_scidata_jsonld_file: pathlib.Path,
    nmr_limonene_ssm_json_file: pathlib.Path,
) -> None:
    __test_convert_jsonld_to_abbreviated_json(
        nmr_limonene_scidata_jsonld_file, nmr_limonene_ssm_json_file
    )
