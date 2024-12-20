import pandas as pd
import hashlib


def modify_artists(artists_file):
    """
    Modifies the artists file.
    """
    artists = pd.read_json(artists_file, lines=True)
    modify_artists = artists.apply(remove_names, axis=1)
    modify_artists = modify_artists.apply(add_index_hashing, axis=1)
    modify_artists = modify_artists.apply(replace_genre, axis=1)
    modify_artists = add_genres_to_hot_one(modify_artists)
    modify_artists.to_json("data_v2/artists.jsonl", lines=True, orient="records")


def add_index_hashing(artist):
    """
    Adds an index hashing to the artists.
    """
    artist["id_artist_hash"] = int(hashlib.md5(artist["id"].encode()).hexdigest(), 16) % (
        10**8
    )
    return artist

def remove_names(artist):
    """
    Removes the name of the artists.
    """
    artist = artist.drop("name")
    return artist




def replace_genre(artist):
    """
    Replace genres with the most popular genres.
    """
    keywords = [
        'regional', 'reggaeton', 'k-pop', 'r&b', 'mellow',
        'post-teen', 'corrido', 'ranchera', 'trap', 'latin',
        'metal', 'dance', 'hip hop', 'country', 'rock', 'rap', 'pop'
    ]
    
    mapped_genres = {
        keyword
        for genre in artist['genres']
        for keyword in keywords
        if keyword in genre.lower()
    }
    artist['genres'] = list(mapped_genres) if mapped_genres else []

    return artist



def add_genres_to_hot_one(artists):
    """
    Adds the genre of the artist to a hot one encoding.
    """
    modified_artists = artists.apply(extract_genre_to_hot_one, axis=1)
    return modified_artists


def extract_genre_to_hot_one(artist):
    """
    Extracts the alterations of a track to a hot one encoding.
    """
    hot_one_genre_encoding = generate_hot_one_encoding_form_genre(artist["genres"])
    artist["genre_hot_one"] = hot_one_genre_encoding
    return artist


def generate_hot_one_encoding_form_genre(genre):
    """
    Generates a hot one encoding from the track genre.
    """
    chacked_types = [
        'regional', 'reggaeton', 'k-pop', 'r&b', 'mellow',
        'post-teen', 'corrido', 'ranchera', 'trap', 'latin',
        'metal', 'dance', 'hip hop', 'country', 'rock', 'rap', 'pop',
    ]
    hot_one = []
    for chacked_type in chacked_types:
        if chacked_type in genre:
            hot_one.append(1)
        else:
            hot_one.append(0)
    return hot_one



if __name__ == "__main__":
    modify_artists("data_v1/artists.jsonl")
