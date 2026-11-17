"""Interpret music requests and safely call the original recommender."""

import math
import re

from recommender import recommend_songs


class RequestError(ValueError):
    """An error that can be shown directly to the user."""


def validate_catalog(songs):
    """Check the dataset before using it to make recommendations."""
    if not songs:
        raise RequestError("The song dataset is empty.")

    seen_ids = set()

    for song in songs:
        # These fields are needed for ranking, display, and identity checks.
        required = ["id", "title", "artist", "genre", "mood", "energy"]

        if any(field not in song for field in required):
            raise RequestError("A song is missing a required field.")

        for field in ["title", "artist", "genre", "mood"]:
            if not isinstance(song[field], str) or not song[field].strip():
                raise RequestError(f"A song has an invalid {field}.")

        # Duplicate IDs could make two different songs look like one result.
        if type(song["id"]) is not int or song["id"] in seen_ids:
            raise RequestError("Song IDs must be unique integers.")

        seen_ids.add(song["id"])

        # NaN and infinity must also be rejected, since normal comparisons
        # do not reliably detect every invalid floating-point value.
        energy = song["energy"]

        if (
            type(energy) not in (int, float)
            or not math.isfinite(energy)
            or not 0 <= energy <= 1
        ):
            raise RequestError("Each song's energy must be between 0 and 1.")


def contains_phrase(text, phrase):
    """Match complete words so 'pop' does not accidentally match 'popular'."""
    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return re.search(pattern, text) is not None


def choose_one(values, label):
    """Ask for clarification instead of silently choosing conflicting values."""
    if len(values) > 1:
        raise RequestError(
            f"Please choose one {label}: {', '.join(sorted(values))}."
        )

    return next(iter(values), "")


def parse_request(text, songs):
    """Turn supported words and phrases into structured music preferences."""
    if not isinstance(text, str) or not text.strip():
        raise RequestError("Please enter a music request.")

    if len(text) > 500:
        raise RequestError("Please keep your request under 501 characters.")

    text = text.lower().strip()

    # This simple parser cannot safely interpret exclusions. Reject them
    # rather than recommending the exact music the user asked to avoid.
    exclusions = ["no", "not", "without", "avoid", "except", "don't", "dont"]

    if any(contains_phrase(text, word) for word in exclusions):
        raise RequestError(
            "Exclusions are not supported yet. Describe what you want."
        )

    genres = {song["genre"].lower() for song in songs}
    moods = {song["mood"].lower() for song in songs}

    matched_genres = {
        genre for genre in genres if contains_phrase(text, genre)
    }

    matched_moods = {
        mood for mood in moods if contains_phrase(text, mood)
    }

    # Aliases only map to moods that actually exist in this dataset.
    # This prevents the parser from inventing unsupported mood categories.
    aliases = {
        "calm": "chill",
        "relaxing": "chill",
        "study": "chill",
        "studying": "chill",
        "cheerful": "happy",
        "joyful": "happy",
        "workout": "intense",
        "gym": "intense"
    }

    for phrase, mood in aliases.items():
        if mood in moods and contains_phrase(text, phrase):
            matched_moods.add(mood)

    genre = choose_one(matched_genres, "genre")
    mood = choose_one(matched_moods, "mood")

    low_energy = any(
        contains_phrase(text, phrase)
        for phrase in ["low energy", "calm", "relaxing", "study", "studying"]
    )

    high_energy = any(
        contains_phrase(text, phrase)
        for phrase in ["high energy", "energetic", "workout", "gym"]
    )

    if low_energy and high_energy:
        raise RequestError("Please choose low energy or high energy.")

    acoustic = contains_phrase(text, "acoustic")

    # An unrecognized request should not produce an arbitrary playlist.
    if not any([genre, mood, low_energy, high_energy, acoustic]):
        raise RequestError(
            "I could not identify a preference. "
            f"Available genres: {', '.join(sorted(genres))}. "
            f"Available moods: {', '.join(sorted(moods))}."
        )

    energy = 0.5

    if low_energy:
        energy = 0.3
    elif high_energy:
        energy = 0.9

    return {
        "genre": genre,
        "mood": mood,
        "energy": energy,
        "acoustic": acoustic
    }


def answer_request(text, songs, k=5):
    """Validate, interpret, filter, rank, and check one complete request."""
    validate_catalog(songs)

    if type(k) is not int or not 1 <= k <= 10:
        raise RequestError("The recommendation count must be from 1 to 10.")

    preferences = parse_request(text, songs)
    candidates = []

    for song in songs:
        # Explicit genre and mood choices are requirements here.
        # The original system only awarded points for these matches.
        if (
            preferences["genre"]
            and song["genre"].lower() != preferences["genre"]
        ):
            continue

        if (
            preferences["mood"]
            and song["mood"].lower() != preferences["mood"]
        ):
            continue

        if preferences["acoustic"]:
            acousticness = song.get("acousticness")

            if (
                type(acousticness) not in (int, float)
                or not math.isfinite(acousticness)
                or not 0 <= acousticness <= 1
            ):
                raise RequestError(
                    "Acoustic recommendations require valid "
                    "acousticness values between 0 and 1."
                )

            # This is an explicit project rule, not a learned threshold.
            if acousticness < 0.6:
                continue

        # Normalize a copy so the original scorer handles capitalization
        # consistently without changing the user's dataset in memory.
        normalized = dict(song)
        normalized["genre"] = song["genre"].lower()
        normalized["mood"] = song["mood"].lower()
        candidates.append(normalized)

    if not candidates:
        raise RequestError(
            "No songs match all those preferences. "
            "Try removing a genre, mood, or acoustic requirement."
        )

    results = recommend_songs(preferences, candidates, k=k)

    # Check the output at the boundary before displaying it.
    # Only known, unique songs with valid baseline scores may be returned.
    allowed_ids = {song["id"] for song in candidates}
    returned_ids = set()

    if not results or len(results) > k:
        raise RequestError("The recommender returned an invalid result count.")

    for song, score, explanation in results:
        if song["id"] not in allowed_ids or song["id"] in returned_ids:
            raise RequestError("The recommender returned an invalid song.")

        if not math.isfinite(score) or not 0 <= score <= 4:
            raise RequestError("The recommender returned an invalid score.")

        if not isinstance(explanation, str) or not explanation.strip():
            raise RequestError("A recommendation is missing its explanation.")

        returned_ids.add(song["id"])

    return preferences, results