from flask import Flask, request, Response
from typing import List, Tuple
import requests
import json
import torch


def create_application() -> Flask:
    app = Flask(__name__)

    @app.route("/api/<resource_type>", methods=["POST"])
    def post_resource(resource_type):
        return resource_type

    @app.route("/api", methods=["GET"])
    def get_resources():
        return "Basic API Gateway torch: " + str(torch.__version__)

    return app


if __name__ == "__main__":
    app = create_application()
    app.run("0.0.0.0", port=5000, debug=True)
