import json
import logging
import pathlib
from typing import List
import urllib


logging.basicConfig(level=logging.WARNING)


class UUIDsDoNotMatchException(Exception):
    """ Exception when UUIDs in same document do not match """


def _get_file_type(filenames: List[str], file_type: str = "") -> str:
    """
    Gets the filename that matches the file type from the list of filenames
    """
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
    """
    Return the original dictionary with the `keys` removed
    """
    return {x: d[x] for x in d if x not in keys}


def get_new_data(filenames: List[str]) -> dict:
    """
    Gest the SSM JSON filename with change set from the list of filenames
    """
    json_filename = _get_file_type(filenames, file_type=".json")
    with open(json_filename, "r") as f:
        new_data = json.load(f)
    return new_data


def get_original_data(filenames: List[str]) -> dict:
    """
    Gets the SciData JSON-LD filename to be updated from the list of filenames
    """
    jsonld_filename = _get_file_type(filenames, file_type=".jsonld")
    with open(jsonld_filename, "r") as f:
        original_data = json.load(f)
    return original_data


def merge_data_from_filenames(filenames: List[str]) -> dict:
    """
    Merges change set in SSM JSON format with SciData JSON-LD document
    """
    json_data = get_new_data(filenames)
    jsonld_data = get_original_data(filenames)

    # top-level metadata sections
    graph = jsonld_data["@graph"]
    scidata = jsonld_data["@graph"]["scidata"]
    scidata_json = json_data["scidata"]

    if "title" in json_data:
        graph["title"] = json_data.get("title")

    json_url = json_data.get("url", None)
    json_uuid = json_data.get("uuid", None)

    # ensure UUIDs from "uuid" and "url" match, otherwise raise exception
    if json_url and json_uuid:
        json_url = json_url.rstrip("/")
        json_url_path = urllib.parse.urlsplit(json_url).path
        json_uuid_from_url = pathlib.PurePosixPath(json_url_path).parts[-1]

        if json_uuid != json_uuid_from_url:
            msg = (
                f'ERROR: UUID {json_uuid} and UUID {json_uuid_from_url} '
                "from URL do not match."
            )
            raise UUIDsDoNotMatchException(msg)

    if json_url:
        jsonld_data["@id"] = json_url

    if json_uuid:
        jsonld_url = jsonld_data["@id"].rstrip('/')
        jsonld_data["@id"] = urllib.parse.urljoin(jsonld_url, json_uuid)

    if "property" in scidata_json:
        properties = scidata_json.get("property").split(',')
        scidata["property"] = properties

    if "description" in json_data:
        graph["description"] = json_data.get("description")

    # methodology

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

    if "sources" in scidata_json:
        sources_list = graph.get("sources", list())
        sources_list_json = scidata_json.get("sources")
        new_sources = list()
        for source_json in sources_list_json:
            matched = False
            for source in sources_list:
                keys = ["@id", "@type"]
                source_stripped = _without_keys(source, keys)
                key = "bibliographicCitation"
                if key in source_stripped:
                    source_stripped["citation"] = source_stripped.get(key)
                    source_stripped.pop(key)
                if "type" in source_stripped:
                    source_stripped["reftype"] = source_stripped.get("type")
                    source_stripped.pop("type")

                if source_stripped == source_json:
                    matched = True

            if not matched:
                source_json["@id"] = ""
                source_json["@type"] = "dc:source"
                new_sources.append(source_json)

        sources_list += new_sources
        scidata["sources"] = sources_list
        print(scidata["sources"])

    return jsonld_data
