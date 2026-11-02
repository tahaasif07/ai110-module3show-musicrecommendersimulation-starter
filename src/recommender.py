import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's music preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file."""
    songs = []

    with open(csv_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for song in reader:
            song["id"] = int(song["id"])

            for feature in [
                "energy", "tempo_bpm", "valence",
                "danceability", "acousticness"
            ]:
                song[feature] = float(song[feature])

            songs.append(song)

    return songs



def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Calculate a song's score and explain the result."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs["genre"]:
        score += 2.0
        reasons.append("Genre match (+2.0)")

    if song["mood"] == user_prefs["mood"]:
        score += 1.0
        reasons.append("Mood match (+1.0)")

    energy_difference = abs(song["energy"] - user_prefs["energy"])
    energy_points = max(0.0, 1.0 - energy_difference)

    score += energy_points
    reasons.append(f"Energy similarity (+{energy_points:.2f})")

    return score, reasons



def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Score all songs and return the top recommendations."""
    recommendations = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)

        recommendations.append((song, score, explanation))

    recommendations.sort(key=lambda item: item[1], reverse=True)

    return recommendations[:k]


class Recommender:
    """Object-oriented music recommender."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top songs for a user profile."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy
        }

        song_scores = []

        for song in self.songs:
            song_data = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy
            }

            score, _ = score_song(user_prefs, song_data)
            song_scores.append((song, score))

        song_scores.sort(key=lambda item: item[1], reverse=True)

        return [song for song, score in song_scores[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain why a song matches a user's preferences."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy
        }

        song_data = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy
        }

        score, reasons = score_song(user_prefs, song_data)

        return f"Score: {score:.2f} - " + ", ".join(reasons)
