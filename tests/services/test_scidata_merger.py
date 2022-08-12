import json
import pytest
import tempfile

from ssm_file_converter.services.scidata_merger import (
    _get_file_type,
    _without_keys,
    get_new_data,
    get_original_data,
    merge_data_from_filenames,
)


@pytest.fixture(name="json_filename")
def fixture__json_filename() -> str:
    new_data = {
        "title": "NEW TITLE",
        "scidata": {
            "system": {
                "facets": [
                    {"bird type": "flamingo"}
                ]
            }
        }
    }
    json_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False
    )
    json.dump(new_data, json_file)
    json_file.flush()
    return json_file.name


@pytest.fixture(name="jsonld_filename")
def fixture_jsonld_filename(raman_soddyite_scidata_jsonld_file) -> str:
    jsonld_filename = raman_soddyite_scidata_jsonld_file.absolute()
    return jsonld_filename


def test_without_keys() -> None:
    a = {"foo": 1, "bar": 2}
    assert _without_keys(a, ["foo"]) == {"bar": 2}


def test_get_file_type(jsonld_filename, json_filename) -> None:
    filenames = [jsonld_filename, json_filename]
    assert _get_file_type(filenames, file_type=".jsonld") == jsonld_filename
    assert _get_file_type(filenames, file_type=".json") == json_filename


def test_get_new_data(jsonld_filename, json_filename) -> None:
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


def test_get_original_data(jsonld_filename, json_filename) -> None:
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


def test_merge_data_from_filenames(jsonld_filename, json_filename) -> None:
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
