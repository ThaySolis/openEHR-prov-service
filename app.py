import flask

from data_layer import path_utils
from presentation_layer import prov_routes, timing_routes
from app_settings import SERVER_PORT, PLAIN_HTTP, INCLUDE_USAGE_STATISTICS

server = flask.Flask(__name__)

server.register_blueprint(prov_routes.blueprint)

if INCLUDE_USAGE_STATISTICS:
    server.register_blueprint(timing_routes.blueprint)

if __name__ == "__main__":
    if PLAIN_HTTP:
        # Simply run the server.
        server.run(host="0.0.0.0", port=SERVER_PORT)
    else:
        # Get the path to the SSL files.
        certificate_path = path_utils.relative_path("certificate", "api-cert.pem")
        key_path = path_utils.relative_path("certificate", "api-key.pem")

        # Run the server with the SSL files.
        server.run(host="0.0.0.0", port=SERVER_PORT, ssl_context=(certificate_path, key_path))
