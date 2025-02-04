from dataclasses import dataclass


@dataclass
class User:
    id: int
    preference_vector: list[float]
    favourite_genres: list[int]
