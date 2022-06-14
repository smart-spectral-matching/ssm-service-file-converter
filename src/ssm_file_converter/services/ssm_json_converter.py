from scidatalib.scidata import SciData


def scidata_to_ssm_json(scidata: SciData) -> dict:
    # Convert from SciData JSON-LD to SSM abbreviated JSON
    output = dict()
    output["title"] = scidata.output["@graph"]["title"]
    if scidata.output["@id"]:
        output["url"] = scidata.output["@id"]
    output["created"] = scidata.output["generatedAt"]
    output["modified"] = scidata.output["generatedAt"]

    sd = scidata.output["@graph"]["scidata"]

    #   methodology
    methodology = sd.get("methodology", None)

    if methodology:
        output_methodology = dict()

        evaulation = methodology.get("evaluation", None)
        if evaulation:
            output_methodology["evaultionMethod"] = evaulation

        aspects_list = methodology.get("aspects", list())
        if aspects_list:
            output_aspect_list = list()
            for aspect in aspects_list:
                aspect.pop("@id")
                aspect.pop("@type")
                output_aspect_list.append(aspect)

            if output_aspect_list:
                for aspect_dict in output_aspect_list:
                    for k, v in aspect_dict.items():
                        output_methodology[k] = v

        output["methodology"] = output_methodology

    #   system
    system = sd.get("system", None)
    if system:
        output_system = dict()

        facets_list = system.get("facets", list())
        if facets_list:
            output_facet_list = list()
            for facet in facets_list:
                facet.pop("@id")
                facet.pop("@type")
                output_facet_list.append(facet)

            if output_facet_list:
                for facet_dict in output_facet_list:
                    for k, v in facet_dict.items():
                        output_system[k] = v

        output["system"] = output_system

    #   dataset
    dataset = sd.get("dataset", None)
    if dataset:

        dataseries_list = dataset.get("dataseries", list())
        if dataseries_list:
            output_dataseries_list = list()
            for dataseries in dataseries_list:
                output_dataseries = dict()

                label = dataseries.get("label", None)
                if label:
                    output_dataseries["label"] = label

                parameter_list = dataseries.get("parameter", None)
                if parameter_list:
                    for i, parameter in enumerate(parameter_list):
                        output_parameter = dict()

                        parameter.pop("@id")
                        parameter.pop("@type")

                        quantity = parameter.get("quantity", None)
                        if quantity:
                            output_parameter["quantity"] = quantity

                        sd_property = parameter.get("property", None)
                        if sd_property:
                            output_parameter["property"] = sd_property

                        units = parameter.get("units", None)
                        if units:
                            output_parameter["units"] = units

                        datatype = parameter.get("datatype", None)
                        if datatype:
                            output_parameter["datatype"] = datatype

                        dataarray = parameter.get("dataarray", None)
                        if dataarray:
                            output_parameter["numericValueArray"] = [
                                {"numberArray": dataarray}
                            ]

                        axis = parameter.get("axis", f"axis-{i}")
                        output_dataseries_list.append({
                            f'{axis}': {"parameter": output_parameter},
                            "hasAxisType": axis
                        })

        output_dataseries = output_dataseries_list
        output["dataseries"] = output_dataseries
        # TODO: need to fix that we use 'dataseries' instead of 'dataset'

    return output
