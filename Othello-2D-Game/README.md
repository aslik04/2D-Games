# Othello-2D-Game

A terminal-based implementation of **Othello (Reversi)** built in Python.

---

## Features

- 8×8 Othello board with standard starting position
- Human vs Human
- Human vs Bot
- Three difficulty levels:
  - **Easy** – random valid moves
  - **Medium** – heuristic-based strategy (corners, edges, safe moves)
  - **Hard (planned)** – Minimax with alpha-beta pruning *(not yet implemented)*

---

## Rules Summary

- Players take turns placing a piece on the board
- A move is valid if it **flips at least one opponent piece**
- Flipping occurs when opponent pieces are sandwiched between the placed piece and another piece of the same color
- If a player has **no valid moves**, they must **pass**
- The game ends when **both players have no valid moves**
- The winner is the player with the most pieces on the board

---

## Controls

- Enter row and column indices when prompted
- Board coordinates are zero-indexed (`0–7`)
- Symbols:
  - `B` — Black
  - `W` — White
  - `.` — Empty

---

## Implementation Notes

- Board state is stored as a 2D list
- Valid move detection is based on directional scanning
- Candidate move pruning is used to reduce unnecessary checks
- Piece flipping is computed per move and applied atomically
- Passing turns is fully supported when no valid moves exist

---

## Difficulty Levels

### Easy
- Chooses a random valid move

### Medium
- Prefers corners
- Avoids moves that give the opponent corners
- Prefers edges when available
- Minimizes opponent mobility

### Hard *(Planned)*
- Minimax with alpha-beta pruning
- Depth-limited search
- Heuristic board evaluation
- Candidate move pruning

> ⚠️ Minimax is **not implemented yet**.  
> Hard difficulty will be added in a future iteration.

---

## Goals of This Project

- Practice **idiomatic Python**
- Design clean game abstractions
- Handle complex move validation correctly
- Prepare for **interview-style 2D game problems** (e.g. Jane Street, HRT)

---

## Future Improvements

- Implement Minimax + alpha-beta pruning
- Add heuristic evaluation function
- Improve move ordering
- Add automated tests
- Optional GUI version

---

## Running the Game

```bash
python game.py