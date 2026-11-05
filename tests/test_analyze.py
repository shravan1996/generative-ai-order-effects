"""The flip rates and cell classes mean what the pre-registration says they mean."""
import json
import unittest
from pathlib import Path

import analyze

ROOT = Path(__file__).parent.parent


class Flips(unittest.TestCase):
    def test_no_movement_at_all(self):
        self.assertEqual(analyze.repeat_and_swap([0, 0], [0, 0]), (0, 0))

    def test_pick_follows_the_slot_completely(self):
        # Option 0 whenever it's first, option 1 whenever it's first: the order decides everything.
        self.assertEqual(analyze.repeat_and_swap([0, 0, 0, 0], [1, 1, 1, 1]), (0, 1))

    def test_pure_noise_has_no_order_effect(self):
        rep, swap = analyze.repeat_and_swap([0, 1, 0, 1], [0, 1, 0, 1])
        self.assertAlmostEqual(rep, 4 / 6 * 1 / 1 * 2 / 2)
        self.assertAlmostEqual(swap, 8 / 16)

    def test_flips_between_two_sources(self):
        self.assertEqual(analyze.flips_between([0, 0], [1, 1]), 1)
        self.assertEqual(analyze.flips_between([0, 1], [0, 0]), 0.5)
        self.assertIsNone(analyze.flips_between([], [0]))


class Classes(unittest.TestCase):
    def test_stable_is_the_same_option_in_both_orders(self):
        self.assertEqual(analyze.classify({"ab": [1, 1, 1, 0], "ba": [1, 1, 1, 1]}), "stable")

    def test_follows_first_means_the_first_listed_option_wins(self):
        self.assertEqual(analyze.classify({"ab": [0, 0, 0, 0], "ba": [1, 1, 1, 1]}), "follows_first")

    def test_follows_second_means_the_last_listed_option_wins(self):
        self.assertEqual(analyze.classify({"ab": [1, 1, 1, 1], "ba": [0, 0, 0, 0]}), "follows_second")

    def test_anything_else_is_mixed(self):
        self.assertEqual(analyze.classify({"ab": [0, 1, 0, 1], "ba": [0, 0, 0, 0]}), "mixed")


class Published(unittest.TestCase):
    """The replies in the repository are the ones the article reports."""

    def test_every_registered_run_is_complete(self):
        rows = analyze.load()
        count = lambda f: sum(1 for r in rows if f(r))
        plain = lambda r: r["arm"] == "plain" and r.get("effort") is None
        self.assertEqual(count(lambda r: plain(r) and r["tier"] in ("close", "twin", "clear")), 864)
        self.assertEqual(count(lambda r: plain(r) and r["tier"] == "five"), 180)
        self.assertEqual(count(lambda r: r["arm"] == "tie_ok"), 336)
        self.assertEqual(count(lambda r: r["arm"] == "score_first"), 336)
        self.assertEqual(count(lambda r: r.get("effort") == "low"), 120)
        self.assertEqual(count(lambda r: r.get("effort") == "xhigh"), 120)
        self.assertEqual(count(lambda r: r["arm"] == "neutral_labels"), 80)

    def test_summary_is_up_to_date(self):
        summary = json.loads((ROOT / "results" / "summary.json").read_text())
        self.assertEqual(summary["calls"], len(analyze.load()))


if __name__ == "__main__":
    unittest.main()
