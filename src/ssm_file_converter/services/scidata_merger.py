import json
import logging
import pathlib
from typing import List


logging.basicConfig(level=logging.WARNING)


def _get_file_type(filenames: List[str], file_type: str = "") -> str:
    output = None
    for filename in filenames:
        file_extension = pathlib.Path(filename).suffix
        if file_extension == file_type:
            output = filename
            break

    if not output:
        raise Exception("ERROR: No {file_type} file provided for merging")

    return output


def _without_keys(d: dict, keys: list) -> dict:
    return {x: d[x] for x in d if x not in keys}


def get_new_data(filenames: List[str]) -> dict:
    json_filename = _get_file_type(filenames, file_type=".json")
    with open(json_filename, "r") as f:
        new_data = json.load(f)
    return new_data


def get_original_data(filenames: List[str]) -> dict:
    jsonld_filename = _get_file_type(filenames, file_type=".jsonld")
    with open(jsonld_filename, "r") as f:
        original_data = json.load(f)
    return original_data


def merge_data_from_filenames(filenames: List[str]) -> dict:
    json_data = get_new_data(filenames)
    jsonld_data = get_original_data(filenames)

    graph = jsonld_data["@graph"]
    if "title" in json_data:
        graph["title"] = json_data.get("title")

    if "url" in json_data:
        jsonld_data["@id"] = json_data.get("url")

    scidata = jsonld_data["@graph"]["scidata"]
    scidata_json = json_data["scidata"]

    if "methodology" in scidata_json:
        if "methodology" not in scidata:
            scidata["methodology"] = dict()

        methodology = scidata.get("methodology")
        methodology_json = scidata_json.get("methodology")

        if "evaluationMethod" in methodology_json:
            evaluationMethod = methodology_json.get("evaluationMethod")
            methodology["evaluation"] = evaluationMethod

        if "aspects" in methodology_json:
            aspects_list = methodology.get("aspects", list())
            aspects_list_json = methodology_json.get("aspects")
            new_aspects = list()
            for aspect_json in aspects_list_json:

                matched = False

                for aspect in aspects_list:
                    keys = ["@id", "@type"]
                    aspect_stripped = _without_keys(aspect, keys)
                    if aspect_stripped == aspect_json:
                        matched = True

                if not matched:
                    aspect_json["@id"] = ""
                    aspect_json["@type"] = ""
                    new_aspects.append(aspect_json)

            aspects_list += new_aspects
            methodology["aspects"] = aspects_list

        if "hasMethodologyAspect" in methodology_json:
            warning = 'Cannot parse "hasMethodologyAspect", skipping...'
            logging.warning(warning)

    if "system" in scidata_json:
        if "system" not in scidata:
            scidata["system"] = dict()

        system = scidata.get("system")
        system_json = scidata_json.get("system")

        if "facets" in system_json:
            facets_list = system.get("facets", list())
            facets_list_json = system_json.get("facets")
            new_facets = list()

            for facet_json in facets_list_json:
                matched = False
                for facet in facets_list:
                    keys = ["@id", "@type"]
                    facet_stripped = _without_keys(facet, keys)
                    if facet_stripped == facet_json:
                        matched = True

                if not matched:
                    facet_json["@id"] = ""
                    facet_json["@type"] = ""
                    new_facets.append(facet_json)

            facets_list += new_facets
            system["facets"] = facets_list

    return jsonld_data
