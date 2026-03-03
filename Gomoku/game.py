import random
from enum import Enum, IntEnum
from abc import ABC, abstractmethod

type Board = list[list[int | None]]

class Symbol(IntEnum):
    X = 0
    O = 1

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

class Player(ABC):
    """Abstract class for player"""

    @abstractmethod
    def get_move(self, board: Board) -> tuple[int, int]:
        """Get next move from player"""
        pass

    @staticmethod
    def get_valid_moves(board: Board) -> list[tuple[int, int]]:
        """Get the valid moves left on the board"""
        return [
            (row, col) 
            for row in range(len(board)) 
            for col in range(len(board)) 
            if board[row][col] is None 
        ]
    
    @staticmethod
    def find_winning_move(
        board: Board, 
        symbol: Symbol,
        valid_moves: list[tuple[int, int]],
    ) -> tuple[int, int] | None:
        """Find a move that wins for symbol, if one exists"""
        for r, c in valid_moves:
            board[r][c] = symbol.value
            is_win = Player.is_game_won(board, symbol)
            board[r][c] = None

            if is_win:
                return (r, c)
            
        return None

    @staticmethod
    def is_game_won(board: Board, symbol: Symbol, k=5) -> bool:
        """Return true is symbol has 5 in a row"""
        ROWS = len(board)
        COLS = len(board[0])
        DIRS = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(ROWS):
            for c in range(COLS):
                if board[r][c] != symbol.value:
                    continue

                for dr, dc in DIRS:
                    end_r = r + (k - 1) * dr
                    end_c = c + (k - 1) * dc
                    if not(0 <= end_r < ROWS and 0 <= end_c < COLS):
                        continue

                    if all(board[r + i * dr][c + i * dc] == symbol.value for i in range(k)):
                        return True
        return False

class Human(Player):
    """Human Player"""

    def __init__(self, symbol: Symbol) -> None:
        self.symbol = symbol 

    def get_move(self, board: Board) -> tuple[int, int]:
        """Get next move from user input"""
        while True:
            try:
                row = int(input(f"Enter a row (0-{len(board) - 1}): "))
                col = int(input(f"Enter a col (0-{len(board) - 1}): "))

                if 0 <= row < len(board) and 0 <= col < len(board) and board[row][col] is None:
                    return (row, col)

                print("Invalid move. Try Again")
            except ValueError:
                print("Please enter integers only")
    
class Bot(Player):
    """Bot Player with configurable difficulty"""

    def __init__(self, difficulty: Difficulty, symbol: Symbol) -> None:
        self.difficulty = difficulty
        self.symbol = symbol
        self.opponent = Symbol(1 - symbol.value)
        self.minimax = Minimax(bot=symbol) if difficulty == Difficulty.HARD else None
    
    def get_move(self, board: Board) -> tuple[int, int]:
        """Get next move from bot player based on difficulty"""
        valid_moves = self.get_valid_moves(board)

        if self.difficulty == Difficulty.EASY:
            return random.choice(valid_moves)
        
        if self.difficulty == Difficulty.MEDIUM:
            return self._medium_strategy(board)
        
        # Difficulty.HARD
        return self.minimax.get_best_move(board)
        
    def _medium_strategy(self, board: Board) -> tuple[int, int]:
        """Medium difficulty strategy"""
        valid_moves = self.get_valid_moves(board)

        # Try to win
        if win_move := self.find_winning_move(board, self.symbol, valid_moves):
            return win_move

        # Block opponent
        if block_move := self.find_winning_move(board, self.opponent, valid_moves):
            return block_move
        
        # Prefer center
        if (1, 1) in valid_moves:
            return (1, 1)
        
        # Prefer corners
        corners = [
            (0, 0),
            (0, len(board[0]) - 1),
            (len(board) - 1, 0),
            (len(board) - 1, len(board[0]) - 1),
        ]
        valid_corners = [move for move in valid_moves if move in corners]
        if valid_corners:
            return random.choice(valid_corners)
        
        # Random fallback
        return random.choice(valid_moves)

class Minimax:
    """Minimax algorithm for gomoku"""
    WIN = 1
    DRAW = 0
    LOSS = -1

    def __init__(self, bot: Symbol) -> None:
        self.bot = bot
        self.human = Symbol(1 - bot.value)

    def get_best_move(self, board: Board) -> tuple[int, int]:
        """Return the optimal move from minimax algorithm"""
        best_score = float("-inf")
        best_move = None
        alpha = float("-inf")
        beta = float("inf")

        for r, c in Player.get_valid_moves(board):
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
    
    def minimax(self, board: Board, symbol: Symbol, alpha: float, beta: float) -> int:
        """Minimax algorithm with alpha beta pruning"""
        # Terminal states
        if Player.is_game_won(board, self.bot):
            return self.WIN
        if Player.is_game_won(board, self.human):
            return self.LOSS
        
        moves = Player.get_valid_moves(board)
        if not moves:
            return self.DRAW
        
        # Bot's turn: maximise score
        if symbol == self.bot:
            best_score = float("-inf")
            for r, c in moves:
                board[r][c] = self.bot
                score = self.minimax(board, self.human, alpha, beta)
                board[r][c] = None

                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if beta <= alpha: # Alpha-beta pruning
                    break
        # Human's turn: minimise score
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
    """Gomoku game manager"""

    def __init__(
        self, 
        board_size: int,
        player_x: Player,
        player_o: Player,
        starting_player: Symbol = Symbol.X,
    ) -> None:
        self.board_size = board_size
        self.board = [[None for _ in range(board_size)] for _ in range(board_size)]
        self.players = {Symbol.X: player_x, Symbol.O: player_o}
        self.current = starting_player
        self.game_over = False
        self.winner: Symbol | None = None
        self.moves = 0
    
    def move(self, row: int, col: int) -> bool:
        "Make a move on the board"
        if not (0 <= row < self.board_size and 0 <= col < self.board_size) or self.board[row][col] is not None:
            return False
        
        self.board[row][col] = self.current
        self.moves += 1

        if Player.is_game_won(self.board, self.current):
            self.winner = self.current
            self.game_over = True
        elif self.moves == (self.board_size * self.board_size):
            self.game_over = True
        else:
            self.current = Symbol(1 - self.current.value)
        
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
        if self.winner is None:
            print("Game is a draw")
        else:
            print(f"Player {['X', 'O'][self.winner]} wins!")
        
    def display_board(self) -> None:
        """Display current board state."""
        symbols = {None: ".", Symbol.X.value: "X", Symbol.O.value: "O"}

        for i, row in enumerate(self.board):
            print(" | ".join(symbols[cell] for cell in row))
            if i < self.board_size - 1:
                print("---+" * (self.board_size - 1) + "---")

if __name__ == "__main__":
    score = {"X": 0, "O": 0, "Draw": 0}
    current_starter = Symbol.X

    while True:
        # Ask if they want to play
        continue_playing = input("Do you wish to start a game? (y/n)").strip().lower() == 'y'
        if not continue_playing:
            print(f"\nScore - X: {score['X']}, O: {score['O']}, Draws: {score['Draw']}")
            break

        # Ask if they would like to play against a bot
        play_bot = input("Play against bot? (y/n): ").strip().lower() == 'y'
        
        if play_bot:
            # Get difficulty
            print("\nChoose difficulty:")
            print("1. Easy")
            print("2. Medium")
            print("3. Hard")

            while True:
                try:
                    choice = int(input("Enter a difficulty (1-3): "))
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

        while True:
            try:
                board_size = int(input("Enter a board size: "))
                break
            except ValueError:
                print("Please enter a number.")
        
        game = Game(board_size, player_x, player_o, current_starter)
        game.play()

        if game.winner is None:
            score["Draw"] += 1
        else:
            score[["X", "O"][game.winner]] += 1

        # Alternate the starting players
        current_starter = Symbol(1 - current_starter.value)

        # Display current score
        print(f"\nScore - X: {score['X']}, O: {score['O']}, Draws: {score['Draw']}")