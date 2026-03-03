# Gomoku

A terminal Gomoku game in Python with Human vs Human and Human vs Bot modes.

> Built to practice **idiomatic Python** and clean class design.

## Features
- 3 bot levels:
  - **Easy**: random
  - **Medium**: win/block + center/corners
  - **Hard**: minimax + alpha-beta pruning

## Input
- Enter row and col within board bounds
- Symbols: X, O, . (empty)

## Note
- Level 3 (Hard) is currently not practical to use on larger boards.
- Even with alpha-beta pruning, full minimax search space is too large.
- Will revisit with depth limits, heuristic evaluation, and candidate move pruning.

## Run
```bash
python3 game.py