from pathlib import Path
from typing import Optional
import json
import math
import heapq

from Dataclasses.Track import Track


class ComplexRecomendationsGenerator:
    def __init__(self, preferences_file_path: Path) -> None:
        self._preferences_file_path = preferences_file_path
        with open(self._preferences_file_path, "r") as f:
            self._user_preferences = json.load(f)

    def generate_recomendations(
        self,
        user_id: int,
        embedsings: list[Track],
        number_of_recomended_tracks: int,
    ) -> Optional[list[dict]]:
        if user_preferences := self.get_user_preference_vector(user_id):
            recomended_tracks = heapq.nsmallest(
                number_of_recomended_tracks,
                list(embedsings),
                key=lambda x: abs(math.dist(x.embedding, user_preferences)),
            )
            return [{"id_track": track.track_id} for track in recomended_tracks]
        return None

    def get_user_preference_vector(self, user_id: int) -> Optional[list[float]]:
        for user_preference in self._user_preferences:
            if int(user_preference["user_id"]) == int(user_id):
                return user_preference["preferences"][0]
        return None
