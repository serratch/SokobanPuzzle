# Sokoban Solver

Modeling and solving the Sokoban puzzle with search algorithms (BFS), with deadlock detection and a Pygame interface
Sokoban is a puzzle where a warehouse keeper pushes boxes onto target squares. The player can only push (never pull), and can only push one box at a time. The goal is to place every box on a target, in any order.

This project:
1. Models the game as a search problem (states, actions, successors, goal test).
2. Solves it with Breadth-First Search (BFS)
3. Detects deadlocks (corner and line).
4. Replays the solution in a Pygame interface.

| Symbol Meaning |
| `R` | Player |
| `O` | Wall |
| ` ` (space) | Empty floor |
| `S` | Target |
| `B` | Box |
| `.` | Player on a target |
| `*` | Box on a target |

