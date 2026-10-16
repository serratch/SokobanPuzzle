
from boards import BOARDS
from sokoban_puzzle import SokobanPuzzle

puzzle = SokobanPuzzle(BOARDS[1])

print("Rows:", puzzle.rows)
print("Columns:", puzzle.cols)
print("Robot:", puzzle.robot_position)
