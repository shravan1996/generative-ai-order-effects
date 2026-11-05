"""Score every reply against PREREGISTRATION.md and write results/summary.json.

No model calls and no network: this reads results/calls.jsonl and data/items.json.

    python3 analyze.py
"""
import json
import os
import random
import re
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path

import choose

ROOT = Path(__file__).parent
ITEMS = {i["id"]: i for i in json.loads((ROOT / "data" / "items.json").read_text())}
CALLS = Path(os.environ.get("ORDER_CALLS", ROOT / "results" / "calls.jsonl"))
MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]
SEED = 7
RESAMPLES = 10_000

# Phrases that say nothing separates the options. A twin reply counts if any of these appears.
TIED = re.compile(
    r"identical|same (?:cv|facts|quote|offer|proposal|project|terms|details|numbers|text|email|message|draft)"
    r"|(?:no|nothing|n't).{0,40}(?:separate|distinguish|differen|favou?r|advantage|between)"
    r"|coin[- ]?(?:toss|flip)|arbitrary|effectively the same|essentially the same|virtually the same"
    r"|interchangeable|word[- ]for[- ]word|equally",
    re.IGNORECASE | re.DOTALL)
# Phrases that flag a decision as close, looked for in close-item replies.
CLOSE_CALL = re.compile(
    r"close (?:call|decision|one)|could go either way|either (?:one )?(?:could|would)|finely balanced"
    r"|toss[- ]?up|tough call|hard call|judgement call|judgment call|genuine(?:ly)? (?:close|trade)|both are (?:good|strong|reasonable|defensible)",
    re.IGNORECASE)


def load():
    """Every ok call, with its pick read again by the current parser (see deviation 1)."""
    rows = []
    if not CALLS.exists():
        return rows
    for line in CALLS.read_text().splitlines():
        r = json.loads(line)
        if r.get("status") == "ok":
            r["pick"], r["slot"] = choose.read_pick(choose.final_pick(r["content"]), ITEMS[r["item"]], r["order"])
            rows.append(r)
    return rows


def repeat_and_swap(a, b):
    """a and b are picks (option index) under the two orders. Returns (repeat flip, swap flip)."""
    same = list(combinations(a, 2)) + list(combinations(b, 2))
    cross = list(product(a, b))
    if not same or not cross:
        return None, None
    return (sum(x != y for x, y in same) / len(same), sum(x != y for x, y in cross) / len(cross))


def pair_cells(rows, reps=None):
    """{(model, item): {'ab': [picks], 'ba': [picks]}} for two-option items, readable picks only."""
    cells = defaultdict(lambda: {"ab": [], "ba": []})
    for r in rows:
        if len(r["order"]) != 2 or not isinstance(r.get("pick"), int):
            continue
        if reps is not None and r["rep"] >= reps:
            continue
        cells[(r["model"], r["item"])]["ab" if r["order"] == [0, 1] else "ba"].append(r["pick"])
    return cells


def tier_stats(cells, tier, models):
    """Mean repeat flip, swap flip, order effect and first-slot share per item, across given models."""
    per_item = defaultdict(list)
    for (model, item), c in cells.items():
        if ITEMS[item]["tier"] != tier or model not in models:
            continue
        rep, swap = repeat_and_swap(c["ab"], c["ba"])
        if rep is None:
            continue
        first = sum(p == 0 for p in c["ab"]) + sum(p == 1 for p in c["ba"])
        n = len(c["ab"]) + len(c["ba"])
        per_item[item].append((rep, swap, first / n))
    return per_item


def summarise(per_item):
    if not per_item:
        return None
    vals = [v for vs in per_item.values() for v in vs]
    rep = sum(v[0] for v in vals) / len(vals)
    swap = sum(v[1] for v in vals) / len(vals)
    first = sum(v[2] for v in vals) / len(vals)
    lo, hi = bootstrap(per_item, lambda v: v[1] - v[0])
    return {"repeat_flip": rep, "swap_flip": swap, "order_effect": swap - rep,
            "order_effect_ci": [lo, hi], "first_slot": first, "first_slot_ci": list(bootstrap(per_item, lambda v: v[2])),
            "items": len(per_item), "cells": len(vals)}


def bootstrap(per_item, f):
    rng = random.Random(SEED)
    keys = sorted(per_item)
    out = []
    for _ in range(RESAMPLES):
        vals = []
        for k in rng.choices(keys, k=len(keys)):
            vals.extend(f(v) for v in per_item[k])
        out.append(sum(vals) / len(vals))
    out.sort()
    return out[int(0.025 * RESAMPLES)], out[int(0.975 * RESAMPLES) - 1]


def classify(c):
    """Stable, follows the order, or mixed, from the main run's replies in each order."""
    a, b = c["ab"], c["ba"]
    if not a or not b:
        return "mixed"
    need_a = 3 * len(a) / 4
    need_b = 3 * len(b) / 4
    for opt in (0, 1):
        if sum(p == opt for p in a) >= need_a and sum(p == opt for p in b) >= need_b:
            return "stable"
    # Slot 0 is option 0 in ab and option 1 in ba; slot 1 is the reverse.
    if sum(p == 0 for p in a) >= need_a and sum(p == 1 for p in b) >= need_b:
        return "follows_first"
    if sum(p == 1 for p in a) >= need_a and sum(p == 0 for p in b) >= need_b:
        return "follows_second"
    return "mixed"


def arm_rows(rows, arm, effort=None):
    return [r for r in rows if r["arm"] == arm and r.get("effort") == effort]


def main():
    rows = load()
    main_rows = arm_rows(rows, "plain")
    pair_rows = [r for r in main_rows if r["tier"] in ("close", "twin", "clear")]
    cells = pair_cells(pair_rows)
    out = {"calls": len(rows), "cost_usd": round(sum(r.get("cost_usd") or 0 for r in rows), 2),
           "seconds_mean": round(sum(r.get("seconds") or 0 for r in rows) / max(1, len(rows)), 1)}

    out["unreadable"] = {
        m: sum(1 for r in rows if r["model"] == m and r.get("pick") is None) for m in MODELS}

    # H1 and the tier table.
    out["tiers"] = {}
    for tier in ("close", "twin", "clear"):
        out["tiers"][tier] = {"pooled": summarise(tier_stats(cells, tier, MODELS))}
        for m in MODELS:
            out["tiers"][tier][m] = summarise(tier_stats(cells, tier, [m]))

    # By kind of decision, close items only.
    out["close_by_domain"] = {}
    for dom in ("hire", "supplier", "project", "draft"):
        sub = {k: v for k, v in cells.items() if ITEMS[k[1]]["domain"] == dom}
        out["close_by_domain"][dom] = summarise(tier_stats(sub, "close", MODELS))

    # Cell classes.
    classes = defaultdict(lambda: defaultdict(int))
    cell_table = []
    for (m, item), c in sorted(cells.items()):
        if ITEMS[item]["tier"] != "close":
            continue
        k = classify(c)
        classes[m][k] += 1
        classes["all"][k] += 1
        cell_table.append({"model": m, "item": item, "class": k, "ab": c["ab"], "ba": c["ba"]})
    out["close_classes"] = {m: dict(v) for m, v in classes.items()}
    out["close_cells"] = cell_table

    # H2: how often the worse option was picked on clear items.
    wrong = defaultdict(lambda: [0, 0])
    wrong_list = []
    for r in pair_rows:
        if r["tier"] != "clear" or not isinstance(r.get("pick"), int):
            continue
        item = ITEMS[r["item"]]
        bad = item["options"][r["pick"]]["name"] != item["better"]
        for key in (r["model"], "all"):
            wrong[key][0] += bad
            wrong[key][1] += 1
        if bad:
            wrong_list.append({"model": r["model"], "item": r["item"], "order": r["order"], "rep": r["rep"]})
    out["clear_wrong"] = {k: {"wrong": v[0], "of": v[1]} for k, v in wrong.items()}
    out["clear_wrong_list"] = wrong_list

    # H3: do twin replies say so?
    tied = defaultdict(lambda: [0, 0])
    for r in pair_rows:
        if r["tier"] != "twin":
            continue
        for key in (r["model"], "all"):
            tied[key][0] += bool(TIED.search(r["content"] or ""))
            tied[key][1] += 1
    out["twin_flagged"] = {k: {"flagged": v[0], "of": v[1]} for k, v in tied.items()}

    # Do close replies flag that the decision is close, and does that vary when the order matters?
    flagged = defaultdict(lambda: [0, 0])
    cls = {(c["model"], c["item"]): c["class"] for c in cell_table}
    for r in pair_rows:
        if r["tier"] != "close":
            continue
        hit = bool(CLOSE_CALL.search(r["content"] or ""))
        for key in (r["model"], "all", "class:" + cls.get((r["model"], r["item"]), "mixed")):
            flagged[key][0] += hit
            flagged[key][1] += 1
    out["close_flagged"] = {k: {"flagged": v[0], "of": v[1]} for k, v in flagged.items()}

    # H4: closing lines, compared with the first two replies per order of the plain run.
    plain2 = pair_cells(pair_rows, reps=2)
    out["arms"] = {"plain_2reps": {"pooled": summarise(tier_stats(plain2, "close", MODELS))}}
    for m in MODELS:
        out["arms"]["plain_2reps"][m] = summarise(tier_stats(plain2, "close", [m]))
    for arm in ("tie_ok", "score_first"):
        sub = arm_rows(rows, arm)
        c = pair_cells(sub)
        if not c:
            continue
        out["arms"][arm] = {"pooled": summarise(tier_stats(c, "close", MODELS))}
        for m in MODELS:
            out["arms"][arm][m] = summarise(tier_stats(c, "close", [m]))
        wrong_arm = [0, 0]
        for r in sub:
            if r["tier"] == "clear" and isinstance(r.get("pick"), int):
                item = ITEMS[r["item"]]
                wrong_arm[0] += item["options"][r["pick"]]["name"] != item["better"]
                wrong_arm[1] += 1
        out["arms"][arm]["clear_wrong"] = {"wrong": wrong_arm[0], "of": wrong_arm[1]}
        ties = defaultdict(lambda: [0, 0])
        for r in sub:
            for key in ((r["tier"], r["model"]), (r["tier"], "all")):
                ties[key][0] += r.get("pick") == "tie"
                ties[key][1] += 1
        out["arms"][arm]["too_close"] = {f"{k[0]}/{k[1]}": {"said": v[0], "of": v[1]} for k, v in ties.items()}

    # tie_ok: order effect counting "too close" as its own answer, not leaving it out.
    sub = arm_rows(rows, "tie_ok")
    if sub:
        withtie = defaultdict(lambda: {"ab": [], "ba": []})
        for r in sub:
            if r["tier"] == "close" and r.get("pick") is not None:
                withtie[(r["model"], r["item"])]["ab" if r["order"] == [0, 1] else "ba"].append(r["pick"])
        per = defaultdict(list)
        for (m, it), c in withtie.items():
            rep, swap = repeat_and_swap(c["ab"], c["ba"])
            if rep is not None:
                per[it].append((rep, swap, 0))
        out["arms"]["tie_ok"]["pooled_counting_ties"] = summarise(per)

    # H5: effort on Sonnet.
    out["effort"] = {"default": summarise(tier_stats(pair_cells([r for r in pair_rows if r["model"] == "claude-sonnet-5-5"], reps=3), "close", ["claude-sonnet-5-5"]))}
    for eff in ("low", "xhigh"):
        c = pair_cells(arm_rows(rows, "plain", eff))
        if c:
            out["effort"][eff] = summarise(tier_stats(c, "close", ["claude-sonnet-5-5"]))
            sel = arm_rows(rows, "plain", eff)
            out["effort"][eff]["thinking_tokens"] = round(sum(r.get("thinking_tokens") or 0 for r in sel) / len(sel))
            out["effort"][eff]["cost_per_call"] = round(sum(r.get("cost_usd") or 0 for r in sel) / len(sel), 4)
            out["effort"][eff]["seconds"] = round(sum(r.get("seconds") or 0 for r in sel) / len(sel), 1)
    sel = [r for r in pair_rows if r["model"] == "claude-sonnet-5-5" and r["tier"] == "close"]
    if sel:
        out["effort"]["default"]["thinking_tokens"] = round(sum(r.get("thinking_tokens") or 0 for r in sel) / len(sel))
        out["effort"]["default"]["cost_per_call"] = round(sum(r.get("cost_usd") or 0 for r in sel) / len(sel), 4)
        out["effort"]["default"]["seconds"] = round(sum(r.get("seconds") or 0 for r in sel) / len(sel), 1)

    # H6: shortlists.
    five = [r for r in main_rows if r["tier"] == "five" and isinstance(r.get("slot"), int)]
    if five:
        out["five"] = {}
        for key in MODELS + ["all"]:
            sel = [r for r in five if key == "all" or r["model"] == key]
            n = len(sel)
            out["five"][key] = {"n": n, "slots": [sum(r["slot"] == s for r in sel) / n for s in range(5)]}
        by_item = defaultdict(list)
        for r in five:
            by_item[r["item"]].append((0, 0, r["slot"] == 0))
        out["five"]["first_slot_ci"] = list(bootstrap(by_item, lambda v: v[2]))
        # How concentrated were the picks on one option, whatever its slot?
        out["five"]["top_option_share"] = {}
        for it in sorted(by_item):
            for m in MODELS + ["all"]:
                sel = [r for r in five if r["item"] == it and (m == "all" or r["model"] == m)]
                if not sel:
                    continue
                counts = defaultdict(int)
                for r in sel:
                    counts[r["pick"]] += 1
                top = max(counts, key=counts.get)
                out["five"]["top_option_share"].setdefault(it, {})[m] = {
                    "option": ITEMS[it]["options"][top]["name"], "share": counts[top] / len(sel)}

    # The two-chat swap test: ask once in each order. How often does it raise the alarm?
    out["swap_test"] = {}
    groups = defaultdict(list)
    for (m, item), c in cells.items():
        rep, swap = repeat_and_swap(c["ab"], c["ba"])
        if swap is None:
            continue
        tier = ITEMS[item]["tier"]
        groups[tier].append(swap)
        if tier == "close":
            groups["close:" + classify(c)].append(swap)
    for k, v in groups.items():
        out["swap_test"][k] = {"disagree": sum(v) / len(v), "cells": len(v)}

    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print_report(out)


def pct(x):
    return "n/a" if x is None else f"{100 * x:.1f}"


def line(name, s):
    if not s:
        print(f"  {name:28} no data")
        return
    print(f"  {name:28} repeat {pct(s['repeat_flip']):>5}  swap {pct(s['swap_flip']):>5}  "
          f"effect {pct(s['order_effect']):>5} [{pct(s['order_effect_ci'][0])}, {pct(s['order_effect_ci'][1])}]  "
          f"first-slot {pct(s['first_slot']):>5}  ({s['cells']} cells)")


def print_report(o):
    print(f"{o['calls']} calls, ${o['cost_usd']}, {o['seconds_mean']} s mean. Unreadable: {o['unreadable']}")
    for tier, d in o["tiers"].items():
        print(tier.upper())
        for k, s in d.items():
            line(k, s)
    print("CLOSE BY KIND")
    for k, s in o["close_by_domain"].items():
        line(k, s)
    print("CLASSES", json.dumps(o["close_classes"]))
    print("CLEAR WRONG", json.dumps(o["clear_wrong"]), o["clear_wrong_list"][:10])
    print("TWIN FLAGGED", json.dumps(o["twin_flagged"]))
    print("CLOSE FLAGGED", json.dumps(o["close_flagged"]))
    print("ARMS")
    for arm, d in o["arms"].items():
        for k, s in d.items():
            if k in ("clear_wrong", "too_close"):
                print(f"  {arm} {k}: {json.dumps(s)}")
            else:
                line(f"{arm} {k}", s)
    print("EFFORT")
    for k, s in o["effort"].items():
        line(k, s)
        if s:
            print(f"    thinking {s.get('thinking_tokens')}, ${s.get('cost_per_call')}, {s.get('seconds')} s")
    if "five" in o:
        print("FIVE")
        for k, s in o["five"].items():
            if isinstance(s, dict) and "slots" in s:
                print(f"  {k:28} n={s['n']}  " + "  ".join(pct(x) for x in s["slots"]))
        print("  first slot CI", [pct(x) for x in o["five"]["first_slot_ci"]])
        print("  top options", json.dumps(o["five"]["top_option_share"]))
    print("SWAP TEST", json.dumps(o["swap_test"]))


if __name__ == "__main__":
    main()
