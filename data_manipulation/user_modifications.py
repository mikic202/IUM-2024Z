import pandas as pd


def modify_users(users_file):
    """
    Modifies the users file.
    """
    users = pd.read_json(users_file, lines=True)
    modify_users = users.apply(remove_location, axis=1)
    modify_users = modify_users.apply(remove_premium_tag, axis=1)
    modify_users.to_json("data_v2/users.jsonl", lines=True, orient="records")


def remove_location(user):
    """
    Removes the location of the users.
    """
    user = user.drop("city")
    user = user.drop("street")
    return user


def remove_premium_tag(user):
    """
    Removes the premium tag of the users.
    """
    user = user.drop("premium_user")
    return user


if __name__ == "__main__":
    modify_users("data_v1/users.jsonl")
