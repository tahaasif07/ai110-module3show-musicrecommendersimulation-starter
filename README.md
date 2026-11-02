# 🎵 Music Recommender Simulation

## Project Summary

For this project, I built a Python-based music recommendation system that recommends songs based on a user's favorite genre, mood, and energy level.

My recommender uses a dataset of 20 fictional songs and calculates a score for each song. It then ranks the songs and displays the top five recommendations with explanations showing why each song was selected.

The goal of this project was to understand how recommendation systems turn data and user preferences into personalized suggestions.

---

## How The System Works

Real music platforms like Spotify and YouTube use information such as listening history, likes, skips, playlists, and song attributes to recommend music.

Two common recommendation approaches are:

- **Content-based filtering:** Recommends music based on song characteristics and the user's preferences.
- **Collaborative filtering:** Uses patterns from other listeners with similar interests to make recommendations.

My program uses content-based filtering.

### Song Features

Each song includes the following attributes:

- Title and artist
- Genre and mood
- Energy
- Tempo (BPM)
- Valence
- Danceability
- Acousticness

The current scoring algorithm uses genre, mood, and energy. The other numerical attributes are stored for future improvements.

### User Preferences

Each user profile contains a favorite genre, favorite mood, and target energy level.

The program compares these preferences with every song in the dataset.

### Scoring Algorithm

Every song receives points based on how closely it matches the user's preferences:

| Feature | Points |
|---|---|
| Matching genre | +2.0 |
| Matching mood | +1.0 |
| Energy similarity | Up to +1.0 |

Energy similarity is calculated using:

`1 - abs(user_energy - song_energy)`

The closer a song's energy is to the user's preferred energy, the more points it earns.

The program calculates a score for each song, ranks all songs from highest to lowest score, and returns the top five recommendations.

### Recommendation Process

1. Load songs from the CSV dataset.
2. Read the user's preferences.
3. Calculate a score for every song.
4. Sort the songs by their scores.
5. Display the top five recommendations with explanations.

One possible bias is that genre receives more weight than other features, which could make the system favor familiar music.

---

## Getting Started

### Setup

Clone the repository and open the project folder.

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate the environment on macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the recommender:

```bash
python src/main.py
```

### Running Tests

Run the tests using:

```bash
python -m pytest -v
```

The test suite checks recommendation sorting and explanation generation.

During development, both starter tests passed successfully.

---

## Sample Recommendation Output

The following results were collected using the original scoring algorithm.

### Profile 1: Happy Pop

Preferences: Pop, Happy, Energy 0.8

```text
===== Happy Pop =====
Sunrise City - Score: 3.98
Because: Genre match (+2.0), Mood match (+1.0), Energy similarity (+0.98)

Gym Hero - Score: 2.87
Because: Genre match (+2.0), Energy similarity (+0.87)

Rooftop Lights - Score: 1.96
Because: Mood match (+1.0), Energy similarity (+0.96)

Starlight Dance - Score: 1.95
Because: Mood match (+1.0), Energy similarity (+0.95)

Electric Dreams - Score: 1.85
Because: Mood match (+1.0), Energy similarity (+0.85)
```

### Profile 2: Chill Lofi

Preferences: Lofi, Chill, Energy 0.3

```text
===== Chill Lofi =====
Library Rain - Score: 3.95
Because: Genre match (+2.0), Mood match (+1.0), Energy similarity (+0.95)

Midnight Coding - Score: 3.88
Because: Genre match (+2.0), Mood match (+1.0), Energy similarity (+0.88)

Focus Flow - Score: 2.90
Because: Genre match (+2.0), Energy similarity (+0.90)

Spacewalk Thoughts - Score: 1.98
Because: Mood match (+1.0), Energy similarity (+0.98)

Broken Memories - Score: 1.00
Because: Energy similarity (+1.00)
```

### Profile 3: Intense Rock

Preferences: Rock, Intense, Energy 0.9

```text
===== Intense Rock =====
Storm Runner - Score: 3.99
Because: Genre match (+2.0), Mood match (+1.0), Energy similarity (+0.99)

Street Kings - Score: 1.98
Because: Mood match (+1.0), Energy similarity (+0.98)

Gym Hero - Score: 1.97
Because: Mood match (+1.0), Energy similarity (+0.97)

Dark Horizon - Score: 1.92
Because: Mood match (+1.0), Energy similarity (+0.92)

Electric Dreams - Score: 0.95
Because: Energy similarity (+0.95)
```

---

## Experiments You Tried

### Experiment 1: Different User Profiles

I tested three different user profiles to see how their preferences changed the recommendations.

**Happy Pop:** Sunrise City ranked first because its genre, mood, and energy closely matched the user's preferences.

**Chill Lofi:** Library Rain ranked first because it matched the preferred genre and mood while having a similar low energy level.

**Intense Rock:** Storm Runner ranked first because it matched the user's favorite genre, intense mood, and high energy level.

### Comparing the Results

Comparing Happy Pop and Chill Lofi showed that different preferences produced different rankings. Chill Lofi favored calmer music, while Happy Pop favored upbeat songs.

Comparing Chill Lofi and Intense Rock demonstrated how low-energy and high-energy preferences affected the results. Library Rain ranked first for Chill Lofi, while Storm Runner ranked first for Intense Rock.

Comparing Happy Pop and Intense Rock showed that Gym Hero could appear in both lists for different reasons. It matched Happy Pop's genre, while it matched Intense Rock's mood and energy.

These results showed that the same dataset can generate different recommendations based on user preferences.

### Experiment 2: Increasing Energy Weight

I tested an alternative scoring algorithm that doubled energy similarity's maximum contribution from 1.0 to 2.0 points while keeping the genre and mood weights unchanged.

In the experimental rankings:

- Gym Hero moved from second to fourth for Happy Pop.
- Spacewalk Thoughts moved from fourth to third for Chill Lofi.
- Storm Runner remained first for Intense Rock.

This demonstrated that increasing the importance of energy can allow songs with closer energy values to outrank songs that match the user's preferred genre.

The experiment helped me understand how adjusting weights influences recommendations and how important it is to balance different features.

After testing, I restored the original scoring algorithm.

---

## Limitations and Risks

My recommendation system has several limitations.

First, the dataset only contains 20 fictional songs, which means it cannot represent the full range of musical preferences.

Second, the algorithm gives more importance to genre than mood or energy. This could create a filter bubble where users repeatedly receive recommendations from familiar genres rather than discovering new styles.

Third, the recommender does not use listening history, likes, skips, or feedback to learn from users.

Finally, although the dataset includes danceability, valence, tempo, and acousticness, the current scoring algorithm does not use these attributes.

These limitations could make recommendations less accurate for users with more complex or changing music preferences.

---

## Reflection

The biggest thing I learned from this project is how recommendation systems can turn relatively simple data into personalized rankings. Before this assignment, I mainly thought of music recommendations as something that required complex machine learning models. Building this simulation showed me that a straightforward scoring algorithm can already produce useful results.

AI assistance helped me organize the Python code, design the scoring logic, and explore different ways to evaluate the recommendations. However, I still needed to test the program, check the output, and investigate inconsistencies in the scores. I also learned how the weight assigned to each feature can influence recommendations and potentially introduce bias.

One of the most interesting discoveries was how changing just the energy weight affected the rankings. This helped me understand why recommendation systems must be evaluated carefully rather than assuming their outputs are always correct.

If I continued developing this project, I would experiment with more song attributes, larger datasets, user feedback, and diversity rules to improve personalization.

For additional details about the model, its evaluation, limitations, and future improvements, see the [Model Card](model_card.md).