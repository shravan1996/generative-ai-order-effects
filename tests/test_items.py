"""The items and the prompts built from them say what the trial claims they say."""
import json
import unittest
from pathlib import Path

import choose

ITEMS = json.loads((Path(__file__).parent.parent / "data" / "items.json").read_text())


class Items(unittest.TestCase):
    def test_counts(self):
        tiers = [i["tier"] for i in ITEMS]
        self.assertEqual(tiers.count("close"), 20)
        self.assertEqual(tiers.count("twin"), 8)
        self.assertEqual(tiers.count("clear"), 8)
        self.assertEqual(tiers.count("five"), 6)

    def test_every_domain_appears_in_each_pair_tier(self):
        for tier in ("close", "twin", "clear"):
            domains = {i["domain"] for i in ITEMS if i["tier"] == tier}
            self.assertEqual(domains, {"hire", "supplier", "project", "draft"}, tier)

    def test_ids_and_names_are_unique(self):
        ids = [i["id"] for i in ITEMS]
        self.assertEqual(len(ids), len(set(ids)))
        for item in ITEMS:
            names = [o["name"] for o in item["options"]]
            self.assertEqual(len(names), len(set(names)), item["id"])

    def test_twins_differ_only_by_name_or_by_a_word(self):
        for item in ITEMS:
            if item["tier"] != "twin":
                continue
            a, b = (o["text"] for o in item["options"])
            if item["domain"] == "draft":
                changed = set(a.split()) ^ set(b.split())
                self.assertLessEqual(len(changed), 4, item["id"])
            else:
                self.assertEqual(a, b, item["id"])

    def test_clear_items_name_a_better_option(self):
        for item in ITEMS:
            names = [o["name"] for o in item["options"]]
            if item["tier"] == "clear":
                self.assertIn(item["better"], names, item["id"])
            else:
                self.assertIsNone(item["better"], item["id"])

    def test_no_em_dashes(self):
        self.assertNotIn("—", json.dumps(ITEMS, ensure_ascii=False))


class Orders(unittest.TestCase):
    def test_pair_is_shown_both_ways(self):
        item = next(i for i in ITEMS if i["tier"] == "close")
        self.assertEqual(choose.orders(item), [[0, 1], [1, 0]])

    def test_every_option_visits_every_slot_in_a_shortlist(self):
        item = next(i for i in ITEMS if i["tier"] == "five")
        orders = choose.orders(item)
        self.assertEqual(len(orders), 5)
        for slot in range(5):
            self.assertEqual(sorted(o[slot] for o in orders), [0, 1, 2, 3, 4])

    def test_swapping_changes_nothing_but_the_order(self):
        for item in ITEMS:
            if len(item["options"]) != 2 or item["domain"] == "draft":
                continue
            ab = choose.message(item, [0, 1])
            ba = choose.message(item, [1, 0])
            self.assertNotEqual(ab, ba)
            self.assertEqual(sorted(ab.split("\n")), sorted(ba.split("\n")), item["id"])

    def test_drafts_are_labelled_by_position(self):
        item = next(i for i in ITEMS if i["id"] == "draft-1")
        ab = choose.message(item, [0, 1])
        ba = choose.message(item, [1, 0])
        self.assertLess(ab.index("Draft 1"), ab.index("Draft 2"))
        self.assertLess(ba.index("Draft 1"), ba.index("Draft 2"))
        # The first draft's text follows the label 'Draft 1' in one order and 'Draft 2' in the other.
        self.assertIn("Draft 1\n" + item["options"][0]["text"], ab)
        self.assertIn("Draft 2\n" + item["options"][0]["text"], ba)

    def test_arms_only_add_a_closing_line(self):
        item = ITEMS[0]
        plain = choose.message(item, [0, 1], "plain")
        for arm in ("tie_ok", "score_first"):
            self.assertTrue(choose.message(item, [0, 1], arm).startswith(plain + "\n\n"))


class Reading(unittest.TestCase):
    item = next(i for i in ITEMS if i["id"] == "hire-1")
    draft = next(i for i in ITEMS if i["id"] == "draft-1")

    def test_last_pick_wins(self):
        self.assertEqual(choose.final_pick("Pick: Anna\nActually\nPick: Emma Turner"), "Emma Turner")

    def test_markdown_is_stripped(self):
        self.assertEqual(choose.final_pick("**Pick: Emma Turner**"), "Emma Turner")
        self.assertEqual(choose.final_pick("Pick: **Emma Turner**."), "Emma Turner")

    def test_missing_pick(self):
        self.assertIsNone(choose.final_pick("I'd go with Emma."))
        self.assertEqual(choose.read_pick(None, self.item, [0, 1]), (None, None))

    def test_pick_maps_to_option_and_slot(self):
        self.assertEqual(choose.read_pick("Emma Turner", self.item, [0, 1]), (1, 1))
        self.assertEqual(choose.read_pick("Emma Turner", self.item, [1, 0]), (1, 0))

    def test_draft_label_maps_through_the_order(self):
        self.assertEqual(choose.read_pick("Draft 1", self.draft, [0, 1]), (0, 0))
        self.assertEqual(choose.read_pick("Draft 1", self.draft, [1, 0]), (1, 0))
        self.assertEqual(choose.read_pick("Draft 2", self.draft, [1, 0]), (0, 1))

    def test_too_close(self):
        self.assertEqual(choose.read_pick("too close", self.item, [0, 1]), ("tie", None))

    def test_naming_both_is_unreadable(self):
        self.assertEqual(choose.read_pick("Anna Clarke or Emma Turner", self.item, [0, 1]), (None, None))


if __name__ == "__main__":
    unittest.main()
