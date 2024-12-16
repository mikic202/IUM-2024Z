import pandas as pd
import hashlib


def modify_artists(artists_file):
    """
    Modifies the artists file.
    """
    artists = pd.read_json(artists_file, lines=True)
    artists = artists.apply(add_index_hashing, axis=1)
    artists.to_json("data_v2/artists_2.jsonl", lines=True, orient="records")


def add_index_hashing(artist):
    """
    Adds an index hashing to the artists.
    """
    artist["id_hash"] = int(hashlib.md5(artist["id"].encode()).hexdigest(), 16) % (
        10**8
    )
    return artist


if __name__ == "__main__":
    modify_artists("data_v2/artists.jsonl")
