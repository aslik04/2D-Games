import random
from enum import IntEnum, Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass

ROWS = 6
COLS = 7

type Board = list[list[int]]

class Symbol(IntEnum):
    RED = 0 
    YELLOW = 1

    def opponent(self) -> "Symbol":
        return Symbol(1 - self.value)

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

@dataclass(frozen=True)
class Move:
    col: int 

@dataclass(frozen=True)
class State:
    board: Board
    player_to_move: Symbol

    def get_valid_moves(self) -> list[Move]:
        """List of valid moves a player can make"""
        return [
            Move(col)
            for col in range(COLS)
            if len(self.board[col]) < ROWS
        ]
    
    def can_move_win(self, col: int, symbol: Symbol) -> bool:
        """Can placing a coin in col win the game"""
        dirs = [
            [(1, 0), (-1, 0)],  # horizontal
            [(0, -1)],          # vertical(down-only)
            [(1, 1), (-1, -1)], # diagonal /
            [(1, -1), (-1, 1)], # diagonal \
        ]
        row = len(self.board[col])

        for direction_group in dirs:
            count = 1

            for dx, dy in direction_group:
                x = col + dx
                y = row + dy

                while 0 <= x < COLS and 0<= y < ROWS and self.board[x][y] == symbol.value:
                    count += 1
                    x += dx 
                    y += dy 

            if count >= 4:
                return True
            
    def can_move_lose(self, col: int) -> bool:
        """Does placing a coin in this column lead to a losing move"""
        new_state = self.apply_move(col)

        return any(
            new_state.can_move_win(move.col)
            for move in new_state.get_valid_moves()
        )

    def apply_move(self, col: int) -> State:
        """Apply the move to a new state"""
        new_board = [c.copy() for c in self.board]

        # Drop coin into column
        new_board[col].append(self.player_to_move.value)

        return State(
            board=new_board,
            player_to_move=self.player_to_move.opponent()
        )

class Player(ABC):
    """Abstract Player Class"""

    def __init__(self, symbol: Symbol) -> None:
        self.symbol = symbol

    @abstractmethod
    def get_move(self, state: State) -> Move:
        """Get a move for the player from current state of game"""
        pass

class Human(Player):
    """Human player"""

    def __init__(self, symbol: Symbol) -> None:
        super().__init__(symbol)

    def get_move(self, state: State) -> Move:
        """Get move for human player"""
        valid_moves = state.get_valid_moves()

        while True:
            try:
                col = int(input("Choose a column to drop your coin: "))
                move = Move(col)

                if move in valid_moves:
                    return move
                
                print(f"Please enter an integer between (0-{COLS})!")
            except ValueError:
                print("Please enter an integer only!")

class Bot(Player):
    """Bot player"""

    def __init__(self, symbol: Symbol, difficulty: Difficulty) -> None:
        super().__init__(symbol)
        self.opponent = symbol.opponent()
        self.difficulty = difficulty

    def get_move(self, state: State) -> Move:
        """Get move for bot player"""
        valid_moves = state.get_valid_moves()

        if self.difficulty == Difficulty.EASY:
            return random.choice(valid_moves)
        
        if self.difficulty == Difficulty.MEDIUM:
            return 
        
    def _medium_bot_strategy(self, state: State, valid_moves: list[Move]) -> Move:
        """Bot strategy for medium difficulty"""
        winning_moves = [
            move
            for move in valid_moves
            if state.can_move_win(move.col, self.symbol)
        ]
        if winning_moves:
            return random.choice(winning_moves)
        
        blocking_moves = [
            move
            for move in valid_moves 
            if state.can_move_win(move.col, self.opponent)
        ]
        if blocking_moves:
            return random.choice(blocking_moves)
        
        if Move(COLS // 2) in valid_moves:
            return Move(COLS // 2)
        
        non_losing_moves = [
            move 
            for move in valid_moves
            if not state.can_move_lose(move.col)
        ]
        if non_losing_moves:
            return random.choice(non_losing_moves)
        
        return random.choice(valid_moves)
    
class Game:
    """Main game logic of connect four"""

    def __init__(self, player_red: Player, player_yellow: Player, player_to_move: Symbol) -> None:
        self.state = State(
            board=[[] for _ in range(COLS)],
            player_to_move=player_to_move
        )
        self.players = {
            Symbol.RED: player_red,
            Symbol.YELLOW: player_yellow
        }
        self.game_over = False
        self.winner = None
        self.moves = 0

    def play(self) -> None:
        """Initiate game play"""

        while not self.game_over:
            print(f"\nPlayer {["Red", "Yellow"][self.state.player_to_move.value]}'s turn to move")
            self.display_board()
            self.players[self.state.player_to_move]

    def display_board(self) -> None:
        pass