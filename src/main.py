"""Command-line interface for the extended music recommender."""

import argparse
from pathlib import Path

from assistant import RequestError, answer_request
from recommender import load_songs


def main():
    parser = argparse.ArgumentParser(
        description="Recommend songs from a natural-language request."
    )

    parser.add_argument(
        "request",
        help='Example: "happy pop high energy"'
    )

    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of recommendations, from 1 to 10."
    )

    # Resolve the default dataset relative to this script so running it
    # from another working directory still finds the correct CSV file.
    default_data = Path(__file__).resolve().parent.parent / "data" / "songs.csv"
    parser.add_argument(
        "--data",
        default=str(default_data),
        help="Path to the song CSV file."
    )

    args = parser.parse_args()

    try:
        songs = load_songs(args.data)

        preferences, results = answer_request(
            args.request,
            songs,
            k=args.count
        )

    except (OSError, ValueError, KeyError) as error:
        # Expected input and dataset problems get a readable message.
        # A failing command also returns a nonzero exit status.
        parser.exit(1, f"Could not recommend songs: {error}\n")

    print(f"Request: {args.request}")
    print(f"Genre: {preferences['genre'] or 'any'}")
    print(f"Mood: {preferences['mood'] or 'any'}")
    print(f"Target energy: {preferences['energy']:.1f}")
    print(f"Acoustic required: {preferences['acoustic']}")

    for number, (song, score, explanation) in enumerate(results, start=1):
        print(f"\n{number}. {song['title']} — {song['artist']}")
        print(f"Score: {score:.2f}/4.00")
        print(f"Because: {explanation}")


if __name__ == "__main__":
    main()