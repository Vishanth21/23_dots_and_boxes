import sys

from game import DotsAndBoxes

if __name__ == "__main__":
    rows = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    cols = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    DotsAndBoxes(rows, cols).run()
