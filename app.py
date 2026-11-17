"""Tempo: a local music discovery app with semantic recommendations."""

import hashlib
import html
from pathlib import Path

import streamlit as st

from src.ai_playlist import MusicEngine
from src.recommender import load_songs
from src.storage import load_library, save_library


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "songs.csv"

st.set_page_config(
    page_title="Tempo",
    page_icon="🎧",
    layout="wide"
)

# CSS must stay inside this quoted text block.
st.markdown(
    """
    <style>
    .stApp {
        background: #101211;
        color: #f0f2ed;
    }

    [data-testid="stSidebar"] {
        background: #0b0d0c;
        border-right: 1px solid #202722;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    .tempo-brand {
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -1px;
        margin: 10px 0 4px;
    }

    .small-label {
        color: #a6baac;
        font-size: 11px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    .intro {
        padding: 35px 0 20px;
    }

    .intro h1 {
        font-size: clamp(40px, 5vw, 68px);
        line-height: 1.05;
        letter-spacing: -3px;
        font-weight: 650;
        margin: 14px 0 18px;
    }

    .intro p {
        color: #a5afa7;
        font-size: 18px;
        max-width: 600px;
    }

    .cover {
        height: 185px;
        border-radius: 12px;
        position: relative;
        overflow: hidden;
        margin-bottom: 14px;
    }

    .cover::before {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        border: 1px solid rgba(255,255,255,.25);
        border-radius: 50%;
        top: -70px;
        right: -50px;
    }

    .cover::after {
        content: "";
        position: absolute;
        width: 150px;
        height: 150px;
        border: 35px solid rgba(255,255,255,.09);
        border-radius: 50%;
        bottom: -100px;
        left: -50px;
    }

    .cover-label {
        position: absolute;
        bottom: 18px;
        left: 18px;
        font-size: 11px;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: rgba(255,255,255,.8);
    }

    .track-title {
        font-size: 18px;
        font-weight: 650;
        letter-spacing: -.3px;
        margin-bottom: 4px;
    }

    .track-artist {
        font-size: 14px;
        color: #a5afa7;
        margin-bottom: 12px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px;
    }

    div.stButton > button {
        border-radius: 20px;
        border-color: #303932;
    }

    div.stButton > button:hover {
        border-color: #a6d8b2;
        color: #c9f0d1;
    }

    /* Native navigation buttons replace the radio circles. */
    .st-key-navigation button {
        justify-content: flex-start;
        border-radius: 8px;
        padding: 13px 16px;
        min-height: 48px;
        font-weight: 600;
    }

    .st-key-navigation button[kind="primary"] {
        background: #222d25;
        border-color: #222d25;
        color: #eff9f1;
    }

    .st-key-navigation button:focus-visible {
        outline: 2px solid #a7d9b2;
        outline-offset: 2px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_resource(show_spinner=False)
def get_engine(csv_path, modified_time):
    """Cache the model and rebuild its index if the CSV changes."""
    return MusicEngine(load_songs(csv_path))


try:
    songs = load_songs(str(DATA_PATH))
    library = load_library()
except (OSError, ValueError, KeyError) as error:
    st.error(f"Could not open your collection: {error}")
    st.stop()

if not songs:
    st.info("Add songs to data/songs.csv to start your collection.")
    st.stop()

by_id = {song["id"]: song for song in songs}
genres = sorted({song["genre"].strip().lower() for song in songs})
moods = sorted({song["mood"].strip().lower() for song in songs})

# Keep the current mix and selected track when a button reruns the app.
st.session_state.setdefault("mix", [])
st.session_state.setdefault("mix_request", "")
st.session_state.setdefault("selected_song", None)


def persist():
    """Report a failed write instead of falsely confirming a save."""
    try:
        save_library(library)
    except OSError as error:
        st.error(f"Your changes could not be saved: {error}")
        st.stop()


def show_cards(items, prefix):
    """Display songs with like, view, and optional match details."""
    if not items:
        st.caption("Nothing here yet.")
        return

    palettes = [
        ("#263c42", "#71948c"),
        ("#4a344c", "#a47f85"),
        ("#38412b", "#8e9a6b"),
        ("#473729", "#b08b65"),
        ("#2c354e", "#7b84a9"),
        ("#493330", "#b47868")
    ]

    for start in range(0, len(items), 4):
        columns = st.columns(4, gap="small")

        for column, item in zip(columns, items[start:start + 4]):
            song = item.get("song", item)
            song_id = song["id"]

            # Give each song consistent decorative colors.
            # These graphics are not actual album covers.
            digest = hashlib.sha256(str(song_id).encode()).digest()[0]
            first, second = palettes[digest % len(palettes)]

            with column:
                with st.container(
                    border=False,
                    key=f"trackcard_{prefix}_{song_id}"
                ):                    # Escape catalog text before placing it in HTML.
                    st.markdown(
                        f"""
                        <div class="cover" style="background:
                        linear-gradient(135deg, {first}, {second});">
                            <div class="cover-label">
                                {html.escape(song["genre"])}
                            </div>
                        </div>
                        <div class="track-title">
                            {html.escape(song["title"])}
                        </div>
                        <div class="track-artist">
                            {html.escape(song["artist"])}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    left, right = st.columns(2)
                    liked = song_id in library["liked"]

                    with left:
                        if st.button(
                            "♥ Saved" if liked else "♡ Like",
                            key=f"{prefix}_like_{song_id}",
                            use_container_width=True
                        ):
                            if liked:
                                library["liked"].remove(song_id)
                            else:
                                library["liked"].append(song_id)

                            persist()
                            st.rerun()

                    with right:
                        if st.button(
                            "View",
                            key=f"{prefix}_view_{song_id}",
                            use_container_width=True
                        ):
                            st.session_state["selected_song"] = song_id
                            st.rerun()

                    if "description" in item:
                        with st.expander("Behind the match"):
                            st.write(item["description"])
                            st.caption(
                                "Listening suggestions come from genre, mood, "
                                "and musical attributes—not audio analysis."
                            )


with st.sidebar:
    st.markdown(
        '<div class="tempo-brand">'
        'tempo<span style="color:#a7d9b2">.</span>'
        '</div>',
        unsafe_allow_html=True
    )
    st.caption("A little closer to your next favorite.")
    st.write("")

    # Native buttons preserve keyboard navigation without radio circles.
    st.session_state.setdefault("page", "For you")

    with st.container(key="navigation"):
        for destination, icon in [
            ("For you", ":material/home:"),
            ("Search", ":material/search:"),
            ("Your library", ":material/library_music:")
        ]:
            if st.button(
                destination,
                icon=icon,
                key=f"nav_{destination}",
                type=(
                    "primary"
                    if st.session_state["page"] == destination
                    else "tertiary"
                ),
                use_container_width=True
            ):
                st.session_state["page"] = destination
                st.rerun()

    page = st.session_state["page"]

    st.write("")
    st.divider()
    st.caption(f"{len(songs)} songs in your collection")
    st.caption(f"{len(library['liked'])} liked songs")

    if library["playlists"]:
        st.write("")
        st.caption("YOUR PLAYLISTS")
        for name in library["playlists"]:
            st.write(name)


if page == "For you":
    st.markdown(
        """
        <div class="intro">
            <div class="small-label">A soundtrack for right now</div>
            <h1>Find your next favorite.</h1>
            <p>A quiet evening. A little motivation.
            Somewhere in between. Start with a feeling.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # A container keeps the request box near the introduction.
    with st.container():
        request = st.chat_input("Describe what you feel like hearing…")

    suggestions = [
        ("Late-night focus", "Mellow music for a late-night study session"),
        ("A slower evening", "Gentle relaxed music for unwinding"),
        ("Find some energy", "Energetic upbeat music for a workout")
    ]

    columns = st.columns(3)

    for column, (label, prompt) in zip(columns, suggestions):
        with column:
            if st.button(label, use_container_width=True):
                request = prompt

    # Keep exact requirements available without a large form.
    with st.expander("A few preferences"):
        genre = st.selectbox("Stay with a genre", ["Any"] + genres)
        mood = st.selectbox("Stay with a mood", ["Any"] + moods)
        excluded = st.multiselect("Exclude genres", genres)
        acoustic = st.checkbox("Keep it acoustic")

        use_energy = st.checkbox("Set an energy preference")
        energy = 0.5

        if use_energy:
            energy = st.slider(
                "From laid-back to energetic",
                0.0, 1.0, 0.5, 0.05
            )

        st.caption(
            "Preferences apply to your next request. "
            "Use the exclusion control rather than writing 'no rock'."
        )

    if request:
        try:
            with st.spinner("Finding your sound…"):
                engine = get_engine(
                    str(DATA_PATH),
                    DATA_PATH.stat().st_mtime_ns
                )

                mix = engine.recommend(
                    query=request,
                    genre=genre,
                    mood=mood,
                    excluded_genres=excluded,
                    acoustic_only=acoustic,
                    target_energy=energy,
                    # Ignore default energy unless the user enables it.
                    semantic_weight=0.75 if use_energy else 1.0,
                    k=9
                )

            st.session_state["mix"] = mix
            st.session_state["mix_request"] = request

        except Exception as error:
            # Clear stale recommendations when a new request fails.
            st.session_state["mix"] = []
            st.error(f"Could not make this mix: {error}")

    mix = st.session_state["mix"]

    if mix:
        st.write("")
        st.subheader("Something for this moment")
        st.caption(st.session_state["mix_request"])

        with st.expander("Keep this mix"):
            with st.form("save_mix"):
                name = st.text_input(
                    "Give it a name",
                    placeholder="After hours",
                    max_chars=60
                )
                save = st.form_submit_button("Save to your library")

            if save:
                name = name.strip()

                if not name:
                    st.warning("Give your mix a name first.")
                elif name in library["playlists"]:
                    st.warning("You already have a mix with that name.")
                else:
                    library["playlists"][name] = [
                        item["song"]["id"] for item in mix
                    ]
                    persist()
                    st.rerun()

        show_cards(mix, "mix")

    else:
        st.write("")
        st.subheader("From your collection")
        st.caption("A few places to start.")
        show_cards(songs[:6], "collection")


elif page == "Search":
    st.markdown(
        """
        <div class="intro">
            <div class="small-label">Find something familiar</div>
            <h1>Search</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    search = st.text_input(
        "Search your collection",
        placeholder="A song, an artist, a mood…",
        label_visibility="collapsed"
    ).strip().lower()

    matches = [
        song for song in songs
        if search in " ".join(
            str(song[field])
            for field in ["title", "artist", "genre", "mood"]
        ).lower()
    ]

    st.write("")
    show_cards(matches, "search")


else:
    st.markdown(
        """
        <div class="intro">
            <div class="small-label">The ones you come back to</div>
            <h1>Your library</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    liked_tab, playlists_tab = st.tabs(["Liked songs", "Your mixes"])

    with liked_tab:
        liked_songs = [
            by_id[song_id]
            for song_id in library["liked"]
            if song_id in by_id
        ]

        if not liked_songs:
            st.caption("Tap Like on a song and it will be waiting here.")

        show_cards(liked_songs, "liked")

    with playlists_tab:
        if not library["playlists"]:
            st.caption("Save a mix from For you to start your collection.")
        else:
            selected = st.selectbox(
                "Choose a mix",
                list(library["playlists"]),
                label_visibility="collapsed"
            )

            playlist_songs = [
                by_id[song_id]
                for song_id in library["playlists"][selected]
                if song_id in by_id
            ]

            show_cards(playlist_songs, "playlist")

            with st.expander("Manage this mix"):
                if st.button("Delete mix"):
                    del library["playlists"][selected]
                    persist()
                    st.rerun()


# Keep selected track details available across navigation.
selected_id = st.session_state["selected_song"]

if selected_id in by_id:
    song = by_id[selected_id]

    st.divider()

    title_column, close_column = st.columns([8, 1])

    with title_column:
        st.subheader(song["title"])
        st.caption(f"{song['artist']} · {song['genre']} · {song['mood']}")

    with close_column:
        if st.button("Close"):
            st.session_state["selected_song"] = None
            st.rerun()

    audio_path = song.get("audio_path", "").strip()

    if audio_path:
        resolved = (ROOT / audio_path).resolve()

        # Only read supported audio files inside this project.
        if (
            resolved.is_relative_to(ROOT)
            and resolved.is_file()
            and resolved.suffix.lower() in {".mp3", ".wav", ".ogg"}
        ):
            st.audio(str(resolved))
        else:
            st.caption("The attached audio file is unavailable.")
    else:
        st.caption("Audio isn’t attached to this track yet.")
        # Keep the interface compact, with quiet surfaces and subtle hover states.
st.markdown(
    """
    <style>
    .stApp {
        background: #121212;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: #090909;
        border-right: none;
    }

    [data-testid="stSidebarUserContent"] {
        padding-top: 1.5rem;
    }

    .block-container {
        max-width: 1500px;
        padding: 2rem 2.5rem 4rem;
    }

    .tempo-brand {
        font-size: 28px;
        margin-bottom: 8px;
    }

    /* Compact navigation with labels aligned to the left. */
    .st-key-navigation {
        margin-top: 18px;
    }

    .st-key-navigation [data-testid="stVerticalBlock"] {
        gap: 4px;
    }

    .st-key-navigation [data-testid="stButton"] > button {
        justify-content: flex-start !important;
        border: none !important;
        border-radius: 6px !important;
        min-height: 44px;
        padding: 10px 14px !important;
        background: transparent;
        color: #b3b3b3;
        box-shadow: none;
    }

    .st-key-navigation [data-testid="stButton"] > button:hover {
        background: #191919;
        color: white;
    }

    .st-key-navigation [data-testid="stButton"] > button[kind="primary"] {
        background: #242424;
        color: white;
    }

    .st-key-navigation button:focus-visible {
        outline: 2px solid #1ed760;
        outline-offset: 2px;
    }

    /* Smaller page headings leave more room for music. */
    .intro {
        padding: 8px 0 14px;
    }

    .intro h1 {
        font-size: clamp(30px, 3vw, 44px);
        line-height: 1.15;
        letter-spacing: -1.5px;
        margin: 8px 0 12px;
        font-weight: 750;
    }

    .intro p {
        font-size: 15px;
        color: #a7a7a7;
    }

    .small-label {
        font-size: 10px;
        letter-spacing: 2px;
        color: #909090;
    }

    /* Cards blend into the page until hovered. */
    [class*="st-key-trackcard_"] {
        background: transparent;
        border-radius: 8px;
        padding: 12px;
        transition: background 160ms ease;
    }

    [class*="st-key-trackcard_"]:hover {
        background: #1c1c1c;
    }

    .cover {
        height: auto;
        aspect-ratio: 1 / 1;
        border-radius: 6px;
        margin-bottom: 12px;
        box-shadow: 0 8px 22px rgba(0,0,0,.25);
    }

    .cover-label {
        bottom: 14px;
        left: 14px;
        font-size: 10px;
        letter-spacing: 2px;
    }

    .track-title {
        font-size: 16px;
        font-weight: 650;
        margin-bottom: 3px;
    }

    .track-artist {
        font-size: 13px;
        color: #a7a7a7;
        margin-bottom: 6px;
    }

    /* Make song actions quiet instead of large outlined pills. */
    [class*="st-key-trackcard_"] [data-testid="stButton"] > button {
        background: transparent !important;
        border: none !important;
        border-radius: 5px !important;
        min-height: 32px;
        padding: 4px 8px !important;
        color: #b3b3b3;
        box-shadow: none;
    }

    [class*="st-key-trackcard_"] [data-testid="stButton"] > button:hover {
        background: #303030 !important;
        color: white;
    }

    [data-testid="stTextInput"] [data-baseweb="input"] {
        border-radius: 24px;
        background: #242424;
        border-color: transparent;
    }

    [data-testid="stTextInput"] input {
        padding: 12px 18px;
    }

    [data-testid="stExpander"] {
        border-color: #282828;
        border-radius: 8px;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    /* Hide Streamlit's running indicator and developer toolbar. */
[data-testid="stStatusWidget"],
[data-testid="stToolbar"],
[data-testid="stAppDeployButton"] {
    display: none !important;
}
    </style>
    """,
    unsafe_allow_html=True
)