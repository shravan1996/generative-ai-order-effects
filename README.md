# generative-ai-order-effects

When you paste options into a chatbot and ask which one to go with, does the order you pasted them
in change the answer? This trial asks Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 to choose between
hires, suppliers, projects and email drafts, in both orders, several times over.

It is the trial behind the Generative AI article on shravanpendem.com, "Only because she's listed
first".

**What this is not.** It doesn't test ChatGPT, Gemini or any non-Claude model. The options are short
and hand-written, four lines or so each, not two-page CVs or full tender documents. Close calls have
no right answer by design, so nothing here says whether a pick was good. And Claude was called
through the Claude Code command-line tool with a one-line system prompt that asks for a closing
`Pick:` line, not through the Claude app.

## Results

Run on 6 November 2026: 2,036 fresh chats. A **flip** is two replies choosing different options.

The order effect is the extra flipping you get from swapping the order, over and above asking the
same thing twice, on 20 close calls with 4 replies per order:

| | Asked again | Swapped | Order effect (95% interval) | Listed first won |
| --- | ---: | ---: | ---: | ---: |
| All three models | 7.2% | 11.5% | 4.2 points (1.2 to 8.3) | 48.3% |
| Haiku 5.5 | 10.4% | 20.0% | 9.6 (1.2 to 21.7) | 40.6% |
| Sonnet 5.5 | 6.2% | 9.4% | 3.1 (0.0 to 8.8) | 53.1% |
| Opus 5.5 | 5.0% | 5.0% | 0.0 (0.0 to 0.0) | 51.2% |

By kind of decision, order effect in points:

| | Haiku | Sonnet | Opus | All |
| --- | ---: | ---: | ---: | ---: |
| Hires | 0.0 | 0.0 | 0.0 | 0.0 |
| Projects | 0.0 | 0.0 | 0.0 | 0.0 |
| Suppliers | 5.0 | 10.0 | 0.0 | 5.0 |
| Drafts | 33.3 | 2.5 | 0.0 | 11.9 |

What the pre-registered questions came to (`PREREGISTRATION.md`):

1. **H1, order moves close calls: a small effect.** 4.2 points sits between "matters" (10 or more)
   and "nearly immune" (3 or less). 52 of 60 model-and-decision cells were stable, 4 mixed, 2 followed
   the first slot and 2 followed the second.
2. **H2, order doesn't push a clearly worse option: held.** 0 of 192.
3. **H3, twins get called twins.** On the six exact twins, all 144 replies said nothing separated the
   options (phrase list plus a hand check in `logs/hand_read.md`), and 143 named whichever was listed
   first. The system prompt forces a name, which is my doing. The two draft twins differ by a word,
   and the models preferred the same word whichever slot it was in: first slot 24 of 48.
4. **H4, a closing line helps: failed for both.** Order effect 2.7 points with "too close" allowed and
   3.3 with "score each one out of 10", against 3.3 for the plain question on the same number of
   replies. "Too close" was used in 11 of 240 replies on close calls (Sonnet 9, Haiku 2, Opus 0; none
   of the 60 on drafts) and 0 of 96 on clear ones.
5. **H5, thinking harder helps: failed by the rule, with no room to pass.** Sonnet's order effect was
   3.9 points at low effort, 3.3 at default and -0.6 at xhigh. The rule asked for 10 points below low.
   Swap flips did fall, from 13.9% to 10.0% to 4.4%. Thinking tokens per call were 114, 265 and 632,
   and cost per call $0.0107, $0.0120 and $0.0158 as the CLI reports it.
6. **H6, shortlists favour the top: failed.** The first of five slots got 24.4% of picks (20.0 to
   30.0), with 18.9, 17.8, 19.4 and 19.4 for the rest. Several of my "nearly equal" shortlists weren't:
   Rachel Dunn won 30 of 30 from all five positions, and Line 3 automation did too.

Exploratory, added after the results (deviations 2 and 3):

| What changed between two replies, on close calls | Chose differently (95% interval) |
| --- | ---: |
| Nothing: the same words again | 7.2% (3.3 to 11.8) |
| Adding "score each one out of 10" | 9.0% (4.8 to 14.0) |
| Swapping the order | 11.5% (5.8 to 17.9) |
| Adding "say if it's too close" | 12.1% (6.7 to 18.1) |
| A different Claude model | 19.8% (10.2 to 30.3) |

- On drafts those three headline rows were 13.9% (again), 25.8% (swapped) and 39.6% (other model).
- Haiku chose the draft it read last in 30 of 40 replies. With names that stayed with the text
  ("Draft Maple", "Draft Rowan") it did the same, 30 of 40, so the position looks like the cause
  rather than the "Draft 2" label. Sonnet didn't: 22 of 40 and 19 of 40 for the first slot.
- None of the 480 plain replies to close calls mentioned the order. 52 of them mentioned today's date,
  which I never gave them: the command-line tool supplies it. 17 of the 24 on the payroll quote did.

The whole run cost $23.03 at list price as the CLI reports it, and took about 35 minutes with 16
parallel calls. The CLI adds its own overhead to every call, so a direct API pipeline would cost less.

## Run it

The tests and the analysis need no key and no network.

```bash
git clone https://github.com/shravan1996/generative-ai-order-effects
cd generative-ai-order-effects
python3 -m unittest discover -s tests -t .
python3 analyze.py
```

To collect fresh replies you need the Claude Code CLI (`claude`), signed in. Collection is resumable:
rerun the same command and it skips calls that already have a reply. Point `ORDER_CALLS` at another
file to keep a test run apart from the published replies.

```bash
python3 prepare.py                                  # rewrite data/items.json
python3 choose.py --models claude-sonnet-5-5 --arm plain --tiers close twin clear --reps 4
python3 choose.py --models claude-sonnet-5-5 --arm plain --tiers five --reps 2
python3 choose.py --models claude-sonnet-5-5 --arm tie_ok --tiers close clear --reps 2
python3 choose.py --models claude-sonnet-5-5 --arm score_first --tiers close clear --reps 2
python3 choose.py --models claude-sonnet-5-5 --arm plain --tiers close --reps 3 --effort xhigh
python3 choose.py --models claude-sonnet-5-5 --arm neutral_labels --tiers close \
    --only draft-1 draft-2 draft-3 draft-4 draft-5 --reps 4
python3 analyze.py
python3 make_figures.py figures/
```

## Files

| Path | What it holds |
| --- | --- |
| `PREREGISTRATION.md` | The questions, thresholds and expectations, committed before the main run, and the three deviations |
| `prepare.py` | The 42 hand-written decisions |
| `choose.py` | Builds each prompt, calls Claude, and reads the pick |
| `analyze.py` | Scores every reply and writes `results/summary.json` |
| `make_figures.py` | The article's three figures |
| `data/items.json` | The decisions as the models saw them |
| `results/calls.jsonl` | Every call: the prompt, the full reply, tokens, cost and the pick |
| `logs/smoke.jsonl` | The 36-call smoke test, not used in any result |
| `logs/hand_read.md` | The two counts that rest on reading replies |

## How Claude was called

`claude -p --tools "" --strict-mcp-config --setting-sources "" --no-session-persistence
--output-format json --system-prompt "<one line asking for a closing 'Pick:' line>" --model <id>`,
from a scratch working directory outside this repository, with `--effort` added on the effort runs.
Every call is a fresh chat. The CLI can't set temperature, so every reply is sampled, and the models
think adaptively before answering. It also tells the model today's date, which I didn't plan for.

## Licence

MIT. See `LICENSE`.
