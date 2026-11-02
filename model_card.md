# 🎧 Model Card: VibeFinder 1.0

## 1. Model Name

**VibeFinder 1.0 — Music Recommender Simulation**

VibeFinder is a Python-based music recommendation system that suggests songs based on a user's preferred genre, mood, and energy level.

## 2. Intended Use

VibeFinder is designed to demonstrate how a content-based music recommendation system works. It recommends five songs based on a user's music preferences.

The system assumes that a user's taste can be represented using a favorite genre, favorite mood, and target energy level.

This project is intended for educational purposes, not for commercial use or as a replacement for Spotify or other music platforms.

## 3. How the Model Works

The system compares each song's characteristics with the user's music preferences.

The scoring system awards:
- 2.0 points for matching the user's favorite genre.
- 1.0 point for matching the user's preferred mood.
- Up to 1.0 point based on how close the song's energy is to the user's preferred energy level.

After calculating each song's score, the system sorts all songs from highest to lowest and recommends the top five.

Each recommendation includes an explanation showing how its score was calculated.

I replaced the starter project's placeholder functions with working code for loading songs, calculating scores, ranking recommendations, and providing explanations.

## 4. Data

The dataset contains 20 fictional songs stored in `data/songs.csv`.

The starter dataset originally contained 10 songs, and I expanded it by adding 10 additional songs representing different genres and moods.

Each song contains attributes including genre, mood, energy, tempo, valence, danceability, and acousticness.

The current algorithm only uses genre, mood, and energy to calculate scores.

The small dataset limits the variety of recommendations and does not represent every musical genre, language, or listening preference.

## 5. Strengths

One strength of the recommender is that it produces different results depending on a user's preferences.

For example, Happy Pop received Sunrise City as its top recommendation, while Chill Lofi received Library Rain.

The scoring system is also easy to understand because each recommendation includes an explanation showing where the points came from.

The algorithm successfully identifies songs that match a user's genre and mood while considering their preferred energy level.

## 6. Limitations and Bias

One major limitation is the small dataset of only 20 songs, which restricts the number and variety of recommendations.

Another limitation is that the algorithm places more importance on genre than mood or energy. This may create a filter bubble where users mainly receive familiar genres instead of discovering different styles of music.

The system also does not learn from user behavior, such as likes, skips, or listening history.

Additionally, the algorithm does not currently use features such as danceability, valence, and acousticness, even though they are included in the dataset.

These limitations may make the recommendations less accurate for users with complex or changing music preferences.

## 7. Evaluation

I tested my recommender using three different user profiles.

**Happy Pop:** Genre pop, mood happy, energy 0.8. Sunrise City ranked first with a score of 3.98.

**Chill Lofi:** Genre lofi, mood chill, energy 0.3. Library Rain ranked first with a score of 3.95.

**Intense Rock:** Genre rock, mood intense, energy 0.9. Storm Runner ranked first with a score of 3.99.

### Comparing User Profiles

Happy Pop and Chill Lofi produced different recommendations because they preferred different genres and energy levels.

Chill Lofi and Intense Rock showed how the recommender distinguishes between low-energy and high-energy music.

Happy Pop and Intense Rock both included Gym Hero, but for different reasons. It matched Happy Pop's genre, while it matched Intense Rock's mood and energy.

### Scoring Experiment

I also experimented with doubling the importance of energy similarity from a maximum of 1.0 point to 2.0 points.

For Happy Pop, Gym Hero moved from second to fourth place because other songs had energy values closer to the user's preference.

For Chill Lofi, Spacewalk Thoughts moved from fourth to third place.

Storm Runner remained first for Intense Rock because it matched all three important features.

This experiment showed that changing the weight of one feature can significantly influence recommendation rankings.

After the experiment, I restored the original scoring rules.

### Testing

I used `python src/main.py` to test the recommendations and `python -m pytest -v` to run the starter tests.

Both starter tests passed.

## 8. Future Work

If I continued developing this project, I would:

1. Expand the dataset to include more songs, artists, and genres.
2. Incorporate additional features such as danceability, valence, and acousticness.
3. Add listening history and user feedback to improve personalization.
4. Introduce diversity rules to prevent recommending too many songs from the same genre.

These improvements could make the recommender more realistic and provide more personalized results.

## 9. Personal Reflection

The biggest thing I learned from this project is how a simple scoring algorithm can generate personalized music recommendations. Before this assignment, I mainly associated recommendation systems with complex machine learning models.

AI tools helped me organize the Python code, understand the scoring algorithm, and explore different ways to evaluate the results. However, I also learned the importance of checking the generated code and verifying that the scores were calculated correctly.

One interesting discovery was how changing the energy weight affected the rankings. Even when the user's preferences stayed the same, different songs moved higher or lower in the recommendations.

This project helped me better understand how music platforms use data to recommend content and how algorithmic decisions can influence what users discover.