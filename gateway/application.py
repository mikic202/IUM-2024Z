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

    @app.route("/api/user_model/update_user_preferences", methods=["POST"])
    def update_user_preferences():
        return "!! NOT IMPLEMENTED !!"

    @app.route("/api/user_model/<model_tpye>/get_user_recomendations", methods=["GET"])
    def get_user_recomendations(model_tpye):
        return "!! NOT IMPLEMENTED !!"

    @app.route("/api/embedding", methods=["POST"])
    def create_embeddings():
        try:
            # Wczytanie danych z pliku .jsonl
            tracks = list(read_jsonl('/app/data/tracks_artists.jsonl'))
            embeddings = []

            # Wysyłanie każdego utworu do torchserve
            for track in tracks:

                # Przygotowanie danych w formacie oczekiwanym przez model API
                fields = [
                    "id_track", "popularity", "duration_ms", "explicit", "release_date",
                    "danceability", "energy", "key", "loudness", "speechiness", "acousticness",
                    "instrumentalness", "liveness", "valence", "tempo", "type_hot_one",
                    "id_artist_hash", "genre_hot_one"
                ]

                data = {field: track[field] for field in fields}

                # Wysłanie danych do modelu API
                response = requests.post(
                    "http://ium-2024z-model_api-1:8080/predictions/embeding_model",
                    json={"data": data},
                    headers={"Content-Type": "application/json"}
                )

                # Jeśli odpowiedź jest poprawna
                if response.status_code == 200:
                    embedding = response.json()
                    print("Embedding received:", embedding)
                    embeddings.append({
                        "id_track": track.get("id_track"),
                        "embedding": embedding
                    })
                else:
                    embeddings.append({
                        "id_track": track.get("id_track"),
                        "error": "Failed to get embedding"
                    })

            # Zapisanie embeddingów do pliku JSON w folderze data_v2
            with open("/app/data/embeddings.json", "w") as f:
                json.dump(embeddings, f, indent=4)

            return Response(
                json.dumps({"status": "success", "embeddings": embeddings}),
                mimetype="application/json",
                status=200
            )
        except Exception as e:
            return Response(
                json.dumps({"status": "error", "message": str(e)}),
                mimetype="application/json",
                status=500
            )

    return app

def read_jsonl(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            yield json.loads(line)


if __name__ == "__main__":
    app = create_application()
    app.run("0.0.0.0", port=5001, debug=True)
