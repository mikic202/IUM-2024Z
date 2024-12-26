import pandas as pd

def merge_tracks_and_artists(tracks_file, artists_file, output_file):
    """
    merge tracks and artists based on 'id_artist' and 'id'.

    """

    tracks = pd.read_json(tracks_file, lines=True)
    artists = pd.read_json(artists_file, lines=True)
    

    merged_data = tracks.merge(artists, left_on="id_artist", right_on="id", how="left", suffixes=("_track", "_artist"))
    
    merged_data = merged_data.drop(columns=["id_artist", "genres"], errors="ignore")

    merged_data["id_artist_hash"] = merged_data["id_artist_hash"].apply(postprocess_hash_to_list)

    merged_data.to_json(output_file, lines=True, orient="records")


def postprocess_hash_to_list(x):
    str_x = str(x)
    if len(str_x) < 8:
        str_x = "0" * (8 - len(str_x)) + str_x
    return [int(x) for x in str_x]

if __name__ == "__main__":
    # Ścieżki do plików wejściowych
    tracks_file = "data_v2/tracks.jsonl"  
    artists_file = "data_v2/artists.jsonl"  
    output_file = "data_v2/tracks_artists.jsonl" 


    merge_tracks_and_artists(tracks_file, artists_file, output_file)
