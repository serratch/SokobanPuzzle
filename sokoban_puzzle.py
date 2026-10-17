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

        self.targets = set()
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell in ('S', '*', '.'):
                    self.targets.add((i, j))

        self.robot_position = None
        for i, row in enumerate(self.board):
            for j, col in enumerate(row):
                if self.board[i][j] == '.':
                    self.robot_position = (i,j)
                elif self.board[i][j] == 'R':
                    self.robot_position = (i,j)

        if self.robot_position is None:
            raise Exception('No robot position found')

    def is_goal(self):
        for row in self.board:
            for cell in row:
                if cell == 'B':
                    return False
        return True

    def successors(self):
        successors = []
        i, j = self.robot_position

        for move, (di, dj) in self.moves.items():
            new_i = i + di
            new_j = j + dj

            # Check board boundaries
            if not (0 <= new_i < self.rows and
                    0 <= new_j < self.cols):
                continue

            cell = self.board[new_i][new_j]

            # Cannot move into a wall
            if cell == 'O':
                continue

            new_board = deepcopy(self.board)

            # Handle pushing a box
            if cell in ('B', '*'):
                after_i = new_i + di
                after_j = new_j + dj

                if not (0 <= after_i < self.rows and
                        0 <= after_j < self.cols):
                    continue

                cell2 = self.board[after_i][after_j]

                if cell2 not in (' ', 'S'):
                    continue

                # Move the box
                if (after_i, after_j) in self.targets:
                    new_board[after_i][after_j] = '*'
                else:
                    new_board[after_i][after_j] = 'B'

            # Restore the robot's previous cell
            if (i, j) in self.targets:
                new_board[i][j] = 'S'
            else:
                new_board[i][j] = ' '

            # Move the robot
            if (new_i, new_j) in self.targets:
                new_board[new_i][new_j] = '.'
            else:
                new_board[new_i][new_j] = 'R'

            new_state = SokobanPuzzle(new_board)
            successors.append((move, new_state))

        return successors
