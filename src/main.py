
from recommender import load_songs, recommend_songs


def main():
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    profiles = {
        "Happy Pop": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8
        },
        "Chill Lofi": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.3
        },
        "Intense Rock": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.9
        }
    }

    for name, user_prefs in profiles.items():
        print(f"\n===== {name} =====")

        recommendations = recommend_songs(user_prefs, songs, k=5)

        for song, score, explanation in recommendations:
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {explanation}")
            print()


if __name__ == "__main__":
    main()
