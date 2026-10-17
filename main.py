from boards import BOARDS
from sokoban_puzzle import SokobanPuzzle

puzzle = SokobanPuzzle(BOARDS[1])

results = puzzle.successors()

for move, state in results:
    print("Move:", move)
    for row in state.board:
        print(row)
    print()