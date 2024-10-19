from textual.app import App, ComposeResult
from textual.widgets import Footer, Button
from textual.containers import Grid, Container
from textual import on
from textual.reactive import reactive
from rich.text import Text

from chess import *


class ChessSquareVisual(Button):
    """A widget for each square on the chess board"""

    piece_art = reactive("")

    def __init__(self, row: int, col: int, piece_art: str = "", **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        art = Text(piece_art, style="black")
        self.piece_art = art
        self.standard_style()

    def standard_style(self):
        if (self.row + self.col) % 2 == 0:
            self.styles.background = "#5f7782"
        else:
            self.styles.background = "#b6b7ba"

    def highlight(self):
        self.styles.background = "#33ff57"

    def highlight_moves(self):
        self.styles.background = "#FFA500"

    def highlight_check(self):
        self.styles.background = "red"

    def render(self):
        return self.piece_art


class ChessBoardVisual(Container):
    """A widget to display the chess board"""

    def __init__(self, board: Board, **kwargs):
        super().__init__(**kwargs)
        self.chess_board = board.chess_board

    def compose(self) -> ComposeResult:
        with Grid():
            for row in range(7, -1, -1):
                for col in range(8):
                    piece_art = (
                        self.chess_board[row][col].piece_art
                        if self.chess_board[row][col]
                        else ""
                    )
                    yield ChessSquareVisual(
                        row=row, col=col, piece_art=piece_art, id=f"r{row}c{col}"
                    )


class SelectedPiece:
    """
    Piece currently selected

    variables:
        self.piece<Piece>
        self.square<ChessSquareVisual>
        self.kill_piece<Bool>

    functions:
        set_(self, piece: Piece)
        reset(self)
    """

    def __init__(self):
        self.piece: Piece = None
        self.square: ChessSquareVisual = None
        self.kill_piece: bool = False

    def set_(self, piece: Piece, square: ChessSquareVisual):
        self.piece = piece
        self.square = square

    def reset(self):
        self.piece = None
        self.square = None


board = Board()
selected_piece = SelectedPiece()
visual_board = ChessBoardVisual(board)


class ChessApp(App):
    TITLE = "sjakk"
    # SUB_TITLE = "Chess in your terminal"
    CSS_PATH = "statics/chess.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reset_board", "Reset board"),
        ("k", "kill_piece", "Capture piece"),
    ]

    def update_board(self):
        for row, line in enumerate(board.chess_board):
            for col, piece in enumerate(line):
                square = self.query_one(f"#r{row}c{col}")
                square.piece_art = Text(piece.piece_art, style="black") if piece else ""
                square.standard_style()

        king, check = board.detect_check()
        if check:
            self.query_one(f"#r{king.row}c{king.col}").highlight_check()

    def action_reset_board(self):
        board.reset()
        self.update_board()

    def action_kill_piece(self):
        selected_piece.kill_piece = True

    def compose(self) -> ComposeResult:
        yield visual_board
        yield Footer()

    @on(ChessSquareVisual.Pressed)
    def handle_square_pressed(self, event: ChessSquareVisual.Pressed):
        square_pressed = event.button
        piece = board.chess_board[square_pressed.row][square_pressed.col]

        if selected_piece.kill_piece:
            board.capture(square_pressed.row, square_pressed.col)
            self.update_board()
            selected_piece.kill_piece = False
            return

        # --- Selecting piece to move ---
        if not selected_piece.piece:
            if piece and piece.color == board.turn:
                selected_piece.set_(piece, square_pressed)
                square_pressed.highlight()
                selected_piece.piece.update_legal_moves(board)

                for move in selected_piece.piece.legal_moves:
                    self.query_one("#r%dc%d" % move).highlight_moves()

            else:
                selected_piece.reset()
                square_pressed.standard_style()

        # --- Moving selected piece ---
        else:
            selected_piece.square.standard_style()

            if (square_pressed.row,
                square_pressed.col,
            ) in selected_piece.piece.legal_moves:
                board.move(selected_piece.piece, square_pressed.row, square_pressed.col)

            self.update_board()
            selected_piece.reset()
