import random
from enum import Enum, IntEnum
from abc import ABC, abstractmethod

class Symbol(IntEnum):
    X = 0
    O = 1

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

type Board = list[list[int | None]]

class Player(ABC):
    """Abstract base class for players"""

    @abstractmethod
    def get_move(self, board: Board) -> tuple[int, int]:
        """Get next move from player"""
        pass

class Human(Player):
    """Human player"""

    def __init__(self, symbol: Symbol) -> None:
        self.symbol = symbol
    
    def get_move(self, board: Board) -> tuple[int, int]:
        """Get move from user input"""
        while True:
            try:
                row = int(input("Enter row (0-2): "))
                col = int(input("Enter col (0-2): "))

                if 0 <= row <= 2 and 0 <= col <= 2 and board[row][col] is None:
                    return (row, col)

                print("Invalid move. Try again.")
            except ValueError:
                print("Please enter integers only.")

class Bot(Player):
    """Bot player with configurable difficulty"""

    def __init__(self, difficulty: Difficulty, symbol: Symbol = Symbol.O) -> None:
        self.difficulty = difficulty
        self.symbol = symbol
        self.opponent = Symbol(1 - symbol)
        self.minimax = Minimax(bot=symbol) if difficulty == Difficulty.HARD else None

    def get_move(self, board: Board) -> tuple[int, int]:
        """Selects move based on difficulty level"""
        valid_moves = Minimax.valid_moves(board)

        if self.difficulty == Difficulty.EASY:
            return random.choice(valid_moves)

        if self.difficulty == Difficulty.MEDIUM:
            return self._medium_strategy(board, valid_moves)
    
        # Difficulty.HARD
        return self.minimax.best_move(board)
    
    def _medium_strategy(self, board: Board, valid_moves: list[tuple[int, int]]) -> tuple[int, int]:
        """Medium difficulty: win/block or prefer center/corners"""
        # Try to win
        if win_move := self._find_winning_move(board, valid_moves, self.symbol):
            return win_move
        
        # Block opponent
        if block_move := self._find_winning_move(board, valid_moves, self.opponent):
            return block_move

        # Prefer center
        if (1, 1) in valid_moves:
            return (1, 1)

        # Prefer corners
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        valid_corners = [move for move in valid_moves if move in corners]
        if valid_corners:
            return random.choice(valid_corners)
        
        # Fallback: random move
        return random.choice(valid_moves)

    def _find_winning_move(
            self, 
            board: Board, 
            valid_moves: list[tuple[int, int]], 
            symbol: int,
        ) -> tuple[int, int] | None:
        """Find move that wins for symbol, if one exists"""
        for r, c in valid_moves:
            board[r][c] = symbol
            is_win = Minimax.is_winner(board, symbol)
            board[r][c] = None

            if is_win:
                return (r, c)
        
        return None

class Minimax:
    """Minimax algorithm for tic-tac-toe"""
    # Class constants for scoring
    WIN = 1
    DRAW = 0
    LOSS = -1

    def __init__(self, bot: Symbol = Symbol.O) -> None:
        self.bot = bot
        self.human = Symbol(1 - bot)

    @staticmethod
    def valid_moves(board: Board) -> list[tuple[int, int]]:
        """Return list of available positions on board"""
        return [(r, c) for r in range(3) for c in range(3) if board[r][c] is None]

    @staticmethod
    def is_winner(board: Board, player: int) -> bool:
        """Return True if player has 3 cells in a row"""
        return (
            any(all(cell == player for cell in row) for row in board) 
            or any(all(row[c] == player for row in board) for c in range(3)) 
            or all(board[i][i] == player for i in range(3)) 
            or all(board[i][2 - i] == player for i in range(3))
        )
    
    def best_move(self, board: Board) -> tuple[int, int]:
        """Find the best move for the bot using minimax algorithm"""
        best_score = float("-inf")
        best_move = None
        alpha = float("-inf")
        beta = float("inf")

        for r, c in self.valid_moves(board):
            board[r][c] = self.bot
            score = self.minimax(board, self.human, alpha, beta)
            board[r][c] = None

            if score > best_score:
                best_score = score
                best_move = (r, c)
            
            # Alpha-beta pruning
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        
        if best_move is None:
            raise ValueError("best_move called on a full board")
        
        return best_move

    def minimax(self, board: Board, player: int, alpha: float, beta: float) -> int:
        """Minimax algorithm"""
        # Terminal states
        if self.is_winner(board, self.bot):
            return self.WIN
        if self.is_winner(board, self.human):
            return self.LOSS
        
        moves = self.valid_moves(board)
        if not moves:
            return self.DRAW
        
        # Bot's turn: maximize score
        if player == self.bot:
            best_score = float("-inf")
            for r, c in moves:
                board[r][c] = self.bot
                score = self.minimax(board, self.human, alpha, beta)
                board[r][c] = None

                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if beta <= alpha: # Alpha-beta pruning
                    break
        # Human's turn: minimize score
        else:
            best_score = float("inf")
            for r, c in moves:
                board[r][c] = self.human
                score = self.minimax(board, self.bot, alpha, beta)
                board[r][c] = None

                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if beta <= alpha: # Alpha-beta pruning
                    break
        return int(best_score)

class Game:
    """Tic-Tac-Toe game manager"""

    def __init__(self, player_x: Player, player_o: Player, starting_player: Symbol = Symbol.X) -> None:
        self.board: Board = [[None for _ in range(3)] for _ in range(3)]
        self.players = {Symbol.X: player_x, Symbol.O: player_o}
        self.current = starting_player
        self.game_over = False
        self.winner: Symbol | None = None
        self.moves = 0
    
    def move(self, row: int, col: int) -> bool:
        """Make a move on the board"""
        if not (0 <= row <= 2 and 0 <= col <= 2) or self.board[row][col] is not None:
            return False
        
        self.board[row][col] = self.current
        self.moves += 1

        if Minimax.is_winner(self.board, self.current):
            self.winner = self.current
            self.game_over = True
        elif self.moves == 9:
            self.game_over = True
        else:
            self.current = Symbol(1 - self.current)
        
        return True
    
    def play(self) -> None:
        """Main game loop"""
        while not self.game_over:
            print(f"\nPlayer {['X', 'O'][self.current]}'s turn")
            self.display_board()

            current_player = self.players[self.current]
            row, col = current_player.get_move(self.board)
            self.move(row, col)
        
        self.display_board()
        print()
        if self.winner is None:
            print("Game is a draw!")
        else:
            print(f"Player {['X', 'O'][self.winner]} wins!")
    
    def display_board(self) -> None: 
        """Display current state of board"""
        symbols = {None: ".", Symbol.X: "X", Symbol.O: "O"}

        for i, row in enumerate(self.board):
            print(" | ".join(symbols[cell] for cell in row))
            if i < 2:
                print("--+---+--")

if __name__ == "__main__":
    score = {"X": 0, "O": 0, "Draw": 0}
    current_starter = Symbol.X

    while True:
        # Ask if playing against bot
        play_bot = input("Play against bot? (y/n): ").strip().lower() == 'y'

        if play_bot:
            # Get difficulty
            print("\nChoose difficulty:")
            print("1. Easy")
            print("2. Medium")
            print("3. Hard")

            while True:
                try:
                    choice = int(input("Enter choice (1-3): "))
                    difficulty_map = {
                        1: Difficulty.EASY,
                        2: Difficulty.MEDIUM,
                        3: Difficulty.HARD
                    }
                    if choice in difficulty_map:
                        difficulty = difficulty_map[choice]
                        break
                    print("Invalid choice, try again")
                except ValueError:
                    print("Please enter a number.")
            
            player_x = Human(Symbol.X)
            player_o = Bot(difficulty, Symbol.O)
        else:
            # Human vs human
            player_x = Human(Symbol.X)
            player_o = Human(Symbol.O)
        
        # Play Game
        game = Game(player_x, player_o, starting_player=current_starter)
        game.play()

        # Update score
        if game.winner is None:
            score["Draw"] += 1
        else:
            score[["X", "O"][game.winner]] += 1
        
        # Alternate the starting players
        current_starter = Symbol(1 - current_starter)

        # Display current score
        print(f"\nScore - X: {score["X"]}, O: {score["O"]}, Draws: {score["Draw"]}")