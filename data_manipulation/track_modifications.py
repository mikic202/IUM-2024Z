import pandas as pd
from datetime import datetime

BASE_DATE = datetime.strptime("2025-01-03", "%Y-%m-%d").timestamp()


def modify_tracks(tracks_file):
    """
    Modifies the tracks file.
    """
    tracks = pd.read_json(tracks_file, lines=True)
    modified_tracks = add_track_alterations_to_hot_one(tracks)
    modified_tracks = modified_tracks.apply(normalize_popularity, axis=1)
    modified_tracks = modified_tracks.apply(normalize_loudness, axis=1)
    modified_tracks = modified_tracks.apply(remove_names, axis=1)

    # NORMALIZE DATES
    modified_tracks["release_date"] = (
        pd.to_datetime(modified_tracks["release_date"], format="mixed").apply(
            lambda x: x.timestamp()
        )
    ).div(BASE_DATE)

    # NORMALIZE DURATION
    modified_tracks["duration_ms"] = modified_tracks["duration_ms"].div(
        modified_tracks["duration_ms"].max()
    )

    # NORMALIZE TEMPO
    modified_tracks["tempo"] = modified_tracks["tempo"].div(
        modified_tracks["tempo"].max()
    )

    # EXPLICITE ENCODING
    modified_tracks["explicit"] = modified_tracks["explicit"].apply(
        lambda x: [0, 1] if x else [1, 0]
    )

    modified_tracks.to_json("data_v2/tracks.jsonl", lines=True, orient="records")


def remove_names(tracks):
    """
    Removes the name of the tracks.
    """
    tracks = tracks.drop("name")
    return tracks


def add_track_alterations_to_hot_one(tracks):
    """
    Adds the alterations of the tracks to a hot one encoding.
    """
    modified_tracks = tracks.apply(extract_track_alterations_to_hot_one, axis=1)
    return modified_tracks


def extract_track_alterations_to_hot_one(track):
    """
    Extracts the alterations of a track to a hot one encoding.
    """
    hot_one_name_encoding = generate_hot_one_encoding_form_name(track["name"])
    track["type_hot_one"] = hot_one_name_encoding
    return track


def generate_hot_one_encoding_form_name(track_name):
    """
    Generates a hot one encoding from the track name.
    """
    chacked_types = [
        "Remix",
        "Remastered",
        "Acoustic",
        "Instrumental",
        "Live",
        "Radio Edit",
        "Anniversary Edition",
    ]
    hot_one = []
    for chacked_type in chacked_types:
        if chacked_type in track_name:
            hot_one.append(1)
        else:
            hot_one.append(0)
    return hot_one


def normalize_popularity(track):
    """
    Normalizes the popularity of the tracks.
    """
    track["popularity"] = track["popularity"] / 100
    return track


def normalize_loudness(track):
    """
    Normalizes the loudness of the tracks.
    """
    track["loudness"] = track["loudness"] / -60
    return track


if __name__ == "__main__":
    tracks = modify_tracks("data_v1/tracks.jsonl")
