# Pre-registration

Written on 6 November 2026, after a 36-call smoke test (kept in `logs/smoke.jsonl`, not used in
any result, with no item changed because of it) and before the main run. Committed before the
first main-run call.

## The question

When you paste options into a chatbot and ask which one to go with, does the order you pasted them
in change the answer?

Li and colleagues (arXiv 2610.22807, October 2026) report that thinking models are "nearly immune"
to position bias, on multiple-choice questions and multi-document tasks that have a right answer.
Yin and colleagues (arXiv 2506.14092) report strong order effects on close comparisons of CVs and
colours, on older models. Neither tests a current Claude model on a close workplace decision. This
trial tests three: Claude Haiku 5.5, Claude Sonnet 5.5 and Claude Opus 5.5.

## Data

`prepare.py` writes 42 hand-written decisions, in four kinds: a hire, a supplier, a project to
fund, and which of two drafts to send.

- **close** (20, five of each kind): a real trade-off. Each option is better on something, and
  neither dominates. There is no right answer, by design.
- **twin** (8, two of each kind): no real difference. The same facts under two names; for drafts,
  the same sentences with one word changed.
- **clear** (8, two of each kind): one option is better on everything that matters, recorded in
  advance.
- **five** (6): five nearly equal options, for the case of pasting a whole shortlist.

Drafts are labelled by position ("Draft 1", "Draft 2"), the way people paste them, so the label
moves with the slot. Everything else keeps its own name.

## Procedure

Every call is a fresh chat through the Claude Code CLI, with tools off and a one-line system prompt
asking for a closing line `Pick: <name>`. The CLI cannot set temperature, so every reply is sampled,
and the models think adaptively before answering.

The runs, in the order they will be collected:

| Run | Models | Items | Orders | Replies per order | Calls |
| --- | --- | --- | --- | --- | --- |
| Main: plain question | All three | close, twin, clear | 2 | 4 | 864 |
| Shortlist: plain question | All three | five | 5 rotations | 2 | 180 |
| `tie_ok`: "If they're too close to call on what I've given you, say so and write 'Pick: too close'." | All three | close, clear | 2 | 2 | 336 |
| `score_first`: "Before you choose, score each one out of 10 on whatever matters most here, then choose." | All three | close, clear | 2 | 2 | 336 |
| Effort: plain question at `--effort low` and at `--effort xhigh` | Sonnet only | close | 2 | 3 | 240 |

If time runs short, the runs lower in the table are the ones to cut, and any cut is logged below.

The pick is read from the last `Pick:` line. A reply with no readable pick is left out of the rates
and counted; a hand check may only correct a parsing failure, never a judgement.

## Measures

For each model and item:

- **Repeat flip**: the chance that two replies to the *same* order pick different options. This is
  the noise floor: how much the answer moves when nothing changes.
- **Swap flip**: the chance that two replies to *different* orders pick different options.
- **Order effect**: swap flip minus repeat flip, in points.
- **First-slot share**: the share of picks that went to whichever option was listed first.

Each model and close item (a "cell", 60 in all) is also classified, using the main run's 4 + 4
replies:

- **Stable**: at least 3 of 4 replies in each order chose the same option.
- **Follows the order**: at least 3 of 4 replies in each order chose the same *slot*, so the option
  changes with the order.
- **Mixed**: neither.

Intervals are 95% percentile intervals from 10,000 bootstrap resamples of items (seed 7), carrying
all models with each item. Per-model numbers are reported but not tested.

## Hypotheses and thresholds

**H1. Order moves close calls (primary).** On close items, pooled across models, in the main run:

- Order matters if the order effect is 10 points or more and its interval is above zero.
- "Nearly immune" holds for these decisions if the order effect is 3 points or less.
- Anything between is a small effect, reported as such.

**H2. Order doesn't push a clearly worse option.** Holds if the worse option is picked in 2% of
clear-item replies or fewer, pooled, in the main run.

**H3. Twins get called twins.** Reported without a threshold: how often replies on twin items say
that nothing separates the options, measured by a phrase list and a hand check of a sample, and the
first-slot share on those items.

**H4. A closing line helps.** Each of `tie_ok` and `score_first` helps if it cuts the pooled
close-item order effect by at least half compared with the plain question. These runs have fewer
replies, so the plain comparison uses the first two replies per order from the main run, to match.
For `tie_ok`, also report how often replies say "too close" on close items, and whether it wrongly
says so on clear items.

**H5. Thinking harder helps.** On Sonnet and close items, `--effort xhigh` helps if its order effect
is at least 10 points below `--effort low`. Default effort, from the main run, is shown beside them.

**H6. Shortlists favour the top.** On five-option items, pooled, position matters if the first
slot's share of picks is 30% or more, against 20% by chance. Report the share for every slot.

**Reported without a threshold:** the two-chat swap test as a detector (how often one reply in each
order disagree, by tier and by cell type); how often close-item replies flag that the decision is
close; every number by model and by kind of decision.

## What I expect

Written down so the article can say where I was wrong. Given the "nearly immune" result, and one
flip in the 15 close-item pairs of the smoke test, I expect a small effect: an order effect of about
15 points on Haiku, 10 on Sonnet and 5 on Opus, favouring the first slot. No clear item goes wrong.
Twins are always called twins, and the tie goes to the first slot. `tie_ok` helps a lot because it
gives permission not to choose, and `score_first` helps little. `xhigh` helps a little. On
shortlists, I expect the first slot to do somewhat better than 20%, but below 30%.

## What would change the article's advice

- If H1 finds order matters, the article recommends asking in both orders before relying on a pick
  between close options. Verdict: Use (the swap), or Split if it only helps some kinds of decision.
- If H1 finds "nearly immune" holds, the article says order isn't worth worrying about on these
  models. Verdict: Skip.
- If H2 fails, the article says so first, and treats it as more serious than anything in H1.
- If `tie_ok` meets H4 without wrongly saying "too close" on clear items, the article recommends
  that sentence over the swap, because it costs nothing.

## Deviations

Any change after the first main-run call is listed here with its reason.

1. **Short names (found after the main run, before any other run).** The parser wanted the full
   name of an option, and 14 main-run replies wrote `Pick: Rowan` for "Project Rowan" and the like,
   all on the two project twins. This is a parsing failure of the kind the procedure allows me to
   correct. `read_pick` now also accepts a word that only one option's name contains, with a test,
   and `analyze.py` reads every stored reply again with it. No judgement changed.

2. **Neutral labels on the drafts (added after every registered run, before any of these calls).**
   Drafts are labelled by position, so "Draft 2" is always the draft read last. Haiku favoured the
   second draft on close items, and that could be either the position or the label. `neutral_labels`
   reruns the five close drafts on Haiku and Sonnet, four replies per order, calling them "Draft
   Maple" and "Draft Rowan", names that stay with the text. Exploratory. What I expect, written
   before the first call: the lean towards the last draft mostly survives, because I think it's the
   position and not the label.

3. **Comparisons added after the registered analysis.** Two flip rates in `analyze.py` were not
   registered, and are labelled exploratory wherever they're reported: how often two replies from
   different models differ, and how often a reply with a closing line differs from a plain reply to
   the same order. Replies mentioning the order and today's date are also counted, because reading
   the replies turned both up.
