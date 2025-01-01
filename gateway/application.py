from flask import Flask, request, Response
from typing import List, Tuple
import requests
import json
import glob
import random
import re
from datetime import datetime
import math
from Gateway import Gateway


BASE_DATE = datetime.strptime("2025-01-03", "%Y-%m-%d").timestamp()


def create_application() -> Flask:
    app = Flask(__name__)

    return app


if __name__ == "__main__":
    app = create_application()
    gateway = Gateway(app)
    gateway.run("0.0.0.0", port=5001, debug=True)
