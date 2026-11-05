"""Draw the article's three figures as SVG from results/summary.json.

    python3 make_figures.py <output-folder>

Figures are 680 wide, transparent, and use the site's palette, so they sit on the article's figure
plate in light and dark mode.
"""
import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
W = 680
INK, SOFT, FAINT, RULE = "#191F1D", "#3F4945", "#5C6964", "#D3DBD7"
GREEN, MUTED = "#1F6B4C", "#A9B7B1"

STYLE = f"""  <style>
    text {{ stroke: none; }}
    .serif {{ font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif; }}
    .sans  {{ font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
    .h1 {{ font-size: 26px; font-weight: 600; fill: {INK}; }}
    .sub {{ font-size: 14.5px; fill: {SOFT}; }}
    .label {{ font-size: 11px; font-weight: 700; letter-spacing: 1.1px; fill: {FAINT}; }}
    .row {{ font-size: 14.5px; fill: {INK}; }}
    .rowb {{ font-size: 14.5px; font-weight: 600; fill: {INK}; }}
    .cell {{ font-size: 13.5px; fill: {SOFT}; }}
    .val {{ font-size: 14px; font-weight: 700; fill: {INK}; }}
    .num {{ font-size: 14px; fill: {SOFT}; }}
    .axis {{ font-size: 12px; fill: {FAINT}; }}
    .foot {{ font-size: 13.5px; fill: {SOFT}; }}
  </style>"""


def wrap(text, width_px, size=13.5):
    """Greedy word wrap using an average glyph width for the sans face."""
    per_line = max(10, int(width_px / (size * 0.53)))
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > per_line:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    if cur:
        lines.append(cur)
    return lines


class Svg:
    def __init__(self, title, desc):
        self.title, self.desc, self.parts, self.y = title, desc, [], 0

    def text(self, x, y, cls, s, anchor=None):
        a = f' text-anchor="{anchor}"' if anchor else ""
        self.parts.append(f'  <text class="{cls}" x="{x:.1f}" y="{y:.1f}"{a}>{escape(s)}</text>')

    def rule(self, y, x1=32, x2=W - 32, colour=RULE):
        self.parts.append(f'  <line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{colour}" stroke-width="1"/>')

    def vline(self, x, y1, y2, colour=RULE, width=1):
        self.parts.append(f'  <line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="{colour}" stroke-width="{width}"/>')

    def rect(self, x, y, w, h, fill):
        self.parts.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 1.5):.1f}" height="{h}" rx="2" fill="{fill}"/>')

    def head(self, subs):
        self.text(32, 44, "serif h1", self.title)
        y = 72
        for s in subs:
            self.text(32, y, "sans sub", s)
            y += 20
        self.rule(y)
        self.y = y + 28

    def foot(self, s):
        for line in wrap(s, W - 64, 13.5):
            self.text(32, self.y, "sans foot", line)
            self.y += 19

    def save(self, path):
        h = int(self.y + 16)
        body = "\n".join(self.parts)
        path.write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
            f'role="img" aria-labelledby="title desc">\n'
            f'  <title id="title">{escape(self.title)}</title>\n'
            f'  <desc id="desc">{escape(self.desc)}</desc>\n{STYLE}\n{body}\n</svg>\n')


def text_table(title, subs, rows, left_w=200, foot=None):
    """Two-column table: a bold prompt on the left, wrapped detail on the right."""
    svg = Svg(title, " ".join(f"{a}: {b}" for a, b in rows) + (f" {foot}" if foot else ""))
    svg.head(subs)
    x2 = 32 + left_w + 16
    for left, right in rows:
        top = svg.y
        ll = wrap(left, left_w, 14.5)
        rl = wrap(right, W - 32 - x2, 13.5)
        for i, line in enumerate(ll):
            svg.text(32, top + i * 20, "sans rowb", line)
        for i, line in enumerate(rl):
            svg.text(x2, top + i * 19, "sans cell", line)
        svg.y = top + max(len(ll) * 20, len(rl) * 19) + 4
        svg.rule(svg.y)
        svg.y += 26
    if foot:
        svg.foot(foot)
    return svg


def reading_rule():
    rows = [
        ("Matched CVs, May 2025 (Rozado)",
         "22 models chose between two CVs for a job. The first-listed candidate got 63.5% of picks, and 21 of the "
         "22 leaned that way. No right answer. Claude 3.5 Sonnet was the Claude in the test."),
        ("Colours and CVs, June 2025 onward (Yin and colleagues)",
         "Options built to be close. Strong order effects that changed with quality: the first option among good "
         "ones, a later one among poor ones. No right answer. The newest Claude was Sonnet 4."),
        ("Agents booking hotels, August 2026 (Wadi and Ma)",
         "7,000 sessions picking from 100 listings. Position mattered less as reasoning effort rose, and Claude "
         "Sonnet 5 at high effort showed no detectable effect. GPT 6 Luna showed one at every level."),
        ("Exam questions, October 2026 (Li and colleagues)",
         "The right answer was forced into one slot of a multiple-choice test. The largest gap was about 4 points "
         "for GPT-5.2 and DeepSeek-V4, against about 21 for the smallest model. Thinking models were \"nearly "
         "immune\". There is an answer key here, and no Claude."),
    ]
    return text_table(
        "Four order studies, four different jobs",
        ["The more recent the models and the clearer the right answer, the smaller", "the effect. Each row tests a different kind of choice."],
        rows, left_w=190,
        foot="None of these asked a current Claude to make a close workplace call, which is the gap my trial tries to fill.")


def what_moved(s):
    w = s["what_moves"]
    bars = [
        ("repeat", "The same words again", MUTED),
        ("score_first", "Adding \"score each one out of 10\"", MUTED),
        ("swap", "Swapping the order", GREEN),
        ("tie_ok", "Adding \"say if it's too close\"", MUTED),
        ("model", "Asking a different Claude model", MUTED),
    ]
    kinds = [("hire", "Hires"), ("project", "Projects"), ("supplier", "Suppliers"), ("draft", "Drafts")]
    desc = "; ".join(f"{label}: {100 * w[k]['flip']:.1f}%, interval {100 * w[k]['ci'][0]:.1f} to {100 * w[k]['ci'][1]:.1f}" for k, label, _ in bars)
    desc += ". By kind of decision, same words, swapped order, different model: " + "; ".join(
        f"{label} {100 * w[k]['repeat']['flip']:.1f}, {100 * w[k]['swap']['flip']:.1f}, {100 * w[k]['model']['flip']:.1f}" for k, label in kinds) + "."
    svg = Svg("Swapping moved it less than switching model", desc)
    svg.head(["How often two replies chose differently, on 20 close calls and three",
              "Claude models. Lines show 95% intervals over the 20 decisions."])

    x0, x1, top = 300, 616, svg.y
    maxv = 35.0
    scale = lambda v: x0 + (x1 - x0) * v / maxv
    svg.text(32, top, "sans label", "WHAT CHANGED BETWEEN THE TWO REPLIES")
    svg.text(x0, top, "sans label", "CHOSE DIFFERENTLY")
    y = top + 16
    for tick in (0, 10, 20, 30):
        svg.vline(scale(tick), y, y + len(bars) * 34 + 2)
    for k, label, colour in bars:
        v = w[k]
        svg.text(32, y + 19, "sans rowb" if k == "swap" else "sans row", label)
        svg.rect(x0, y + 7, scale(100 * v["flip"]) - x0, 16, colour)
        lo, hi = scale(100 * v["ci"][0]), scale(100 * v["ci"][1])
        svg.parts.append(f'  <line x1="{lo:.1f}" y1="{y + 15:.1f}" x2="{hi:.1f}" y2="{y + 15:.1f}" stroke="{INK}" stroke-width="1.5"/>')
        svg.vline(lo, y + 11, y + 19, INK, 1.5)
        svg.vline(hi, y + 11, y + 19, INK, 1.5)
        svg.text(hi + 8, y + 20, "sans val", f"{100 * v['flip']:.1f}%")
        y += 34
    y += 18
    for tick in (0, 10, 20, 30):
        svg.text(scale(tick), y, "sans axis", f"{tick}%", "middle")
    svg.y = y + 18
    svg.rule(svg.y)
    svg.y += 28

    cols = [(420, "SAME WORDS"), (510, "SWAPPED"), (600, "OTHER MODEL")]
    svg.text(32, svg.y, "sans label", "BY KIND OF DECISION")
    for x, name in cols:
        svg.text(x, svg.y, "sans label", name, "middle")
    svg.y += 28
    for k, label in kinds:
        svg.text(32, svg.y, "sans row", label)
        for (x, _), key in zip(cols, ("repeat", "swap", "model")):
            cls = "sans val" if key == "swap" else "sans num"
            svg.text(x, svg.y, cls, f"{100 * w[k][key]['flip']:.1f}%", "middle")
        svg.y += 26
    svg.y -= 4
    svg.rule(svg.y)
    svg.y += 24
    svg.foot("The swap row was pre-registered. Comparing across models or against a closing line was added after I saw "
             "the results, so read those rows as a description. Asking again is the noise floor.")
    return svg


def working_default():
    rows = [
        ("Quotes, CVs or projects, on Sonnet or Opus",
         "Ask once. Order moved almost nothing here except one payroll quote, and a clearly worse option never won."),
        ("Two pieces of writing",
         "Ask twice, with the order swapped. If the picks differ, call it a draw and decide yourself. Drafts moved "
         "more than anything else I tested."),
        ("A small, fast model",
         "Swap every time, or use a larger model for this one job. Haiku changed which draft it chose half the time "
         "when I swapped them."),
        ("It says nothing separates them",
         "Believe the sentence and ignore the name. The name was the first-listed option in 143 of 144 replies."),
        ("The decision really matters",
         "Ask a second model too, and read where they differ. Disagreement tells you it's a judgement call. It doesn't "
         "tell you who's right."),
        ("The reply sounds sure of itself",
         "Don't take that as a sign the pick is steady. None of the 480 replies to close calls mentioned the order, "
         "including the ones that changed with it."),
    ]
    return text_table(
        "When I'd swap the order, and when I wouldn't",
        ["For choosing between options you've pasted into Claude, as of November 2026."],
        rows, left_w=190,
        foot="All of this comes from short options I wrote myself. Long documents are untested, and they're where I'd "
             "expect order to matter more.")


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "figures")
    out.mkdir(parents=True, exist_ok=True)
    s = json.loads((ROOT / "results" / "summary.json").read_text())
    reading_rule().save(out / "reading-rule.svg")
    what_moved(s).save(out / "prototype-result.svg")
    working_default().save(out / "working-default.svg")
    print("wrote", out)


if __name__ == "__main__":
    main()
