import pandas as pd


def modify_users(users_file):
    """
    Modifies the users file.
    """
    users = pd.read_json(users_file, lines=True)
    modify_users = users.apply(remove_location_name, axis=1)
    modify_users = modify_users.apply(remove_premium_tag, axis=1)
    modify_users = modify_users.apply(replace_genre, axis=1)
    modify_users = add_genres_to_hot_one(modify_users)
    modify_users = modify_users.apply(remove_genres, axis=1)
    modify_users.to_json("data_v2/users.jsonl", lines=True, orient="records")


def remove_location_name(user):
    """
    Removes the location of the users and names.
    """
    user = user.drop("city")
    user = user.drop("street")
    user = user.drop("name")
    return user


def remove_premium_tag(user):
    """
    Removes the premium tag of the users.
    """
    user = user.drop("premium_user")
    return user

def remove_genres(user):
    """
    Removes the genres of the user.
    """
    user = user.drop("favourite_genres")
    return user


def replace_genre(user):
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
        for genre in user['favourite_genres']
        for keyword in keywords
        if keyword in genre.lower()
    }
    user['favourite_genres'] = list(mapped_genres) if mapped_genres else []

    return user


def add_genres_to_hot_one(users):
    """
    Adds the genre of the user to a hot one encoding.
    """
    modified_users = users.apply(extract_genre_to_hot_one, axis=1)
    return modified_users


def extract_genre_to_hot_one(user):
    """
    Extracts the alterations of a track to a hot one encoding.
    """
    hot_one_genre_encoding = generate_hot_one_encoding_form_genre(user["favourite_genres"])
    user["genre_hot_one"] = hot_one_genre_encoding
    return user


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
    modify_users("data_v1/users.jsonl")
