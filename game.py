from board import Board
from rules import valid_move, completed_boxes


def _is_ascii_digits(text):
    """True only for non-empty strings of ASCII digits 0-9.

    str.isdigit() also accepts non-ASCII digits such as '\u00b2' and '\u2460',
    which then raise ValueError in int(). Restricting to ASCII avoids the crash.
    """
    return bool(text) and all("0" <= ch <= "9" for ch in text)


class DotsAndBoxes:
    def __init__(self, rows=2, cols=2):
        self.board = Board(rows, cols)
        self.current = 0
        self.scores = [0, 0]

    def run(self):
        print("Dots and Boxes")
        print("Enter moves as H row col or V row col.")
        print("Rows and columns start at 0.")
        print("Example: H 0 1")

        while not self.board.is_complete():
            self.board.display(self.scores, self.current)
            raw = input(f"Player {self.current + 1}, move: ").strip().upper()
            parts = raw.split()

            if len(parts) != 3:
                print("Invalid format.")
                continue

            orientation, row, col = parts
            if not _is_ascii_digits(row) or not _is_ascii_digits(col):
                print("Row and column must be numbers.")
                continue

            row, col = int(row), int(col)
            if not valid_move(self.board, orientation, row, col):
                print("Invalid or already-used move.")
                continue

            before = set(self.board.completed)
            self.board.add_line(orientation, row, col)
            newly_completed = completed_boxes(self.board, before)

            if newly_completed:
                self.board.claim(newly_completed, self.current + 1)
                self.scores[self.current] += len(newly_completed)
                print(f"Player {self.current + 1} completed {len(newly_completed)} box(es) and plays again.")
            else:
                self.current = 1 - self.current

        self.board.display(self.scores, self.current)
        print("Game over!")
        if self.scores[0] == self.scores[1]:
            print("The game is a draw.")
        else:
            winner = 1 if self.scores[0] > self.scores[1] else 2
            print(f"Player {winner} wins!")
