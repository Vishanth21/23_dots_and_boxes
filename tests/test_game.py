"""Tests for the Dots and Boxes game.

Run from the repo root with:

    pytest -v

Single test:

    pytest tests/test_game.py::test_valid_horizontal_move -v
"""

import pytest

from board import Board
from game import DotsAndBoxes, _is_ascii_digits
from rules import completed_boxes, valid_move


# --- valid moves -----------------------------------------------------------


def test_valid_horizontal_move():
    board = Board()
    assert valid_move(board, "H", 0, 0) is True
    board.add_line("H", 0, 0)
    assert board.horizontal[0][0] is True


def test_valid_vertical_move():
    board = Board()
    assert valid_move(board, "V", 0, 0) is True
    board.add_line("V", 0, 0)
    assert board.vertical[0][0] is True


# --- invalid / repeated moves ----------------------------------------------


def test_invalid_move_rejected():
    board = Board()
    assert valid_move(board, "H", -1, 0) is False
    assert valid_move(board, "H", 3, 0) is False
    assert valid_move(board, "H", 0, -1) is False
    assert valid_move(board, "H", 0, 2) is False
    assert valid_move(board, "V", -1, 0) is False
    assert valid_move(board, "V", 2, 0) is False
    assert valid_move(board, "V", 0, 3) is False
    assert valid_move(board, "X", 0, 0) is False
    assert valid_move(board, "", 0, 0) is False


def test_repeated_move_rejected():
    board = Board()
    board.add_line("H", 0, 0)
    assert valid_move(board, "H", 0, 0) is False


def test_add_line_guards_board_state():
    board = Board()
    with pytest.raises(ValueError):
        board.add_line("Z", 0, 0)
    with pytest.raises(ValueError):
        board.add_line("V", 9, 9)
    with pytest.raises(ValueError):
        board.add_line("H", 9, 9)

    board.add_line("H", 0, 0)
    with pytest.raises(ValueError):
        board.add_line("H", 0, 0)


# --- box completion --------------------------------------------------------


def test_box_completion():
    board = Board()
    before = set(board.completed)

    board.add_line("H", 0, 0)
    board.add_line("H", 1, 0)
    board.add_line("V", 0, 0)
    assert completed_boxes(board, before) == set()

    board.add_line("V", 0, 1)
    newly = completed_boxes(board, before)
    assert newly == {(0, 0)}
    assert (0, 0) in board.completed

    board.claim(newly, 1)
    assert board.owner[(0, 0)] == 1


def test_two_boxes_completed_by_one_move():
    board = Board()
    before = set(board.completed)

    for move in [("H", 0, 0), ("H", 1, 0), ("H", 0, 1), ("H", 1, 1),
                 ("V", 0, 0), ("V", 0, 2)]:
        board.add_line(*move)
    assert completed_boxes(board, before) == set()

    board.add_line("V", 0, 1)
    newly = completed_boxes(board, before)
    assert newly == {(0, 0), (0, 1)}

    board.claim(newly, 1)
    assert board.owner[(0, 0)] == 1
    assert board.owner[(0, 1)] == 1


# --- end of game -----------------------------------------------------------


def test_end_of_game_direct_state():
    board = Board()
    for r in range(board.rows + 1):
        for c in range(board.cols):
            board.add_line("H", r, c)
    for r in range(board.rows):
        for c in range(board.cols + 1):
            board.add_line("V", r, c)

    assert board.is_complete() is True
    assert len(board.completed) == board.rows * board.cols


def test_full_game_via_scripted_input(monkeypatch, capsys):
    moves = iter([
        "H 0 0", "H 1 0", "H 2 0", "V 0 0", "V 0 2", "V 1 0", "V 1 1",
        "V 0 1", "H 0 1", "H 1 1", "V 1 2", "H 2 1",
    ])

    def fake_input(_prompt=""):
        try:
            return next(moves)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)

    game = DotsAndBoxes()
    game.run()

    assert game.board.is_complete() is True
    assert sum(game.scores) == 4
    assert all(cell in game.board.owner for cell in game.board.completed)
    assert "Game over!" in capsys.readouterr().out


# --- regressions -----------------------------------------------------------


def test_ascii_digit_guard_rejects_non_ascii():
    assert _is_ascii_digits("2") is True
    assert _is_ascii_digits("12") is True
    assert _is_ascii_digits("\u00b2") is False
    assert _is_ascii_digits("\u2460") is False
    assert _is_ascii_digits("\u0662") is False
    assert _is_ascii_digits("") is False
    assert _is_ascii_digits("1a") is False


def test_board_size_is_configurable():
    board = Board(3, 4)
    assert len(board.horizontal) == 4
    assert len(board.vertical) == 3
    assert len(board.vertical[0]) == 5
    assert board.is_complete() is False