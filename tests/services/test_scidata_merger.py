import json
import pytest
import tempfile

from ssm_file_converter.services.scidata_merger import (
    _get_file_type,
    _without_keys,
    get_new_data,
    get_original_data,
    merge_data_from_filenames,
    UUIDsDoNotMatchException,
)


@pytest.fixture(name="json_data")
def fixture__json_data() -> dict:
    json_data = {
        "title": "NEW TITLE",
        "scidata": {
            "system": {
                "facets": [
                    {"bird type": "flamingo"}
                ]
            }
        }
    }
    return json_data


def create_json_file(data: dict) -> str:
    json_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False
    )
    json.dump(data, json_file)
    json_file.flush()
    return json_file.name


@pytest.fixture(name="jsonld_filename")
def fixture_jsonld_filename(raman_soddyite_scidata_jsonld_file) -> str:
    with open(raman_soddyite_scidata_jsonld_file.absolute(), "r") as f:
        data = json.load(f)
    data.get("@graph").get("scidata").pop("system")
    jsonld_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".jsonld",
        delete=False
    )
    json.dump(data, jsonld_file)
    jsonld_file.flush()
    return jsonld_file.name


def test_without_keys() -> None:
    a = {"foo": 1, "bar": 2}
    assert _without_keys(a, ["foo"]) == {"bar": 2}


def test_get_file_type(jsonld_filename: str, json_data: dict) -> None:
    json_filename = create_json_file(json_data)
    filenames = [jsonld_filename, json_filename]
    assert _get_file_type(filenames, file_type=".jsonld") == jsonld_filename
    assert _get_file_type(filenames, file_type=".json") == json_filename


def test_get_new_data(jsonld_filename: str, json_data: dict) -> None:
    json_filename = create_json_file(json_data)
    filenames = [jsonld_filename, json_filename]
    output = get_new_data(filenames)

    with open(json_filename, 'rb') as f:
        target = json.load(f)

    assert sorted(output.items()) == sorted(target.items())


def test_get_new_data_bad_filenames() -> None:
    filenames = [
        "a.txt",
        "b.txt",
    ]

    with pytest.raises(Exception):
        get_new_data(filenames)


def test_get_original_data(jsonld_filename: str, json_data: dict) -> None:
    json_filename = create_json_file(json_data)
    filenames = [jsonld_filename, json_filename]
    output = get_original_data(filenames)

    with open(jsonld_filename, "rb") as f:
        target = json.load(f)

    assert sorted(output.items()) == sorted(target.items())


def test_get_original_data_bad_filenames() -> None:
    filenames = [
        "a.txt",
        "b.txt",
    ]

    with pytest.raises(Exception):
        get_original_data(filenames)


def test_merge_data_from_filenames(
    jsonld_filename: str,
    json_data: dict,
) -> None:
    json_filename = create_json_file(json_data)
    filenames = [jsonld_filename, json_filename]
    output = merge_data_from_filenames(filenames)

    assert output.get("@graph").get("title") == "NEW TITLE"

    system_target = {
        "facets": [{"@id": "", "@type": "", "bird type": "flamingo"}]
    }
    scidata = output.get("@graph").get("scidata")
    assert scidata.get("system") == system_target
    scidata.pop("system")

    # Remove different title to see if rest of JSON-LD matches
    target = get_original_data(filenames)
    for f in [output, target]:
        graph = f.get("@graph")
        graph.pop("title")

    assert sorted(output.items()) == sorted(target.items())


def test_merge_data_from_filenames_with_uuid(
    jsonld_filename: str,
    json_data: dict
) -> None:
    json_data["uuid"] = "FOO"
    json_filename = create_json_file(json_data)
    filenames = [jsonld_filename, json_filename]
    output = merge_data_from_filenames(filenames)
    assert output["@id"] == json_data["uuid"]


def test_merge_data_from_filenames_with_url(
    jsonld_filename: str,
    json_data: dict
) -> None:
    json_data["url"] = "https://path.to.url/FOO"
    json_filename = create_json_file(json_data)
    filenames = [jsonld_filename, json_filename]
    output = merge_data_from_filenames(filenames)
    assert output["@id"] == json_data["url"]


def test_merge_data_from_filenames_exception_uuids_not_matching(
    jsonld_filename: str,
    json_data: dict
) -> None:
    json_data["uuid"] = "FOO"
    json_data["url"] = "https://url.to.data/BAR"
    json_filename = create_json_file(json_data)
    filenames = [jsonld_filename, json_filename]
    with pytest.raises(UUIDsDoNotMatchException):
        merge_data_from_filenames(filenames)
