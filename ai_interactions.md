# AI Collaboration and System Design

## How I Used AI

I used AI to help extend my AI110 Module 3 music recommender
into Tempo. I shared the original project, assignment rubric,
source files, screenshots, and error messages.

AI helped with implementation, interface design, debugging,
evaluation, and documentation. I applied changes in VS Code
and ran the system locally.

For example, after I pasted CSS outside a Python string,
the app reported a SyntaxError. I shared the error, and the
assistant provided a complete replacement app.py with the
CSS correctly enclosed.

## An AI Suggestion I Accepted

I accepted using a local pretrained sentence embedding model
because I could not obtain an API key. MiniLM allows users
to describe a listening moment instead of entering only
structured genre, mood, and energy preferences.

The model retrieves songs using metadata descriptions.
It does not generate conversation or analyze audio.

## Suggestions I Rejected or Revised

I rejected the mechanical dashboard appearance and visible
sidebar radio controls. I requested a more seamless,
Spotify-inspired interface.

The design was revised to use navigation buttons, smaller
headings, and less prominent song-card borders and actions.

An early explanation-only extension was also revised because
the original recommender already provided explanations.
The substantial extension became semantic retrieval with
integrated validation, filtering, and evaluation.

## Testing and Observations

I ran:

python3 -m src.evaluate_semantic

The real-model evaluation passed 9/9 checks on my Mac.
It tested three listening requests and checked output validity,
input rejection, exact filtering, and repeatable rankings.

For the rainy late-night study request, the results were:

- Deep Focus
- Spacewalk Thoughts
- Focus Flow
- Library Rain
- Midnight Coding

The unwinding request also returned Starlight Dance.
This illustrates that passing technical checks does not
guarantee every recommendation matches the intended mood.

## Design Tradeoffs

Free-text requests make discovery more flexible, while explicit
filters make requirements enforceable. The system uses exact
controls for genre, mood, exclusions, and acoustic preferences
because semantic similarity alone cannot guarantee compliance.

The default ranking does not use the preset energy value.
Energy contributes only when the user enables that preference.

The app saves likes and mixes locally, but these actions do not
train the model or change future rankings.

## Limitations and Future Improvements

The catalog contains only 20 fictional songs. Listening contexts
are handcrafted suggestions from metadata rather than verified
audio properties.

A useful next step would be collecting independent relevance
ratings for more requests and comparing the semantic system
with the original scorer on held-out examples.

Other improvements could include richer verified metadata,
better rejection of unrelated requests, and licensed audio previews.