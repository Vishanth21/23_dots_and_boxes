# Lab 4: VibeCoding — Chat History

**Student:** se-lab-pes1ug24am323
**Scenario:** 23 — Dots and Boxes
**Tool used:** OpenCode (model `v4.1flash`)
**Date:** 6 October 2026


---

## Task index

| Task | Commit | Summary |
|------|--------|---------|
| Task 1 — Fix the broken code | `a4fa85f` | Fixed the crash on non-ASCII digit input (`H 0 ²`) |
| Task 2 — Add a feature | `e959242` | Box ownership (`1`/`2` markers) + configurable board size |
| Task 3 — Validation & robustness | `e428902` | Clean exit on Ctrl-D/Ctrl-C/`Q`; `add_line` guards; `.gitignore` |
| Task 4 — Testing & quality | `37d0685` | 11 pytest cases + `conftest.py` import fix |
| Final submission | `97887d2` | Handout PDF + before/after demo videos |

---

## Task 1 — Reproduce and investigate the bug

**Prompt:**

> game crashes went entering ascii numeral, and also when ctrl+c instead of handling it gracefully, refer 
> @Lab_4_VibeCoding_Student_handout.pdf

The handout text was extracted with `pdftotext`. It does not name a specific bug — it says
"fix the broken code." The README's Task 1 points at "score and turn behaviour after box completion."

The code was then exercised directly. Single-box completion scores +1 and keeps the turn; a move
completing two boxes scores +2 and keeps the turn; final-line completion credits the right player;
`is_complete()` math, bounds checks, and repeated-move rejection all behave correctly. Git history
was checked too: the only commit after "Initial commit" changed the README title, not code.

Conclusion: the starter's score/turn logic is correct. The reproducible defects are in input
handling and board robustness. The assistant recommended the `²` crash as the Task 1 bug and
drafted a reproduction sequence.

**Prompt:**

> go with int bug

The `²` crash is caused by `str.isdigit()` returning `True` for non-ASCII digits such as `²`
(U+00B2) and `①` (U+2460), while `int()` raises `ValueError` for them. The `.isdigit()` check
passes and the crash happens one line later at `int(row), int(col)`.

### Fix applied

`game.py` gained an `_is_ascii_digits()` helper and the two `.isdigit()` checks were replaced with it:

```python
def _is_ascii_digits(text):
    """True only for non-empty strings of ASCII digits 0-9.

    str.isdigit() also accepts non-ASCII digits such as '\u00b2' and '\u2460',
    which then raise ValueError in int(). Restricting to ASCII avoids the crash.
    """
    return bool(text) and all("0" <= ch <= "9" for ch in text)
```

### Verified outcome

- `H 0 ²` → `"Row and column must be numbers."` — no crash, loop continues.
- Valid moves still accepted, turns still alternate correctly.

Committed as `a4fa85f` — *Task 1: fix crash on non-ASCII digit input*.

---

## Task 2 — Add a meaningful feature

**Prompt:**

> now lets add a proper feature, right now the game is too plain and just shows an X for a box. i want
> something that actually uses the game state and works with the scores, and it has to touch more than
> one module. what can we do?

The assistant proposed several candidate features and recommended **box ownership + configurable
board size**, because it changes actual gameplay feedback, interacts with the turn/score system,
forces `rules.completed_boxes()` to change its contract (return *which* boxes, not a count), and
spans more than one module, as the README requires.

**Prompt:**

> use 1 and 2 for the two players so we can see who owns the box, take the board size from the command
> line arguments instead of a prompt, and dont bother with the dots on the display for now

Markers `1`/`2`; board size via `sys.argv`; no display-dot fix.

### Implementation

- **`rules.py`** — `completed_boxes()` now returns the **set of newly completed cells** instead of a
  count. Scoring still uses `len(...)`, so behaviour is preserved.
- **`board.py`** — added `self.owner = {}` and `claim(cells, player)`; `display()` renders the owner
  marker (`1` or `2`) instead of a bare `X`.
- **`game.py`** — `DotsAndBoxes(rows, cols)`; on completion it claims the boxes for the current player
  and scores `len(newly_completed)`.
- **`main.py`** — reads `sys.argv[1]`/`[2]`, defaulting to 2×2 so existing behaviour is unchanged.

### Verified outcome

- Double-box move renders `| 1 | 1 |` with `P1=2`, turn retained.
- 3×3 board dimensions correct (`4×3` horizontal, `3×4` vertical), runs without index errors.
- Scores still sum to the total box count.

Committed as `e959242` — *Task 2: track box ownership and allow configurable board size*.

---

## Task 3 — Validation and robustness

**Prompt:**

> it still crashes if i give it weird input or press ctrl+d, and the board functions themselves dont
> check anything so a bad call can corrupt the state. make it handle malformed commands, bad
> coordinates, repeated lines and ctrl+c/d cleanly. also add a gitignore for the pycache

The following gaps were identified in the existing code:

1. `EOFError` on Ctrl-D / piped-input exhaustion — printed a traceback.
2. No `KeyboardInterrupt` (Ctrl-C) handling — traceback.
3. No quit command — `Q` produced "Invalid format."
4. `Board.add_line` unguarded — any orientation ≠ `"H"` wrote to `vertical`; bad index → `IndexError`.
5. `__pycache__/` untracked — should be gitignored.

`valid_move()` already correctly rejected out-of-range coords, repeated lines, and bad orientations,
so the work was items 1–4 plus a `.gitignore`.

**Prompt:**

> raise a valueerror from add_line instead of returning false, handle ctrl+c and ctrl+d gracefully, and
> yes include the gitignore in this commit

### Implementation

- **`game.py`** — new `_read_move()` catches `EOFError` (Ctrl-D) and `KeyboardInterrupt` (Ctrl-C),
  returning `None` so `run()` exits with `"Game ended by user."`; added `Q`/`QUIT` handling.
- **`board.py`** — `add_line()` raises `ValueError` for unknown orientation, out-of-range indices, and
  repeated lines, instead of silently corrupting state or raising `IndexError`.
- **`.gitignore`** — ignores `__pycache__/` and `*.pyc`.

### Verified outcome

```
Q/QUIT                -> "Game ended by user." (clean, no traceback)
Ctrl-D (EOF)          -> "Game ended by user."
Ctrl-C                -> handled by the same except clause
add_line('Z', 0, 0)   -> ValueError: Unknown orientation: 'Z'
add_line('V', 9, 9)   -> ValueError: Vertical line out of range
add_line('H', 9, 9)   -> ValueError: Horizontal line out of range
repeat move           -> ValueError: Horizontal line already drawn
```

A full 2×2 game still ends correctly (`| 1 | 1 |` / `| 2 | 2 |`, "The game is a draw."), with scores
summing to 4 — no regressions.

Committed as `e428902` — *Task 3: harden input and board-state handling*.

---

## Task 4 — Testing and quality

**Prompt:**

> now add tests for the main game rules. use pytest since its easier, and update the agent.md while
> youre at it because it still says the project has no dependencies

**Prompt:**

> put the tests in a tests folder, update the requirements.txt and fix the no dependency line in
> agent.md, and leave the readme alone

Tests go in `tests/`; pytest added to `requirements.txt` **and** the stale "no third-party packages"
claim in `AGENTS.md` corrected; README left untouched.

### Implementation

`tests/test_game.py` — 11 pytest cases covering the five behaviours the README requires, plus
regressions for Tasks 1 and 2:

| Test | Asserts |
|------|---------|
| `test_valid_horizontal_move` | `valid_move(..., "H", 0, 0)` is `True`; line set after `add_line` |
| `test_valid_vertical_move` | same for `"V"` |
| `test_invalid_move_rejected` | out-of-bounds and bad orientation rejected |
| `test_repeated_move_rejected` | a drawn line is no longer valid |
| `test_add_line_guards_board_state` | `add_line` raises `ValueError` on bad/repeat input |
| `test_box_completion` | closing a box adds it to `completed`; `claim` records owner |
| `test_two_boxes_completed_by_one_move` | one move can claim two boxes |
| `test_end_of_game_direct_state` | filling all lines makes `is_complete()` `True` |
| `test_full_game_via_scripted_input` | a scripted game ends with all boxes owned, `"Game over!"` |
| `test_ascii_digit_guard_rejects_non_ascii` | Task 1 regression: `²`, `①`, `٢` rejected |
| `test_board_size_is_configurable` | Task 2 regression: `Board(3, 4)` dimensions |

### Import failure and fix

Running plain `pytest` produced:

```
ModuleNotFoundError: No module named 'board'
```

Because pytest inserted `tests/` onto `sys.path`, not the repo root. Fixed with `tests/conftest.py`,
which prepends the repo root to `sys.path` before collection. Plain `pytest` then passed:

```
11 passed in 0.03s
```

Committed as `37d0685` — *Task 4: add pytest suite and document test setup* (the `conftest.py` fix was
squashed into this commit so each task is a single commit).

---

## Final submission

**Prompt:**

> add before.mp4, after.mp4 and also the student handout(update the agent.md) then commit

Updated `AGENTS.md` with a `## Submission artifacts` section, then committed the handout PDF, both
demo videos, and the updated `AGENTS.md` in a single commit:

`97887d2` — *Final submission: handout and before/after demo videos*

---

## Appendix A — Demo video sequences

`before.mp4` (bug present) and `after.mp4` (fixed) use the same sequence:

```
H 0 0
H 1 0
V 0 0
H 0 1
H 1 1
V 0 2
V 0 1     <- P1 completes TWO boxes at once
H 0 ²     <- before: crash.  after: "Row and column must be numbers."
Q         <- after only: clean exit
```

- Move 7 proves the turn/score logic is correct (P1 scores 2, plays again) **and** shows the Task 2
  ownership markers (`| 1 | 1 |`).
- Move 8 shows the Task 1 bug and its fix.
- The trailing `Q` shows the Task 3 clean-exit command.

---

## Appendix B — Final commit history

```
97887d2 Final submission: handout and before/after demo videos
37d0685 Task 4: add pytest suite and document test setup
e428902 Task 3: harden input and board-state handling
e959242 Task 2: track box ownership and allow configurable board size
a4fa85f Task 1: fix crash on non-ASCII digit input
a0ad1a1 Updated scenario title   (starter)
97d5e78 Initial commit
```

