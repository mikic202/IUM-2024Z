from typing import Optional
from pathlib import Path

from helpers.read_jsinl import read_jsonl
import heapq
import math

from Dataclasses.Track import Track
from Dataclasses.User import User


class SimpleRecomendationsGenerator:
    def __init__(self, sessions_directory: Path, tracks_file: Path) -> None:
        self._sessions_directory = sessions_directory
        self._tracks_file = tracks_file
        self._tracks = self._load_tracks()
        self._user_sessions = {}

    def generate_recomendations(
        self,
        user: User,
        tracks: list[Track],
        number_of_recomended_tracks: int,
    ) -> Optional[list[dict]]:
        reacent_track_embedding = self._get_reacent_track_embedding(user.id, tracks)
        new_tracks = [
            track
            for track in tracks
            if any(
                a == 1 and b == 1
                for a, b in zip(user.favourite_genres, track.geners_one_hot)
            )
        ]
        recomended_tracks = heapq.nsmallest(
            number_of_recomended_tracks + 1,
            list(new_tracks),
            key=lambda x: abs(math.dist(x.embedding, reacent_track_embedding)),
        )
        return [{"id_track": track.track_id} for track in recomended_tracks][1:]

    def _load_tracks(self) -> list[dict]:
        return list(read_jsonl(self._tracks_file))

    def _get_reacent_track_embedding(
        self, user_id: int, embeddsings: list[Track]
    ) -> Optional[list[float]]:
        user_sessions = self.get_user_sessions(user_id)
        liked_tracks = filter(
            lambda session: session["event_type"] == "like", user_sessions
        )
        last_track_id = max(liked_tracks, key=lambda x: x["timestamp"])["track_id"]
        last_track = next(
            (track for track in embeddsings if track.track_id == last_track_id),
            None,
        )
        return last_track.embedding

    def get_user_sessions(self, user_id: int) -> list[dict]:
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = list(
                read_jsonl(str(self._sessions_directory) + f"{user_id}.jsonl")
            )
        return self._user_sessions[user_id]
