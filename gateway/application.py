from flask import Flask, request, Response
from typing import List, Tuple
import requests
import json

PREDICTION_TYPES = ["classification", "regression"]


def create_application() -> Flask:
    app = Flask(__name__)

    @app.route("/api/status", methods=["GET"])
    def get_resources():
        return requests.get("http://model_api:8080/ping").text

    @app.route("/api/predict/<prediction_type>", methods=["POST"])
    def predict(prediction_type):
        return "!! NOT IMPLEMENTED !!"

    return app


if __name__ == "__main__":
    app = create_application()
    app.run("0.0.0.0", port=5001, debug=True)
