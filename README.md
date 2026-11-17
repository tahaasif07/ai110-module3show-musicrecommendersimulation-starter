# Music Recommendation Assistant

## Base project

This project extends my AI110 Module 3 Show Music Recommender Simulation:

https://github.com/tahaasif07/ai110-module3show-musicrecommendersimulation-starter

The original program loaded songs from a CSV file and ranked them for
three predefined profiles. Its scoring system awarded 2 points for a
genre match, 1 point for a mood match, and up to 1 point for energy
similarity. It also explained each score.

## Extension

The new command-line interface accepts supported natural-language
requests instead of requiring hardcoded profiles.

A reliability workflow validates the catalog, detects ambiguous requests,
filters songs according to explicit preferences, and checks results
before displaying them. An evaluation script tests successful requests
and failure cases.

The parser uses explicit rules and dataset labels. It does not call an
LLM, perform fine-tuning, or implement RAG.

## Files

- recommender.py: original loading and ranking functions
- assistant.py: request interpretation and reliability checks
- main.py: command-line interface
- evaluate.py: synthetic evaluation cases and pass/fail summary
- architecture.mmd: implemented data flow
- data/songs.csv: original song dataset
- model_card.md: behavior and limitations
- ai_interactions.md: AI collaboration record and reflection

## Setup

Use Python 3.10 or newer. No third-party packages are required for these
scripts.

Keep the original songs.csv inside the data folder.

Run:

```bash
python main.py "happy pop high energy" --count 3
python main.py "calm lofi music for studying" --count 3
python main.py "intense rock high energy" --count 3
python evaluate.py
```

The default count is 5. When fewer songs meet all requirements, the
program returns the available matches.

To use another CSV:

```bash
python main.py "happy pop" --data data/songs.csv
```

## Interpreting requests

Genres and moods are read from the dataset.

Supported aliases include:
- calm, relaxing, study, studying: chill
- cheerful, joyful: happy
- workout, gym: intense

An alias is only enabled if its target mood exists in the dataset.

Low-energy phrases set target energy to 0.3.
High-energy phrases set target energy to 0.9.
Otherwise, the target is 0.5.

Acoustic requests require acousticness of at least 0.6.

Genre and mood are filters. Energy is a ranking preference, not a hard
limit. Unspecified genre or mood is left unrestricted.

## Example output

The following is an illustrative example using the synthetic catalog
defined in evaluate.py. These are not claimed to be songs from songs.csv
or captured execution results.

Input:

```text
happy pop high energy
```

Expected recommendation:

```text
Sample Pop — Test Artist
Score: 3.90/4.00
Because: Genre match (+2.0), Mood match (+1.0), Energy similarity (+0.90)
```

Input:

```text
calm acoustic music for studying
```

Expected recommendation:

```text
Sample Study — Test Artist
Score: 2.00/4.00
Because: Mood match (+1.0), Energy similarity (+1.00)
```

Input:

```text
rock workout
```

Expected recommendation:

```text
Sample Rock — Test Artist
Score: 4.00/4.00
Because: Genre match (+2.0), Mood match (+1.0), Energy similarity (+1.00)
```

Scores depend on which preferences are specified. They are ranking
scores, not confidence probabilities.

Before submission, run the commands against the actual CSV and add
captured command-line output here.

## Guardrail examples

| Input or condition | Behavior | Result |
| --- | --- | --- |
| Empty request | Rejects missing preferences | Asks for a music request |
| pop rock | Detects multiple genres | Asks the user to choose one |
| not pop | Detects unsupported exclusion | Requests positive preferences |
| pop chill with no matching song | Refuses unrelated replacements | Suggests relaxing a requirement |
| Song energy is NaN | Rejects invalid catalog data | No recommendations displayed |
| Ranking component returns unknown ID | Blocks invalid output | No invalid song displayed |

## Evaluation

```bash
python evaluate.py
```

The script contains 10 test methods, including three successful request
examples, ambiguity checks, catalog validation, acoustic filtering,
invalid recommendation counts, and a simulated faulty ranking result.

It prints individual test results and a summary in this format:

```text
Evaluation summary: X/10 tests passed.
```

The tests have not been executed in the authoring chat. Record the
actual result after running them.

## Limitations and future work

The parser recognizes a limited set of words and phrases. It cannot
reliably understand negation, multiple requested genres, complex
sentences, or every unsupported preference. Recognized parts of a
request may be used even when other words are ignored.

Strict filtering can return fewer recommendations. The acoustic
threshold is manually selected. The evaluation uses a small synthetic
catalog and does not measure real listeners' satisfaction.

Future improvements include testing the real CSV, collecting listener
feedback, adding better language interpretation, and supporting
explicit exclusions.
## Project 4: Applied AI Extension

This project extends my AI110 Module 3 Music Recommender Simulation.
The original system ranked 20 fictional songs using genre matches
(+2), mood matches (+1), and energy similarity (up to +1). It already
provided score explanations.

The new system, Tempo, adds local semantic retrieval using
sentence-transformers/all-MiniLM-L6-v2. Users describe a listening
moment, and the model compares their request with song metadata
descriptions. It requires no API key.

Tempo also adds a Streamlit interface, liked songs, saved mixes,
and integrated reliability controls. It performs semantic retrieval,
not generative conversation, audio analysis, or autonomous planning.

### Setup and Run

Run these commands in Terminal from the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

If the virtual environment already exists, skip its creation.

Open http://localhost:8501. The first discovery request requires
internet access to download the pretrained model. Later requests
can use the cached model.

### Evaluation

```bash
python3 -m src.evaluate_semantic
```

Actual results from my Mac:

```text
Request: Mellow music for a rainy late-night study session
Deep Focus — Quiet Mind
Spacewalk Thoughts — Orbit Bloom
Focus Flow — LoRoom
Library Rain — Paper Lanterns
Midnight Coding — LoRoom

Request: Gentle relaxed music for unwinding
Spacewalk Thoughts — Orbit Bloom
Deep Focus — Quiet Mind
Golden Fields — Acoustic Soul
Library Rain — Paper Lanterns
Starlight Dance — Nova Beat

Request: Energetic upbeat music for a workout
Storm Runner — Voltline
Street Kings — Urban Flow
Rooftop Lights — Indigo Parade
Gym Hero — Max Pulse
Night Drive Loop — Neon Echo

Evaluation summary: 9/9 checks passed.
```

The evaluation checks valid catalog results, unique song IDs,
finite scores, descending ranking, request validation, exact
filters, and repeatable results. Passing these checks demonstrates
technical reliability, not subjective recommendation quality.

### Guardrail Examples

| Input or setting | Actual behavior |
| --- | --- |
| Empty request | Rejected: “Describe the music you want.” |
| `no rock` | Rejected with directions to use exclusion controls. |
| Select pop and exclude pop | Rejected because the requirements conflict. |
| Select rock and chill | Reports that no songs match these filters. |
| Select lofi and acoustic only | Every result satisfies both filters. |
| Repeat the same request | Returns the same song order. |

### Limitations

The catalog contains only 20 fictional songs and no bundled audio.
Listening contexts are handcrafted suggestions based on metadata,
not verified audio facts. Semantic similarity can produce imperfect
matches: the unwinding example includes Starlight Dance. Exact mood
and genre controls can enforce requirements.

Likes and mixes are stored locally for one user and do not train
the model. Similarity scores are ranking values, not confidence
probabilities.

The architecture source is included in architecture.mmd.