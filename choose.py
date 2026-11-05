"""Ask Claude to choose between options, in both orders, several times over.

Claude is called through the Claude Code CLI (`claude -p`) with no tools, no MCP servers, no
settings and the one-line system prompt below. The CLI cannot set temperature, so every reply is
sampled at its default, and the models think adaptively before answering. Each call is a fresh
chat, so no reply ever sees another.

    python3 choose.py --models claude-haiku-5-5 --arm plain --tiers close twin clear --reps 4
    python3 choose.py --models claude-haiku-5-5 --arm plain --tiers five --reps 2

Every call is appended to results/calls.jsonl (or $ORDER_CALLS). A rerun skips calls that already
have an ok record, so collection can be stopped and restarted at any point.
"""
import argparse
import json
import os
import re
import subprocess
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
ITEMS = ROOT / "data" / "items.json"
CALLS = Path(os.environ.get("ORDER_CALLS", ROOT / "results" / "calls.jsonl"))
SCRATCH = os.environ.get("ORDER_CLAUDE_CWD", os.path.join(tempfile.gettempdir(), "order-claude"))

SYSTEM = ("You are a helpful assistant. End every reply with one line of the form 'Pick: <name>', "
          "using the exact name of the option you recommend.")

# What the user adds after the options, fixed before the main run.
ARMS = {
    "plain": "",
    "tie_ok": "If they're too close to call on what I've given you, say so and write 'Pick: too close'.",
    "score_first": "Before you choose, score each one out of 10 on whatever matters most here, then choose.",
}

_lock = threading.Lock()


def orders(item):
    """Every order the item is shown in: both orders for a pair, five rotations for a shortlist."""
    n = len(item["options"])
    if n == 2:
        return [[0, 1], [1, 0]]
    return [[(start + i) % n for i in range(n)] for start in range(n)]


def label(item, order, slot):
    """The name the model sees for the option in this slot. Drafts are labelled by position,
    the way people paste them, so 'Draft 1' is always whichever draft came first."""
    if item["domain"] == "draft":
        return f"Draft {slot + 1}"
    return item["options"][order[slot]]["name"]


def message(item, order, arm="plain"):
    blocks = []
    for slot, idx in enumerate(order):
        blocks.append(f"{label(item, order, slot)}\n{item['options'][idx]['text']}")
    parts = [item["ask"], *blocks]
    if ARMS[arm]:
        parts.append(ARMS[arm])
    return "\n\n".join(parts)


PICK = re.compile(r"pick\s*[:：]\s*(.+)", re.IGNORECASE)


def final_pick(text):
    """The text after the last 'Pick:' in the reply, without markdown decoration."""
    if not text:
        return None
    hits = PICK.findall(text)
    if not hits:
        return None
    return hits[-1].strip().strip("*`_'\"<>. ").strip()


def read_pick(raw, item, order):
    """Return (option index, slot). Option index is None for an unreadable pick, 'tie' for too close."""
    if raw is None:
        return None, None
    low = raw.lower()
    if "too close" in low:
        return "tie", None
    matches = []
    for slot, idx in enumerate(order):
        name = label(item, order, slot).lower()
        if name in low:
            matches.append((idx, slot))
    if len(matches) == 1:
        return matches[0]
    return None, None


def call_claude(model, prompt, effort=None, timeout=420):
    os.makedirs(SCRATCH, exist_ok=True)
    cmd = ["claude", "-p", "--tools", "", "--strict-mcp-config", "--setting-sources", "",
           "--no-session-persistence", "--output-format", "json", "--system-prompt", SYSTEM,
           "--model", model]
    if effort:
        cmd += ["--effort", effort]
    t = time.time()
    try:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=SCRATCH)
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "timeout", "seconds": round(time.time() - t, 3)}
    if proc.returncode != 0:
        return {"status": "error", "error": (proc.stderr or proc.stdout)[-500:], "seconds": round(time.time() - t, 3)}
    out = json.loads(proc.stdout)
    if out.get("is_error"):
        return {"status": "error", "error": str(out.get("result"))[-500:], "seconds": round(time.time() - t, 3)}
    u = out.get("usage", {})
    return {
        "status": "ok",
        "content": out.get("result"),
        "stop_reason": out.get("stop_reason"),
        "input_tokens": (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)
                        + (u.get("cache_read_input_tokens") or 0),
        "output_tokens": u.get("output_tokens"),
        "thinking_tokens": (u.get("output_tokens_details") or {}).get("thinking_tokens"),
        "cost_usd": out.get("total_cost_usd"),
        "seconds": round(time.time() - t, 3),
    }


def load_done():
    done = set()
    if CALLS.exists():
        for line in CALLS.read_text().splitlines():
            rec = json.loads(line)
            if rec.get("status") == "ok":
                done.add((rec["model"], rec.get("effort"), rec["arm"], rec["item"], tuple(rec["order"]), rec["rep"]))
    return done


def append(rec):
    with _lock:
        CALLS.parent.mkdir(exist_ok=True)
        with CALLS.open("a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run_one(model, effort, arm, item, order, rep):
    prompt = message(item, order, arm)
    out = call_claude(model, prompt, effort)
    rec = {"model": model, "effort": effort, "arm": arm, "item": item["id"], "tier": item["tier"],
           "domain": item["domain"], "order": order, "rep": rep, "message": prompt,
           "at": datetime.now().isoformat(timespec="seconds"), **out}
    if out["status"] == "ok":
        raw = final_pick(out["content"])
        idx, slot = read_pick(raw, item, order)
        rec.update({"raw_pick": raw, "pick": idx, "slot": slot})
    append(rec)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--arm", default="plain", choices=sorted(ARMS))
    ap.add_argument("--tiers", nargs="+", default=["close", "twin", "clear"])
    ap.add_argument("--reps", type=int, default=4)
    ap.add_argument("--effort", default=None, help="passed to the CLI's --effort; omit for its default")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--deadline", type=float, default=540, help="stop submitting new calls after this many seconds")
    ap.add_argument("--only", nargs="*", default=None, help="only these item ids (for a smoke test)")
    args = ap.parse_args()

    items = [i for i in json.loads(ITEMS.read_text()) if i["tier"] in args.tiers]
    if args.only:
        items = [i for i in items if i["id"] in args.only]
    done = load_done()
    jobs = []
    # Reps go first in the outer loop, so a stopped run still has balanced orders.
    for rep in range(args.reps):
        for model in args.models:
            for item in items:
                for order in orders(item):
                    if (model, args.effort, args.arm, item["id"], tuple(order), rep) not in done:
                        jobs.append((model, args.effort, args.arm, item, order, rep))
    print(f"{len(jobs)} calls to make", flush=True)
    start = time.time()
    ok = err = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = set()
        queue = list(jobs)
        while queue or pending:
            while queue and len(pending) < args.workers and time.time() - start < args.deadline:
                pending.add(pool.submit(run_one, *queue.pop(0)))
            if not pending:
                break
            for fut in as_completed(list(pending)):
                pending.discard(fut)
                rec = fut.result()
                if rec["status"] == "ok":
                    ok += 1
                else:
                    err += 1
                    print("error", rec["model"], rec["item"], rec.get("error", "")[:200], flush=True)
                break
    print(f"ok {ok}, errors {err}, not started {len(queue)}, {time.time() - start:.0f} s", flush=True)


if __name__ == "__main__":
    main()
