# Model Card: Tempo

## Purpose

Tempo helps users discover songs by describing a listening moment.
It extends the AI110 Module 3 recommender, which originally ranked
20 fictional songs using genre, mood, and energy preferences.

## Model

Tempo uses sentence-transformers/all-MiniLM-L6-v2, a pretrained
sentence embedding model running locally on CPU.

The model compares a user's request with descriptions built from
song metadata. No API key or fine-tuning is required. The first
model download requires internet access.

This is semantic retrieval. It does not generate conversation,
analyze audio, or act as an autonomous agent.

## Data

The catalog is data/songs.csv and contains 20 fictional songs.

Descriptions use genre, mood, energy, acousticness, tempo, and
danceability. Handcrafted rules add possible listening contexts,
such as studying or exercising. These contexts are suggestions
from metadata, not verified facts about the audio.

Valence is validated but is not currently used for ranking.

## Ranking

Song descriptions and user requests are converted into normalized
embeddings. Their dot product gives cosine similarity, which is
clipped to the range 0–1.

By default, the interface ranks using semantic similarity alone.
When the user enables an energy preference, ranking combines:

- 75% semantic similarity.
- 25% normalized original scoring.

Genre, mood, excluded genres, and acoustic-only settings are
applied as hard filters. Acoustic-only requires acousticness
of at least 0.6.

Scores are ranking values, not confidence probabilities.
Equal scores are ordered by song ID.

## Reliability Controls

The system checks:

- Required metadata and unique integer song IDs.
- Numeric attribute ranges and positive finite tempo.
- Empty requests and requests longer than 500 characters.
- Invalid parameters and contradictory filters.
- Requests containing negation, directing users to exclusion controls.
- Cases where no songs satisfy the filters.
- Nonfinite similarity scores.

Failed discovery requests clear the previous mix.

Saved likes and mixes use checked JSON and atomic file replacement.
Corrupt saved data is reported instead of silently overwritten.

## Actual Evaluation

Command:

python3 -m src.evaluate_semantic

The real-model evaluation ran successfully on the user's Mac
with Python 3.14 and passed 9/9 checks.

Three requests each returned five unique catalog songs with
finite scores in descending order. Six additional checks covered
empty requests, negation, conflicting filters, no matches,
genre/acoustic filtering, and repeatable rankings.

Example first results:

| Request | First result |
| --- | --- |
| Rainy late-night study | Deep Focus |
| Gentle unwinding | Spacewalk Thoughts |
| Energetic workout | Storm Runner |

These checks establish technical behavior. They do not measure
subjective musical relevance or prove superiority over the
original recommender.

## Limitations

The catalog is small and fictional. No audio is bundled.

Semantic similarity does not guarantee that every result fits
the intended mood. For example, the unwinding request returned
Starlight Dance among its five results. Explicit filters help
enforce requirements.

The model does not verify lyrics, explicit content, instruments,
or listening quality. Unrelated requests may still return nearby
catalog entries. Negation handling is conservative and may reject
otherwise harmless wording.

Likes and saved mixes do not personalize or train the model.
Storage supports one local user, not concurrent hosted accounts.

## Future Improvements

Collect independent relevance judgments for a larger set of
requests, compare results with the original scorer, and evaluate
on held-out examples before changing ranking rules further.

Other improvements could include richer verified metadata,
better handling of unrelated requests, and licensed audio previews.