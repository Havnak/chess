from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static, Button
from textual.containers import Grid, Container
from textual import on
from rich.text import Text
from chess_classes import *


class ChessSquare(Button):
    """A widget for each square on the chess board"""
    
    def __init__(self, row: int, col: int, piece_art: str = '', **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        art = Text(piece_art, style="white")
        self.piece_art = art
        self.standard_style()

        
    def standard_style(self):
        if (self.row + self.col) % 2 == 0:
            self.styles.background = "#5f7782"
        else:
            self.styles.background = "#b6b7ba"


    def render(self) -> str:
        """Return the string representation of the square, including the piece."""
        return self.piece_art
    
    def highlight(self):
        self.styles.background = "#33ff57" 


class ChessBoard(Container):
    """A widget to display the chess board"""

    def __init__(self, board: Board, **kwargs):
        super().__init__(**kwargs)
        self.chess_board = board.chess_board
    
    def compose(self) -> ComposeResult:
        with Grid():
            for row in range(7, -1, -1):
                for col in range(8):
                    piece_art = self.chess_board[row][col].piece_art if (row<2 or row>5) else ""
                    yield ChessSquare(row=row, col=col, piece_art=piece_art, id=f"r{row}c{col}")


class SelectedPiece():
    """
    Piece currently selected

    variables:
        self.piece: Piece

    functions:
        set_selected_piece(self, piece: Piece)
        reset_selected_piece(self)
    """
    def __init__(self):
        self.piece: Piece = None
        self.square: ChessSquare = None
    
    def set_selected_piece(self, piece: Piece, square: ChessSquare):
        self.piece = piece
        self.square = square

    def reset_selected_piece(self):
        self.piece = None
        self.square = None


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
        square_pressed = event.button
        piece = board.chess_board[square_pressed.row][square_pressed.col]
        # --- Selecting piece to move ---
        if not selected_piece.piece: # No selected piece
            if piece and piece.color == board.turn: 
                selected_piece.set_selected_piece(piece, square_pressed)
                square_pressed.highlight()
                # Update visuals on board to show legal moves
            else:
                selected_piece.reset_selected_piece()
                square_pressed.standard_style()

        # --- Moving selected piece ---
        else: # Selected own piece
            selected_piece.square.standard_style()
            row, col = square_pressed.row, square_pressed.col
            if (row, col) in selected_piece.piece.legal_moves:
                board.move(selected_piece.piece, row, col)





        


