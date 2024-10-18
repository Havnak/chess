from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static, Button
from textual.containers import Grid, Container
from textual import on
from rich.text import Text
from classes import *


class ChessSquare(Button):
    """A widget for each square on the chess board"""
    
    def __init__(self, row: int, col: int, piece_art: str = '', **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.piece_art = piece_art
        self.update_style()
        self.legal_move = False

    def update_style(self):
        if (self.row + self.col) % 2 == 0:
            self.styles.background = "#b6b7ba"
        else:
            self.styles.background = "#5f7782"
        
        art = Text(self.piece_art, style="white")
        self.piece_art = art

    def render(self) -> str:
        """Return the string representation of the square, including the piece."""
        return self.piece_art
    

class ChessBoard(Container):
    """A widget to display the chess board"""

    def __init__(self, board: Board, **kwargs):
        super().__init__(**kwargs)
        self.chess_board = board.chess_board
    
    def compose(self) -> ComposeResult:
        with Grid():
            for row in range(8):
                for col in range(8):
                    piece_art = self.chess_board[row][col].piece_art if (row<2 or row>5) else ""
                    yield ChessSquare(row=row, col=col, piece_art=piece_art, id=f"r{row}c{col}")

class SelectedPiece():
    """
    Piece currently selected

    variables:
        self.piece: Piece

    functions:
        set_selected_piece(self, piece: Piece, turn: board.turn)
        reset_selected_piece(self)
    """
    def __init__(self):
        self.piece: Piece = None
    
    def set_selected_piece(self, piece: Piece, turn):
        if turn == piece.color:
            self.piece = piece

    def reset_selected_piece(self):
        self.piece = None

board = Board()
selected_piece = SelectedPiece()

class ChessApp(App):
    # TITLE = "sjakktui"
    # SUB_TITLE = "Chess in your terminal"
    CSS_PATH = "statics/chess.tcss"

    BINDINGS = [
            ("q", "quit", "Quit"), 
            ("r", "reset_borad", "Reset board")
            ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ChessBoard(board)
        yield Footer()

    @on(ChessSquare.Pressed)
    def handle_square_pressed(self, event: ChessSquare.Pressed):
        global selected_piece
        global board
        square = event.button
        piece = board.chess_board[square.row][square.col]

        if not selected_piece.piece: # No selected piece
            if piece: 
                selected_piece.set_selected_piece(piece, board.turn)
                # Update visuals on board to show legal moves
            else:
                selected_piece.reset_selected_piece()

        else: # Selected own piece
            if [square.row, square.col] in selected_piece.piece.legal_moves:
                board.move(selected_piece.piece, square.row, square.col)


        



