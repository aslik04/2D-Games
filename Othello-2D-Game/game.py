import random
from enum import IntEnum, Enum
from abc import ABC, abstractmethod

type Board = list[list[int | None]]

class Symbol(IntEnum):
    BLACK = 0
    WHITE = 1

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

class Player(ABC):
    """Abstract class for Player"""

    def get_move(board: Board) -> tuple[tuple[int, int], set[tuple[int, int]]]:
        """Get next move"""
        pass

    @staticmethod
    def get_valid_moves(
        board: Board, 
        symbol: Symbol,
    ) -> dict[tuple[int, int], set[tuple[int, int]]]:
        """Get the possible moves a player can make"""
        # Symbol values for comparison
        player_value = symbol.value

        return {
            (r, c): flipped
            for r in range(8)
            for c in range(8)
            if board[r][c] is None
            and (flipped := Player.pieces_flipped(board, r, c, player_value))
        }

    @staticmethod
    def pieces_flipped(
        board: Board, 
        r: int, 
        c: int,
        player_value: int,
    ) -> set[tuple[int, int]]:
        """Return all opponent pieces that would be flipped by playing (r, c)"""
        if board[r][c] is not None:
            return set()
        
        flips: set[tuple[int, int]] = set()

        opponent_value = 1 - player_value

        # All 8 directions
        dirs = [
            (-1, -1), (-1, 0), (-1, 1), 
             (0, -1),           (0, 1), 
             (1, -1),  (1, 0),  (1, 1)
        ]

        for dr, dc in dirs:
            row, col = r + dr, c + dc
            line: list[tuple[int, int]] = []

            # first must be opponent
            if not (0 <= row < 8 and 0 <= col < 8):
                continue
            if board[row][col] != opponent_value:
                continue
                
            # collect opponent run
            while 0 <= row < 8 and 0 <= col < 8 and board[row][col] == opponent_value:
                line.append((row, col))
                row += dr
                col += dc
            
            # a line is flippable only if it end of players piece
            if 0 <= row < 8 and 0 <= col < 8 and board[row][col] == player_value:
                flips.update(line)
        return flips

class Human(Player):
    """Human Player"""

    def __init__(self, symbol: Symbol) -> None:
        self.symbol = symbol 

    def get_move(self, board: Board) -> tuple[tuple[int, int], set[tuple[int, int]]]:
        """Get next move from user input"""

        while True:
            try:
                row = int(input(f"Please enter a row (0 - {len(board) - 1})"))
                col = int(input(f"Please enter a col (0 - {len(board[0]) - 1})"))

                if not (0 <= row < 8 and 0 <= col < 8):
                    print("Out of bounds. Try again.")
                    continue

                if flipped := self.pieces_flipped(board, row, col, self.symbol.value):
                    return (row, col), flipped

                print("Please enter a valid empty cell")
            except ValueError:
                print("Please enter an integer only")

class Bot(Player):
    """Bot Player"""

    def __init__(self, bot_symbol: Symbol, difficulty: Difficulty) -> None:
        self.bot_symbol = bot_symbol
        self.human_symbol = Symbol(1 - bot_symbol.value)
        self.difficulty = difficulty
    
    def get_move(self, board: Board) -> tuple[tuple[int, int], set[tuple[int, int]]]:
        """Get next move for the bot"""
        valid_moves = self.get_valid_moves(board, self.bot_symbol)

        if not valid_moves:
            print("No valid moves must pass")
            return None

        if self.difficulty == Difficulty.EASY:
            move = random.choice(list(valid_moves))
            return move, valid_moves[move]
        
        # Difficulty.MEDIUM
        return self._medium_strategy(board, valid_moves)

    def _medium_strategy(self, board: Board, valid_moves: dict[tuple[int, int], set[tuple[int, int]]]) -> tuple[tuple[int, int], set[tuple[int, int]]]:
        """Get the next move if bot is on medium difficulty"""
        CORNERS = [(0, 0), (0, 7), (7, 0), (7, 7)]
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        valid_corner = [
            (r, c)
            for r, c in CORNERS
            if (r, c) in valid_moves
        ]
        if valid_corner:
            move = random.choice(valid_corner)
            return move, valid_moves[move]
        
        # Choose a valid move which does not give opponenet a corner move
        valid_non_corner = []
        possible_moves = {}
        for (r, c), flipped in valid_moves.items():
            # pseudo candidates = neighbours of newly affected squares
            affected = {(r, c)} | flipped
            pseudo_cand = {
                (ar + dr, ac + dc)
                for ar, ac in affected 
                for dr, dc in dirs
                if 0 <= ar + dr < 8
                and 0 <= ac + dc < 8
                and board[ar + dr][ac + dc] is None
            }
            possible_moves[(r, c)] = len(pseudo_cand)

            # Risky if a move gives opponet a corner
            gives_corner = any(
                corner in pseudo_cand
                and self.pieces_flipped(board, corner[0], corner[1], self.human_symbol.value)
                for corner in CORNERS
            )

            if not gives_corner:
                valid_non_corner.append((r, c))
        if valid_non_corner:
            move = random.choice(valid_non_corner)
            return move, valid_moves[move]

        # Choose any edge node if available
        EDGES = [(0, c) for c in range(8)] + [(r, 0) for r in range(8)] + [(7, c) for c in range(1, 7)] + [(r, 7) for r in range(1, 7)]
        valid_edges = [
            (r, c)
            for r, c in EDGES
            if (r, c) in valid_moves
        ]
        if valid_edges:
            move = random.choice(valid_edges)
            return move, valid_moves[move]
        
        sorted_possible_moves = sorted(possible_moves.items(), key=lambda kv: kv[1])
        best_score = sorted_possible_moves[0][1]
        tied = [move for move, score in sorted_possible_moves if score == best_score]
        choice = random.choice(tied)

        return choice, valid_moves[choice]

class Game:
    """Game"""

    def __init__(self, player_b: Player, player_w: Player, starting_player: Symbol) -> None:
        self.board = [[None for _ in range(8)] for _ in range(8)]

        self.board[3][3] = Symbol.BLACK.value
        self.board[3][4] = Symbol.WHITE.value
        self.board[4][3] = Symbol.WHITE.value
        self.board[4][4] = Symbol.BLACK.value

        self.players = {Symbol.BLACK: player_b, Symbol.WHITE: player_w}
        self.current = starting_player
        self.game_over = False
        self.winner = None
        self.moves = 0

    def move(self, row: int, col: int, flipped: set[tuple[int, int]]) -> bool:
        """Make a move in the game"""
        self.board[row][col] = self.current
        self.moves += 1

        for r, c in flipped:
            self.board[r][c] = self.current
        
        if self.moves == 60:
            self.game_over = True
            self.winner = self._find_winner()
        else:
            self.current = Symbol(1 - self.current.value)

        return True 

    def _find_winner(self) -> Symbol | None:
        """Find who won the game"""
        cells = (cell for row in self.board for cell in row)
        black = sum(cell == Symbol.BLACK for cell in cells)
        white = sum(cell == Symbol.WHITE for cell in cells)

        if black == white:
            return None
        return Symbol.BLACK if black > white else Symbol.WHITE
    
    def play(self):
        """Main game play loop"""
        while not self.game_over:
            print(f"Player: {["Black", "White"][self.current.value]}'s turn")
            self.display_board()

            current_player = self.players[self.current]
            if (result := current_player.get_move(self.board)) is not None:
                (row, col), flipped = result
                self.move(row, col, flipped)

        self.display_board()

        if self.winner is None:
            print("Game is a draw")
        else:
            print(f"Player {["Black", "White"][self.winner]} wins!")

    def display_board(self) -> None:
        """Pretty-print Othello board with coordinates."""
        symbols = {
            None: ".",
            Symbol.BLACK.value: "B",
            Symbol.WHITE.value: "W",
        }

        n = len(self.board)

        # Column header
        print("   " + " ".join(f"{c:2}" for c in range(n)))

        # Rows
        for r, row in enumerate(self.board):
            print(f"{r:2} " + " ".join(f"{symbols[cell]:2}" for cell in row))

if __name__ == "__main__":
    score = {"Black": 0, "White": 0, "Draw": 0}
    current_starter = Symbol.BLACK

    while True:
        # Ask if they want to play
        continue_playing = input("Do you wish to start a game? (y/n)").strip().lower() == 'y'
        if not continue_playing:
            print(f"\nScore - Black: {score["Black"]}, White: {score["White"]}, Draws: {score['Draw']}")
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

            play_botvbot = input("Play bot v bot? (y/n): ").strip().lower() == 'y'

            if play_botvbot:
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
                            difficulty_two = difficulty_map[choice]
                            break
                        print("Invalid choice, try again")
                    except ValueError:
                        print("Please enter a number.")
                
                player_black = Bot(Symbol.BLACK, difficulty_two)
                player_white = Bot(Symbol.WHITE, difficulty)
            else:
                player_black = Human(Symbol.BLACK)
                player_white = Bot(Symbol.WHITE, difficulty)
        else:
            # Human vs human
            player_black = Human(Symbol.BLACK)
            player_white = Human(Symbol.WHITE)
        
        game = Game(player_black, player_white, current_starter)
        game.play()

        if game.winner is None:
            score["Draw"] += 1
        else:
            score[["Black", "White"][game.winner]] += 1

        # Alternate the starting players
        current_starter = Symbol(1 - current_starter.value)

        # Display current score
        print(f"\nScore - Black: {score["Black"]}, White: {score["White"]}, Draws: {score['Draw']}")