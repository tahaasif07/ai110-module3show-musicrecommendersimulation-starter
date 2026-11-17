"""Evaluate the real semantic recommender and its guardrails."""

import math
from pathlib import Path

from src.ai_playlist import MusicEngine
from src.recommender import load_songs


def main():
    root = Path(__file__).resolve().parent.parent
    songs = load_songs(root / "data" / "songs.csv")

    print("Loading the local model...")
    engine = MusicEngine(songs)

    passed = 0
    total = 0

    def check(name, condition):
        """Record each result without hiding failed checks."""
        nonlocal passed, total
        total += 1

        if condition:
            passed += 1
            print(f"PASS: {name}")
        else:
            print(f"FAIL: {name}")

    def rejects(name, **options):
        """An invalid request should raise a readable ValueError."""
        try:
            engine.recommend(**options)
        except ValueError as error:
            check(name, bool(str(error).strip()))
            print(f"  Message: {error}")
        else:
            check(name, False)

    requests = [
        "Mellow music for a rainy late-night study session",
        "Gentle relaxed music for unwinding",
        "Energetic upbeat music for a workout"
    ]

    # These checks verify valid output, not subjective listening quality.
    for request in requests:
        results = engine.recommend(
            request,
            semantic_weight=1.0,
            k=5
        )

        ids = [item["song"]["id"] for item in results]
        known_ids = {song["id"] for song in songs}
        scores = [item["score"] for item in results]

        valid = (
            len(results) == 5
            and len(set(ids)) == 5
            and set(ids).issubset(known_ids)
            and all(math.isfinite(score) for score in scores)
            and all(0 <= score <= 1 for score in scores)
            and scores == sorted(scores, reverse=True)
        )

        print(f"\nRequest: {request}")
        check("Five unique, valid, ranked catalog songs", valid)

        for item in results:
            song = item["song"]
            print(f"  {song['title']} — {song['artist']}")

    print("\nGuardrail checks")

    rejects("Empty request rejected", query="")

    rejects(
        "Negation redirected to exclusion controls",
        query="no rock"
    )

    rejects(
        "Conflicting filters rejected",
        query="music",
        genre="pop",
        excluded_genres=["pop"]
    )

    rejects(
        "No matching songs reported",
        query="music",
        genre="rock",
        mood="chill"
    )

    acoustic = engine.recommend(
        "quiet acoustic music",
        genre="lofi",
        acoustic_only=True
    )

    check(
        "Genre and acoustic filters enforced",
        bool(acoustic) and all(
            item["song"]["genre"] == "lofi"
            and item["song"]["acousticness"] >= 0.6
            for item in acoustic
        )
    )

    first = engine.recommend(requests[0], semantic_weight=1.0)
    second = engine.recommend(requests[0], semantic_weight=1.0)

    check(
        "Repeated requests give the same ranking",
        [item["song"]["id"] for item in first]
        == [item["song"]["id"] for item in second]
    )

    print(f"\nEvaluation summary: {passed}/{total} checks passed.")
    print("These checks do not prove subjective recommendation quality.")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())