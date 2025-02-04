from dataclasses import dataclass


@dataclass
class Track:
    track_id: str
    embedding: list[float]
    geners_one_hot: list[int]
