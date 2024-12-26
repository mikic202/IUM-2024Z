from flask import Flask, request, Response
from typing import List, Tuple
import requests
import json
import glob

PREDICTION_TYPES = ["classification", "regression"]


def create_application() -> Flask:
    app = Flask(__name__)

    @app.route("/api/status", methods=["GET"])
    def get_resources():
        return requests.get("http://model_api:8080/ping").text

    @app.route("/api/predict/<prediction_type>", methods=["POST"])
    def predict(prediction_type):
        return "!! NOT IMPLEMENTED !!"

    @app.route("/api/user_model/update_user_preferences", methods=["GET"])
    def update_user_preferences():
        user_preferences = []
        for user_id in range(101, 1101):
            user_preferences.append(
                {
                    "preferences": get_user_preferences_from_model(user_id),
                    "user_id": user_id,
                }
            )

        json.dump(
            user_preferences, open("/app/data/user_preferences.json", "w"), indent=4
        )
        return Response(
            json.dumps({"status": "success", "user_preferences": user_preferences}),
            mimetype="application/json",
            status=200,
        )

    @app.route("/api/user_model/<user_id>/get_user_preferences", methods=["GET"])
    def get_user_preferences(user_id: int):
        user_preferences = json.load(open("/app/data/user_preferences.json", "r"))
        for user_preference in user_preferences:
            if int(user_preference["user_id"]) == int(user_id):
                return user_preference
        return {"error": f"User {user_id} not found"}

    @app.route("/api/user_model/<model_tpye>/get_user_recomendations", methods=["GET"])
    def get_user_recomendations(model_tpye):
        return "!! NOT IMPLEMENTED !!"

    @app.route("/api/embedding", methods=["POST"])
    def create_embeddings():
        try:
            # Wczytanie danych z pliku .jsonl
            tracks = list(read_jsonl("/app/data/tracks_artists.jsonl"))
            embeddings = []

            # Wysyłanie każdego utworu do torchserve
            for track in tracks:

                # Przygotowanie danych w formacie oczekiwanym przez model API
                fields = [
                    "id_track",
                    "popularity",
                    "duration_ms",
                    "explicit",
                    "release_date",
                    "danceability",
                    "energy",
                    "key",
                    "loudness",
                    "speechiness",
                    "acousticness",
                    "instrumentalness",
                    "liveness",
                    "valence",
                    "tempo",
                    "type_hot_one",
                    "id_artist_hash",
                    "genre_hot_one",
                ]

                data = {field: track[field] for field in fields}

                # Wysłanie danych do modelu API
                response = requests.post(
                    "http://ium-2024z-model_api-1:8080/predictions/embeding_model",
                    json={"data": data},
                    headers={"Content-Type": "application/json"},
                )

                # Jeśli odpowiedź jest poprawna
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

            # Zapisanie embeddingów do pliku JSON w folderze data_v2
            with open("/app/data/embeddings.json", "w") as f:
                json.dump(embeddings, f, indent=4)

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

    return app


def read_jsonl(file_path):
    with open(file_path, "r") as f:
        for line in f:
            yield json.loads(line)


def get_user_preferences_from_model(user_id: int):
    user_sessions = glob.glob(f"/app/data/sessions/sessions_user_{user_id}.jsonl")
    if len(user_sessions) != 1:
        raise ValueError(f"User {user_id} has {len(user_sessions)} sessions")
    user_sessions = list(read_jsonl(user_sessions[0]))
    dummy_user_preference = [0] * 8
    # here sending requests to model and returning user preferences
    return dummy_user_preference


if __name__ == "__main__":
    app = create_application()
    app.run("0.0.0.0", port=5001, debug=True)
