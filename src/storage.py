"""Persist a single local user's liked songs and playlists."""

import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LIBRARY_PATH = ROOT / "user_data" / "library.json"


def load_library():
    """Return an empty library on first use, but report corrupted files."""
    if not LIBRARY_PATH.exists():
        return {"liked": [], "playlists": {}}

    try:
        with LIBRARY_PATH.open("r", encoding="utf-8") as file:
            library = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            "Could not read your saved library. "
            "Check user_data/library.json before changing it."
        ) from error

    # Do not silently overwrite a file with an unexpected structure.
    if not isinstance(library, dict):
        raise ValueError("The saved library has an invalid format.")

    liked = library.get("liked")
    playlists = library.get("playlists")

    if (
        not isinstance(liked, list)
        or not all(type(song_id) is int for song_id in liked)
        or not isinstance(playlists, dict)
    ):
        raise ValueError("The saved library has an invalid format.")

    for name, ids in playlists.items():
        if (
            not isinstance(name, str)
            or not isinstance(ids, list)
            or not all(type(song_id) is int for song_id in ids)
        ):
            raise ValueError("A saved playlist has an invalid format.")

    return library


def save_library(library):
    """Replace the save file only after the new JSON is fully written."""
    LIBRARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        # Writing beside the destination allows an atomic replacement.
        # A failed write leaves the previous library intact.
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=LIBRARY_PATH.parent,
            suffix=".tmp",
            delete=False
        ) as file:
            temporary_path = Path(file.name)
            json.dump(library, file, indent=2, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, LIBRARY_PATH)

    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()