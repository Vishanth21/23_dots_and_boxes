# AGENTS.md

Dots and Boxes (SE lab, Scenario 23). Python 3.10+. The game itself has no third-party runtime dependencies; pytest is a test-only dependency. No build/lint/typecheck config.

## Run

```text
python main.py
python main.py 3 3   # optional rows/cols, default 2x2
```

The game needs no install step. Moves are `H row col` or `V row col`, 0-indexed. `Q`/`QUIT` exits; Ctrl-D and Ctrl-C exit cleanly.

## Tests

```text
pip install -r requirements.txt
pytest -v
pytest tests/test_game.py::test_box_completion -v   # single test
```

## Layout and entrypoints

- `main.py` — 4-line launcher only; do not put logic here (README constraint).
- `game.py` — `DotsAndBoxes` owns the turn loop, scores, and win/draw output. This is the real entrypoint (`DotsAndBoxes().run()`).
- `board.py` — `Board` holds line state (`horizontal`, `vertical`, `completed`) and renders via `display()`. `add_line()` calls `_update_completed()`.
- `rules.py` — `valid_move(board, orientation, row, col)` bounds/repeat checks and `completed_boxes(board, before)` diff.

## Important

- The starter's score/turn logic is actually correct (verified). The real reproducible bug was the int-parsing crash on non-ASCII digits (`H 0 ²`), fixed in Task 1. Do not "fix" the turn logic — it already follows the rules.
- New features must span more than one module, not pile into `main.py`.
- `Board._update_completed()` only ever adds to `completed` (a set). Scoring relies on `completed_boxes()` diffing against a pre-move snapshot — keep that contract if you refactor. It now returns the set of new cells (not a count), so callers use `len(...)`.
- `Board.owner` maps `(r, c) -> 1|2`; `claim(cells, player)` records ownership. `display()` renders the owner marker.
- `Board.add_line()` raises `ValueError` on bad orientation / out-of-range / repeated lines — a defensive guard, since `game.py` validates via `valid_move()` first.
- `board.is_complete()` compares used lines against total lines; a full board ends the loop and any post-completion moves must not corrupt state.
- Tests live in `tests/test_game.py` (pytest, 11 cases). Run with `pytest -v` from the repo root.
- Untracked file `Lab_4_VibeCoding_Student_handout.pdf` is the assignment handout, not source.