from copy import deepcopy

"""Representation used:
  'O' : Obstacle
  'S' : Storage
  'B' : Box
  'R' : Robot (Agent)
  '*' : Box on a Storage Case
  '.' : Robot on a Storage Case"""

class SokobanPuzzle:
    def __init__(self, board):
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0])
        self.moves = {
            "Up": (-1, 0),
            "Down": (1, 0),
            "Left": (0, -1),
            "Right": (0, 1)
        }
        self.robot_position = None
        for i, row in enumerate(self.board):
            for j, col in enumerate(self.board):
                if board[i][j] == '.':
                    self.robot_position = (i,j)
                elif board[i][j] == 'R':
                    self.robot_position = (i,j)

        if self.robot_position is None:
            raise Exception('No robot position found')