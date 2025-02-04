from typing import Optional
from pathlib import Path

from helpers.read_jsinl import read_jsonl
import heapq
import math


class SimpleRecomendationsGenerator:
    def __init__(self, sessions_directory: Path, tracks_file: Path) -> None:
        self._sessions_directory = sessions_directory
        self._tracks_file = tracks_file

    def generate_recomendations(
        self,
        user_id: int,
        embeddsings: list[list[float]],
        number_of_recomended_tracks: int,
        user_favourite_geners_one_hot: list[int],
    ) -> Optional[list[dict]]:
        reacent_track_embedding = self._get_reacent_track_embedding(
            user_id, embeddsings
        )
        tracks_data = self._load_tracks()
        new_embeddings = []
        for i, row in enumerate(embeddsings):
            track_genre = tracks_data[i]["genre_hot_one"]
            if any(
                u == 1 and t == 1
                for u, t in zip(user_favourite_geners_one_hot, track_genre)
            ):
                new_embeddings.append(row)
        recomended_tracks = heapq.nsmallest(
            number_of_recomended_tracks + 1,
            list(embeddsings),
            key=lambda x: abs(math.dist(x["embedding"], reacent_track_embedding)),
        )
        return [{"id_track": track["id_track"]} for track in recomended_tracks][1:]

    def _load_tracks(self) -> list[dict]:
        return list(read_jsonl(self._tracks_file))

    def _get_reacent_track_embedding(
        self, user_id: int, embeddsings: list[list[float]]
    ) -> Optional[list[float]]:
        user_sessions = self.get_user_sessions(user_id)
        liked_tracks = filter(
            lambda session: session["event_type"] == "like", user_sessions
        )
        last_track_id = max(liked_tracks, key=lambda x: x["timestamp"])["track_id"]
        last_track = next(
            (track for track in embeddsings if track["id_track"] == last_track_id),
            None,
        )
        return last_track["embedding"]

    def get_user_sessions(self, user_id: int) -> list[dict]:
        return list(read_jsonl(str(self._sessions_directory) + f"{user_id}.jsonl"))
