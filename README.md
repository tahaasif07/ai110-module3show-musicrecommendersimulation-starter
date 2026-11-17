
# Tempo — Project 4: Applied AI System
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