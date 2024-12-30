from flask import Flask, request, Response
from typing import List, Tuple
import requests
import json
import glob
import random
import re
from datetime import datetime
import math


def get_embeding_to_compare_for_advanced_model(user_id: int):
    user_preferences = json.load(open("/app/data/user_preferences.json", "r"))
    for user_preference in user_preferences:
        if int(user_preference["user_id"]) == int(user_id):
            return user_preference["preferences"][0]
    return None

def get_embeding_to_compare_for_simple_model(user_id: int):
    track_embeddings = json.load(open("/app/data/embeddings.json", 'r'))
    user_session = list(read_jsonl(f'/app/data/sessions/sessions_user_{user_id}.jsonl'))

    filtered_data = [session for session in user_session if session['event_type'] == 'like']
    last_liked_track = max(filtered_data, key=lambda x: x['timestamp'])    
    last_track_id = last_liked_track['track_id']
    track_row = next((track for track in track_embeddings if track["id_track"] == last_track_id), None)
    embedding_last_liked = track_row['embedding']
    return (embedding_last_liked, last_track_id)



MODEL_TYPES = {"simple": get_embeding_to_compare_for_simple_model, "complex": get_embeding_to_compare_for_advanced_model}
BASE_DATE = datetime.strptime("2025-01-03", "%Y-%m-%d").timestamp()


def create_application() -> Flask:
    app = Flask(__name__)

    @app.route("/api/status", methods=["GET"])
    def get_resources():
        return requests.get("http://model_api:8080/ping").text

    @app.route("/api/user_model/update_user_preferences", methods=["POST"])
    def update_user_preferences():
        user_preferences = []
        try:
            user_sesions_files = glob.glob("/app/data/sessions/sessions_user_*.jsonl")
            user_preferences = [
                {
                    "preferences": get_user_preferences_from_model(user_id),
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

    @app.route("/api/user_model/<user_id>/get_user_preferences", methods=["GET"])
    def get_user_preferences(user_id: int):
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

    @app.route(
        "/api/user_model/<model_type>/get_user_recomendations/<user_id>",
        methods=["GET"],
    )
    def get_user_recomendations(model_type: str, user_id: int):
        if model_type not in MODEL_TYPES:
            return Response(
                json.dumps({"status": "error", "message": "Model type not found"}),
                mimetype="application/json",
                status=400,
            )
        embeding_to_compare = MODEL_TYPES[model_type](user_id)
        with open("/app/data/embeddings.json") as f:
            embeddings = json.load(f)
        if model_type == "simple":
            user_data = list(read_jsonl("/app/data/users.jsonl")) 
            tracks_data = list(read_jsonl('/app/data/tracks_artists.jsonl'))
    
            new_embeddings = []
            id_track = embeding_to_compare[1]
            embeding_to_compare = embeding_to_compare[0]
            user = next(item for item in user_data if int(item['user_id']) == int(user_id))
            user_genre = user['genre_hot_one']
            for i, row in enumerate(embeddings):
                if row['id_track'] == id_track:
                    continue
                track_genre = tracks_data[i]['genre_hot_one']
                if any(u == 1 and t == 1 for u, t in zip(user_genre, track_genre)):
                    new_embeddings.append(row)
            embeddings = new_embeddings


        best_tracks = sorted(
            list(embeddings),
            key=lambda x: abs(math.dist(x["embedding"], embeding_to_compare)),
        )[:20]
        return Response(
            json.dumps({"status": "success", "recomended_tracks": best_tracks}),
            mimetype="application/json",
            status=200,
        )
    
    @app.route("/api/ab_test/<user_id>", methods=["GET"])
    def ab_test(user_id: int):
        model_type = random.choice(["simple", "complex"])
        try:
            response = get_user_recomendations(model_type, user_id)
            
            response_data = json.loads(response.data)
            recommended_tracks = response_data.get("recomended_tracks", [])

            if recommended_tracks:
                best_track = recommended_tracks[0]
                log_experiment_result(user_id, model_type, best_track, "success")
            else:
                log_experiment_result(user_id, model_type, {}, "no_tracks_found")

            return response
            
        except Exception as e:
            log_experiment_result(user_id, model_type, {}, f"error: {str(e)}")
            
            return Response(
                json.dumps({"status": "error", "message": str(e)}),
                mimetype="application/json",
                status=500,
            )



    @app.route("/api/embedding", methods=["POST"])
    def create_embeddings():
        try:
            tracks = list(read_jsonl("/app/data/tracks_artists.jsonl"))
            embeddings = []

            for track in tracks:

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

                response = requests.post(
                    "http://ium-2024z-model_api-1:8080/predictions/embeding_model",
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

# Funkcja do zapisania danych logów
def log_experiment_result(user_id: int, model_type: str, recommended_tracks: list, status: str):
    log_data = {
        "user_id": user_id,
        "model_type": model_type,
        "timestamp": datetime.now().isoformat(),
        "recommended_tracks": recommended_tracks,
        "status": status
    }

    # Zapisywanie do pliku logu
    with open("/app/data/ab_experiment_log.json", "a") as log_file:
        log_file.write(json.dumps(log_data) + "\n")



def read_jsonl(file_path):
    with open(file_path, "r") as f:
        for line in f:
            yield json.loads(line)


def transform_event_type_to_one_hot(event_type: str) -> List[int]:
    if event_type not in ["like", "play", "skip"]:
        raise ValueError(f"Event type {event_type} not supported")
    return [
        1.0 if event_type == "like" else 0.0,
        1.0 if event_type == "play" else 0.0,
        1.0 if event_type == "skip" else 0.0,
    ]


def process_sesions(sessions: List[dict]) -> Tuple[List[dict], List[dict]]:
    with open("/app/data/embeddings.json") as f:
        embeddings = json.load(f)
    for sesion in sessions:
        tracks_embedings = list(
            filter(lambda x: x["id_track"] == sesion["track_id"], embeddings)
        )[0]
        sesion["timestamp"] = (
            datetime.strptime(sesion["timestamp"], "%Y-%m-%dT%H:%M:%S.%f").timestamp()
            / BASE_DATE
        )
        sesion["embeding"] = tracks_embedings["embedding"]
        sesion["embeding"] = [float(x) for x in sesion["embeding"]]
        sesion["event_type"] = transform_event_type_to_one_hot(sesion["event_type"])
    return sessions


def get_user_preferences_from_model(user_sessions_file: str):
    user_sessions = sorted(
        [sesion for sesion in read_jsonl(user_sessions_file)],
        key=lambda x: x["timestamp"],
    )[:40]
    user_sessions = process_sesions(user_sessions)
    response = requests.post(
        "http://ium-2024z-model_api-1:8080/predictions/recomendations_model",
        json={"data": user_sessions},
        headers={"Content-Type": "application/json"},
    )
    return response.json()


if __name__ == "__main__":
    app = create_application()
    app.run("0.0.0.0", port=5001, debug=True)
