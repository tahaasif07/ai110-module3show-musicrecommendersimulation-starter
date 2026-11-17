"""Local semantic retrieval combined with the original song scorer."""

import math
import re


from .recommender import score_song


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def describe_song(song):
    """Build a searchable description from actual metadata and explicit rules."""
    energy = song["energy"]
    acousticness = song["acousticness"]
    mood = song["mood"].lower()
    genre = song["genre"].lower()

    if energy < 0.4:
        energy_description = "low energy, gentle, mellow, quiet"
    elif energy < 0.7:
        energy_description = "moderate energy, steady, balanced"
    else:
        energy_description = "high energy, lively, energetic"

    acoustic_description = (
        "mostly acoustic" if acousticness >= 0.6 else "less acoustic"
    )

    contexts = []

    # These are transparent recommendations based on metadata.
    # They are not claims that the model has listened to the audio.
    if energy <= 0.55 and mood in {"chill", "focused", "relaxed"}:
        contexts.append(
            "suggested for studying, reading, concentration, "
            "quiet work, and late-night focus"
        )

    if energy <= 0.45 and genre in {"lofi", "ambient"}:
        contexts.append(
            "suggested for a mellow rainy evening, "
            "a peaceful study session, or unwinding"
        )

    if mood == "focused":
        contexts.append("suggested for deep work, coding, and concentration")

    if mood in {"happy", "upbeat"}:
        contexts.append("suggested for a cheerful morning and a positive mood")

    if energy >= 0.7:
        contexts.append("suggested for exercise, movement, and an energy boost")

    if mood == "sad":
        contexts.append("suggested for reflection and a melancholy mood")

    if acousticness >= 0.6:
        contexts.append("suggested for an acoustic listening preference")

    context_description = ". ".join(contexts)

    return (
        f"{genre} music with a {mood} mood. "
        f"{energy_description}. {acoustic_description}. "
        f"Tempo: {song['tempo_bpm']} beats per minute. "
        f"Danceability: {song['danceability']:.2f}. "
        f"{context_description}."
    )
class MusicEngine:
    """Build a reusable song index and search it with a local model."""

    def __init__(self, songs):
        if not songs:
            raise ValueError("The catalog is empty.")

        self.songs = []
        seen_ids = set()

        for original in songs:
            song = dict(original)

            # Normalize labels once so filters and baseline scoring agree.
            for field in ["title", "artist", "genre", "mood"]:
                if not isinstance(song.get(field), str) or not song[field].strip():
                    raise ValueError(f"Invalid or missing song field: {field}")

            song["genre"] = song["genre"].strip().lower()
            song["mood"] = song["mood"].strip().lower()

            if type(song.get("id")) is not int or song["id"] in seen_ids:
                raise ValueError("Song IDs must be unique integers.")

            seen_ids.add(song["id"])

            # Reject invalid metadata before it reaches the embedding model.
            for field in [
                "energy", "valence", "danceability", "acousticness"
            ]:
                value = song.get(field)

                if (
                    type(value) not in (int, float)
                    or not math.isfinite(value)
                    or not 0 <= value <= 1
                ):
                    raise ValueError(f"{field} must be between 0 and 1.")

            tempo = song.get("tempo_bpm")

            if (
                type(tempo) not in (int, float)
                or not math.isfinite(tempo)
                or tempo <= 0
            ):
                raise ValueError("tempo_bpm must be a positive number.")

            self.songs.append(song)

        # CPU mode keeps behavior consistent across Macs.
        # The first initialization downloads the pretrained model.
        # Load the model only when discovery is first used.
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(MODEL_NAME, device="cpu")

        self.descriptions = [describe_song(song) for song in self.songs]

        # Normalized vectors let a dot product calculate cosine similarity.
        # Song embeddings are created once, rather than for every search.
        self.embeddings = self.model.encode(
            self.descriptions,
            normalize_embeddings=True,
            show_progress_bar=False
        )

    def recommend(
        self,
        query,
        genre="Any",
        mood="Any",
        excluded_genres=None,
        target_energy=0.5,
        acoustic_only=False,
        semantic_weight=0.75,
        k=8
    ):
        """Apply hard filters, then combine semantic and baseline scores."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Describe the music you want.")

        query = query.strip()

        if len(query) > 500:
            raise ValueError("Keep your request to 500 characters or fewer.")

        # This embedding model does not reliably enforce negation.
        # Route exclusions through explicit controls instead of pretending
        # that semantic similarity will honor 'no rock' or 'without pop'.
        if re.search(
            r"\b(no|not|without|avoid|except|exclude|excluding|don't|dont)\b",
            query.lower()
        ):
            raise ValueError(
                "Use the 'Exclude genres' control for exclusions, "
                "then describe what you want in the request."
            )

        if type(k) is not int or not 1 <= k <= 20:
            raise ValueError("Playlist size must be between 1 and 20.")

        for label, value in [
            ("Target energy", target_energy),
            ("Semantic weight", semantic_weight)
        ]:
            if (
                type(value) not in (int, float)
                or not math.isfinite(value)
                or not 0 <= value <= 1
            ):
                raise ValueError(f"{label} must be between 0 and 1.")

        available_genres = {song["genre"] for song in self.songs}
        available_moods = {song["mood"] for song in self.songs}
        excluded = set(excluded_genres or [])

        if genre != "Any" and genre not in available_genres:
            raise ValueError("Unknown genre.")

        if mood != "Any" and mood not in available_moods:
            raise ValueError("Unknown mood.")

        if not excluded.issubset(available_genres):
            raise ValueError("An excluded genre is not in the catalog.")

        if genre in excluded:
            raise ValueError("The selected genre is also excluded.")

        candidate_indices = []

        for index, song in enumerate(self.songs):
            if genre != "Any" and song["genre"] != genre:
                continue
            if mood != "Any" and song["mood"] != mood:
                continue
            if song["genre"] in excluded:
                continue
            if acoustic_only and song["acousticness"] < 0.6:
                continue

            candidate_indices.append(index)

        if not candidate_indices:
            raise ValueError(
                "No songs match these filters. Try relaxing one filter."
            )

        query_vector = self.model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False
        )[0]

        preferences = {
            "genre": "" if genre == "Any" else genre,
            "mood": "" if mood == "Any" else mood,
            "energy": target_energy
        }

        # Normalize by the maximum possible baseline score for the
        # preferences supplied. Unspecified genre/mood earn no points.
        baseline_max = (
            1.0
            + (2.0 if genre != "Any" else 0.0)
            + (1.0 if mood != "Any" else 0.0)
        )

        results = []

        for index in candidate_indices:
            song = self.songs[index]

            cosine = float(self.embeddings[index] @ query_vector)

            if not math.isfinite(cosine):
                raise ValueError("The model returned an invalid similarity.")

            # Clipping gives the combined ranking a consistent 0–1 range.
            # It does not turn similarity into a confidence probability.
            semantic_score = max(0.0, min(1.0, cosine))
            baseline_score, reasons = score_song(preferences, song)
            normalized_baseline = baseline_score / baseline_max

            combined = (
                semantic_weight * semantic_score
                + (1 - semantic_weight) * normalized_baseline
            )

            results.append({
                "song": song,
                "score": combined,
                "semantic_score": semantic_score,
                "baseline_score": baseline_score,
                "description": self.descriptions[index],
                "reasons": reasons
            })

        # Use ID as a tie-breaker so equal scores have a stable order.
        results.sort(key=lambda item: (-item["score"], item["song"]["id"]))

        return results[:k]