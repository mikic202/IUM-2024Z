import pandas as pd


def merge_tracks_and_artists(tracks_file, artists_file, output_file):
    """
    merge tracks and artists based on 'id_artist' and 'id'.

    """

    tracks = pd.read_json(tracks_file, lines=True)
    artists = pd.read_json(artists_file, lines=True)

    merged_data = tracks.merge(
        artists,
        left_on="id_artist",
        right_on="id",
        how="left",
        suffixes=("_track", "_artist"),
    )

    merged_data = merged_data.drop(columns=["id_artist", "genres"], errors="ignore")

    merged_data.to_json(output_file, lines=True, orient="records")


if __name__ == "__main__":
    # Ścieżki do plików wejściowych
    tracks_file = "data_v2/tracks.jsonl"
    artists_file = "data_v2/artists.jsonl"
    output_file = "data_v2/tracks_artists.jsonl"

    merge_tracks_and_artists(tracks_file, artists_file, output_file)
