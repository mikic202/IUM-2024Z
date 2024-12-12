from flask import Flask, request, Response
from typing import List, Tuple
import requests
import json


def create_application() -> Flask:
    app = Flask(__name__)

    @app.route("/api/<resource_type>", methods=["POST"])
    def post_resource(resource_type):
        return Response()

    @app.route("/api/<resource_type>", methods=["GET"])
    def get_resources(resource_type):

        return Response()

    return app


if __name__ == "__main__":
    app = create_application()
    app.run("0.0.0.0", port=5001, debug=True)
