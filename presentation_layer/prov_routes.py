from flask import Blueprint, request, Response

from authentication import auth
from business_layer import prov_controller, controller_exceptions
from business_layer.timing import timed, GET_PROVENANCE_MEASUREMENT

blueprint = Blueprint("PROV routes", __name__)

@blueprint.route("/provenance/service", methods=["GET"])
@timed.measure(GET_PROVENANCE_MEASUREMENT)
@auth.login_required
def get_provenance():
    """
    Gets the provenance of the resource identified by the URI on the 'target' query parameter.

    If the URI is not provided, this function return a 400 (Bad Request) response.

    If the URI does not correspond to an EHR_STATUS, COMPOSITION or patient, this function returns a 404 (Not Found) response.

    Returns:
        The HTTP response.
    """

    uri = request.args.get("target", None)

    if uri is None:
        return Response(status = 400)

    try:
        prov_document = prov_controller.get_provenance(uri)
    except (controller_exceptions.InvalidURIException, controller_exceptions.NoSuchVersionedObjectException):
        return Response(status = 404)
    except controller_exceptions.InternalException:
        return Response(status = 500)

    xml = prov_document.serialize(format="xml")
    return Response(status = 200, content_type="text/xml", response = xml)
