from flask import Blueprint, Response
import json

from business_layer import timing_controller

blueprint = Blueprint("timing routes", __name__)

@blueprint.route("/usage_statistics", methods=["GET"])
def get_usage_statistics():
    report = {
        "usage_statistics": timing_controller.get_usage_statistics()
    }

    return Response(
        status = 200,
        response=json.dumps(report, indent=2),
        mimetype="application/json"
    )

@blueprint.route("/usage_statistics", methods=["DELETE"])
def clear_usage_statistics():
    timing_controller.clear_usage_statistics()

    return Response(status = 204)
