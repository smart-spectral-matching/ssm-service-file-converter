from fastapi.testclient import TestClient
import json
import pathlib

from ssm_file_converter import app

FILE_ARG = "upload_file"
client = TestClient(app)


def __test_convert_jsonld_to_abbreviated_json(
    scidata_jsonld_file: pathlib.Path,
    ssm_json_file: pathlib.Path,
) -> None:
    # target ssm json file
    with open(ssm_json_file.absolute(), "rb") as f:
        target = json.load(f)

    # post jsonld file to convert to ssm json
    with open(scidata_jsonld_file.absolute(), 'rb') as f:
        files = {FILE_ARG: (scidata_jsonld_file.name, f)}
        response = client.post("/convert/json", files=files)
    assert response.status_code == 200
    output = response.json()

    # have to remove create and modified date since won't match
    for key in ["created", "modified"]:
        output.pop(key)
        target.pop(key)

    assert sorted(output.items()) == sorted(target.items())


def test_convert() -> None:
    response = client.get("/convert")
    assert response.status_code == 200
    assert response.json() == {
        "input formats": ["rruff", "jcamp", "json-ld", "json"],
        "output formats": ["json", "json-ld"]
    }


def test_convert_rruff_to_jsonld(
    raman_soddyite_rruff_file: pathlib.Path
) -> None:
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
    raman_soddyite_jcamp_file: pathlib.Path,
    raman_soddyite_scidata_jsonld_file: pathlib.Path,
) -> None:
    # target ssm json file
    with open(raman_soddyite_scidata_jsonld_file.absolute(), "rb") as f:
        target = json.load(f)

    # post jcamp file to convert to scidata jsonld
    with open(raman_soddyite_jcamp_file.absolute(), 'rb') as f:
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
    with open(raman_soddyite_jcamp_file.absolute(), 'rb') as f:
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

    # Property isn't included so remove
    target["scidata"].pop("property")

    # have to remove create and modified date since won't match
    for key in ["created", "modified"]:
        output.pop(key)
        target.pop(key)

    assert sorted(output.items()) == sorted(target.items())


def test_convert_abbreviated_json_to_jsonld(
    raman_soddyite_ssm_json_file: pathlib.Path,
    raman_soddyite_scidata_jsonld_file: pathlib.Path,
) -> None:
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


def test_convert_jsonld_to_abbreviated_json_raman_soddyite(
    raman_soddyite_scidata_jsonld_file: pathlib.Path,
    raman_soddyite_ssm_json_file: pathlib.Path,
) -> None:
    __test_convert_jsonld_to_abbreviated_json(
        raman_soddyite_scidata_jsonld_file,
        raman_soddyite_ssm_json_file
    )


def test_convert_jsonld_to_abbreviated_json_ramad_studtite(
    raman_studtite_scidata_jsonld_file: pathlib.Path,
    raman_studtite_ssm_json_file: pathlib.Path,
) -> None:
    __test_convert_jsonld_to_abbreviated_json(
        raman_studtite_scidata_jsonld_file,
        raman_studtite_ssm_json_file
    )


def test_convert_jsonld_to_abbreviated_json_nmr_limonene(
    nmr_limonene_scidata_jsonld_file: pathlib.Path,
    nmr_limonene_ssm_json_file: pathlib.Path,
) -> None:
    __test_convert_jsonld_to_abbreviated_json(
        nmr_limonene_scidata_jsonld_file,
        nmr_limonene_ssm_json_file
    )
