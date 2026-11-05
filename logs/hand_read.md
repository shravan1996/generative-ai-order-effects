# Hand checks

Two things in the article rest on reading replies rather than on a script. Both are written down
here so they can be checked.

## Exact twins: did the reply say nothing separated the options?

`analyze.py` looks for phrases in the 144 replies on the six exact twins (the same block under two
names). Two replies didn't match the phrase list, both from Opus:

- `project-t1`: "On these details, neither project is better"
- `vendor-t2`: "On these quotes, neither is better."

Both say it in other words, so all 144 of 144 said nothing separated the options. The phrase list is
a hint, and the count in the article is this hand-corrected one. The one reply that didn't name the
first-listed option (Haiku on `hire-t2`, listing James Fenn first and naming Mark Hale) also opens by
saying neither candidate is clearly better.

## Close calls: did the reply sound close?

24 close-call replies from the main run, drawn with `random.Random(20261106).sample(rows, 24)` over
the 480 plain close-item replies in file order. Reading each one in full:

- All 24 open by naming or recommending an option.
- One says it's a close call in its opening line (Haiku on `project-1`).
- 14 of the 19 about hires, suppliers and projects name a condition under which the other option
  would win, or would become the fallback. Reply numbers in sample order: 0, 2, 4, 8, 9, 10, 11, 13,
  16, 18, 19, 20, 22, 23. This is a judgement call on a couple of them (9, 22).
- None of the 5 about drafts does. They suggest edits to the chosen draft instead.
