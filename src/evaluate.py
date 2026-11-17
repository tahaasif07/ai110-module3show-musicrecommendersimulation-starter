"""Evaluate recommendation behavior and guardrails using synthetic songs."""

from copy import deepcopy
import unittest
from unittest.mock import patch

from assistant import RequestError, answer_request


def sample_songs():
    """Create independent fixtures so one test cannot change another."""
    return [
        {
            "id": 1,
            "title": "Sample Pop",
            "artist": "Test Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "acousticness": 0.1
        },
        {
            "id": 2,
            "title": "Sample Study",
            "artist": "Test Artist",
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.3,
            "acousticness": 0.9
        },
        {
            "id": 3,
            "title": "Sample Rock",
            "artist": "Test Artist",
            "genre": "rock",
            "mood": "intense",
            "energy": 0.9,
            "acousticness": 0.1
        }
    ]


class MusicEvaluation(unittest.TestCase):
    def setUp(self):
        self.songs = sample_songs()

    def test_three_supported_requests(self):
        """Each request should select the corresponding catalog song."""
        examples = [
            ("happy pop high energy", 1),
            ("calm acoustic music for studying", 2),
            ("rock workout", 3)
        ]

        for request, expected_id in examples:
            with self.subTest(request=request):
                _, results = answer_request(request, self.songs)
                self.assertEqual(results[0][0]["id"], expected_id)

    def test_empty_request(self):
        with self.assertRaises(RequestError):
            answer_request("   ", self.songs)

    def test_unknown_request(self):
        with self.assertRaises(RequestError):
            answer_request("tell me tomorrow's weather", self.songs)

    def test_conflicting_preferences(self):
        """The parser must request clarification instead of guessing."""
        for request in ["pop rock", "low energy high energy"]:
            with self.subTest(request=request):
                with self.assertRaises(RequestError):
                    answer_request(request, self.songs)

    def test_exclusion_is_not_misread(self):
        with self.assertRaises(RequestError):
            answer_request("not pop", self.songs)

    def test_no_matching_song(self):
        """Do not silently replace a requested match with another genre."""
        with self.assertRaises(RequestError):
            answer_request("pop chill", self.songs)

    def test_acoustic_filter(self):
        _, results = answer_request("acoustic", self.songs)
        self.assertEqual([song["id"] for song, _, _ in results], [2])

    def test_invalid_catalog(self):
        """Check both out-of-range values and duplicate identities."""
        bad_energy = deepcopy(self.songs)
        bad_energy[0]["energy"] = float("nan")

        duplicate_id = deepcopy(self.songs)
        duplicate_id[1]["id"] = duplicate_id[0]["id"]

        for catalog in [[], bad_energy, duplicate_id]:
            with self.subTest(catalog=catalog):
                with self.assertRaises(RequestError):
                    answer_request("pop", catalog)

    def test_invalid_count(self):
        for count in [0, 11, True]:
            with self.subTest(count=count):
                with self.assertRaises(RequestError):
                    answer_request("pop", self.songs, k=count)

    def test_invalid_output_is_blocked(self):
        """Simulate a faulty ranking component returning an unknown song."""
        unknown_song = dict(self.songs[0])
        unknown_song["id"] = 999

        with patch(
            "assistant.recommend_songs",
            return_value=[(unknown_song, 3.0, "Invalid result")]
        ):
            with self.assertRaises(RequestError):
                answer_request("pop", self.songs)


if __name__ == "__main__":
    # unittest prints individual results; this adds a project-friendly
    # summary and makes failures visible to automated checks.
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MusicEvaluation)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    passed = result.testsRun - len(result.failures) - len(result.errors)

    print(f"\nEvaluation summary: {passed}/{result.testsRun} tests passed.")
    raise SystemExit(0 if result.wasSuccessful() else 1)