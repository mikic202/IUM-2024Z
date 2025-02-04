from flask import Response, Flask
import requests
import math
import random
from datetime import datetime
import glob
import json
from pathlib import Path

from helpers.read_jsinl import read_jsonl
from recomendation_generators.ComplexRecomendationsGenerator import (
    ComplexRecomendationsGenerator,
)
from recomendation_generators.SimpleRecomendationsGenerator import (
    SimpleRecomendationsGenerator,
)


BASE_DATE = datetime.strptime("2025-01-03", "%Y-%m-%d").timestamp()

MODEL_API_URL = "http://model_api:8080"

RECOMENDED_TRACKS = 5
COMPLEX_MODEL_CONTEXT_WINDOW = 50


class Gateway:
    def __init__(self, app: Flask, **configs) -> None:
        self.app = app
        self.configs(**configs)
        with open("/app/data/embeddings.json") as f:
            self.embeddings = json.load(f)
        self.add_endpoint("/api/status", "api/status", self.get_status, methods=["GET"])
        self.add_endpoint(
            "/api/user_model/<user_id>/get_user_preferences",
            "api/user_model/get_user_preferences",
            self.get_user_preferences,
            methods=["GET"],
        )
        self.add_endpoint(
            "/api/user_model/get_user_recomendations/<user_id>",
            "api/user_model/get_user_recomendations",
            self.get_user_recomendations,
            methods=["GET"],
        )
        self.add_endpoint("/api/test", "api/test", self.get_test_data, methods=["GET"])
        self.add_endpoint(
            "/api/embedding", "api/embedding", self.create_embeddings, methods=["POST"]
        )
        self.add_endpoint(
            "/api/user_model/update_user_preferences",
            "api/user_model/update_user_preferences",
            self.update_user_preferences,
            methods=["POST"],
        )

    def configs(self, **configs):
        for config, value in configs:
            self.app.config[config.upper()] = value

    def add_endpoint(
        self,
        endpoint=None,
        endpoint_name=None,
        handler=None,
        methods=["GET"],
        *args,
        **kwargs,
    ):
        self.app.add_url_rule(
            endpoint, endpoint_name, handler, methods=methods, *args, **kwargs
        )

    def get_status(self):
        return requests.get(MODEL_API_URL + "/ping").text

    def get_user_preferences(self, user_id: int):
        user_preferences = json.load(open("/app/data/user_preferences.json", "r"))
        for user_preference in user_preferences:
            if int(user_preference["user_id"]) == int(user_id):
                return Response(
                    json.dumps(user_preference),
                    mimetype="application/json",
                    status=200,
                )
        return Response(
            {"status": "error", "message": f"User {user_id} not found"},
            status=404,
            mimetype="application/json",
        )

    def get_user_recomendations(self, user_id: int):
        random.seed(datetime.now().timestamp())
        if hash(str(user_id)) % 2 == 0:
            model_type = "simple"
            user_data = list(read_jsonl("/app/data/users.jsonl"))
            user = next(
                item for item in user_data if int(item["user_id"]) == int(user_id)
            )
            recomendations = SimpleRecomendationsGenerator(
                Path("/app/data/sessions/sessions_user_"),
                Path("/app/data/tracks_artists.jsonl"),
            ).generate_recomendations(
                user_id,
                self.embeddings.copy(),
                RECOMENDED_TRACKS,
                user["genre_hot_one"],
            )
        else:
            model_type = "complex"
            recomendations = ComplexRecomendationsGenerator(
                Path("/app/data/user_preferences.json")
            ).generate_recomendations(
                user_id,
                self.embeddings.copy(),
                RECOMENDED_TRACKS,
            )

        self.log_experiment_result(
            user_id, model_type, recomendations, "success", "ab_experiment_log"
        )
        return Response(
            json.dumps({"status": "success", "recomended_tracks": recomendations}),
            mimetype="application/json",
            status=200,
        )

    def get_test_data(self):
        try:
            for user_sesion_file in glob.glob(
                "/app/data/sessions/sessions_user_*.jsonl"
            ):
                user_id = int(user_sesion_file.split("_")[-1].split(".")[0])
                try:
                    self.get_user_recomendations(user_id)

                except Exception as e:
                    json.dumps({"user_id": user_id, "status": f"error: {str(e)}"}),
                    mimetype = ("application/json",)
                    status = 404

            return Response(
                json.dumps({"status": "success"}),
                mimetype="application/json",
                status=200,
            )

        except Exception as e:
            return Response(
                json.dumps({"status": "error", "message": str(e)}),
                mimetype="application/json",
                status=500,
            )

    def log_experiment_result(
        self,
        user_id: int,
        model_type: str,
        recommended_tracks: list,
        status: str,
        filename: str,
    ):
        log_data = {
            "user_id": user_id,
            "model_type": model_type,
            "timestamp": datetime.now().isoformat(),
            "recommended_tracks": recommended_tracks,
            "status": status,
        }

        with open(f"/app/data/{filename}.jsonl", "a") as log_file:
            log_file.write(json.dumps(log_data) + "\n")

    def run(self, address, port, debug=False):
        self.app.run(address, port=port, debug=debug)

    def create_embeddings(self):
        try:
            tracks = list(read_jsonl("/app/data/tracks_artists.jsonl"))
            embeddings = []

            fields = tracks[0].keys()

            for track in tracks:

                data = {field: track[field] for field in fields}
                response = requests.post(
                    MODEL_API_URL + "/predictions/embeding_model",
                    json={"data": data},
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    embedding = response.json()
                    print("Embedding received:", embedding)
                    embeddings.append(
                        {"id_track": track.get("id_track"), "embedding": embedding}
                    )
                else:
                    embeddings.append(
                        {
                            "id_track": track.get("id_track"),
                            "error": "Failed to get embedding",
                        }
                    )

            with open("/app/data/embeddings.json", "w") as f:
                json.dump(embeddings, f, indent=4)

            self.embeddings = embeddings

            return Response(
                json.dumps({"status": "success", "embeddings": embeddings}),
                mimetype="application/json",
                status=200,
            )
        except Exception as e:
            return Response(
                json.dumps({"status": "error", "message": str(e)}),
                mimetype="application/json",
                status=500,
            )

    def update_user_preferences(self):
        user_preferences = []
        try:
            user_sesions_files = glob.glob("/app/data/sessions/sessions_user_*.jsonl")

            user_preferences = [
                {
                    "preferences": self.get_user_preferences_from_model(user_id),
                    "user_id": user_id.split("_")[-1].split(".")[0],
                }
                for user_id in user_sesions_files
            ]
            json.dump(
                user_preferences, open("/app/data/user_preferences.json", "w"), indent=4
            )
        except Exception:
            return Response(
                json.dumps({"status": "error"}),
                mimetype="application/json",
                status=500,
            )
        return Response(
            json.dumps(
                {
                    "status": "success",
                    "message": "Updated user preferences for all users in the database",
                }
            ),
            mimetype="application/json",
            status=200,
        )

    def transform_event_type_to_one_hot(self, event_type: str) -> list[int]:
        if event_type not in ["like", "play", "skip"]:
            raise ValueError(f"Event type {event_type} not supported")
        return [
            1.0 if event_type == "like" else 0.0,
            1.0 if event_type == "play" else 0.0,
            1.0 if event_type == "skip" else 0.0,
        ]

    def process_user_sesions(
        self, sessions: list[dict]
    ) -> tuple[list[dict], list[dict]]:
        for sesion in sessions:
            tracks_embedings = list(
                filter(lambda x: x["id_track"] == sesion["track_id"], self.embeddings)
            )[0]
            sesion["timestamp"] = (
                datetime.strptime(
                    sesion["timestamp"], "%Y-%m-%dT%H:%M:%S.%f"
                ).timestamp()
                / BASE_DATE
            )
            sesion["embeding"] = tracks_embedings["embedding"]
            sesion["embeding"] = [float(x) for x in sesion["embeding"]]
            sesion["event_type"] = self.transform_event_type_to_one_hot(
                sesion["event_type"]
            )
        return sessions

    def get_user_preferences_from_model(self, user_sessions_file: str):
        user_sessions = sorted(
            [sesion for sesion in read_jsonl(user_sessions_file)],
            key=lambda x: x["timestamp"],
        )[:COMPLEX_MODEL_CONTEXT_WINDOW]
        user_sessions = self.process_user_sesions(user_sessions)
        response = requests.post(
            MODEL_API_URL + "/predictions/recomendations_model",
            json={"data": user_sessions},
            headers={"Content-Type": "application/json"},
        )
        return response.json()
