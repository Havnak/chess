from textual.app import App, ComposeResult
from textual.widgets import Footer, Button, Label
from textual.containers import Grid, Container, Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
from textual import on
from textual.reactive import reactive
import pyperclip 
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
        self.active_effect_duration = 0

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
                        row=row, col=col, piece_art=piece_art, id=f"r{row}c{col}", classes="square"
                    )

class ChoosePiece(Container):

    def __init__(self, color, promotion=True):
        super().__init__()
        self.promotion = promotion
        self.color = color

        self.pieces = {
                "W": ["♔", "♕", "♖", "♗", "♘", "♙"],
                "B": ["♚", "♛", "♜", "♝", "♞", "♟"]
                }
        
        self.piece_to_str = {
                        "♔": "K",
                        "♕": "Q",
                        "♖": "R",
                        "♗": "B",
                        "♘": "N",
                        "♙": "P",
                        "♚": "k",
                        "♛": "q",
                        "♜": "r",
                        "♝": "b",
                        "♞": "n",
                        "♟": "p"
                        }

    def compose(self) -> ComposeResult:
        with Vertical():
            for piece in self.pieces[self.color][1:-1] if self.promotion else self.pieces[self.color]:
                yield Button(piece, id=self.piece_to_str[piece], classes="PickerButton")

class InfoBox(Container):
    """ Widget to display information such as moves, game result, engine analysis and such """

    def __init__(self, board, **kwargs):
        super().__init__(**kwargs)
        self.moves_made = board.moves_made
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("", id="gamestate")
            with Horizontal(id="sidebar"):
                yield ScrollableContainer(id="moves")
                # yield EvaluationBar(id="evalFish")
            with Container(id="fen_box"):
                with Horizontal():
                    yield Label(f"fen: ")
                    yield Button("copy", id="copyfen") 
                yield Label(f"{board.fen()}", id="fen")
        
    def add_single_move(self, move: str, number):
        string = f" {number}. {move:>6}" # Longest sting is 6 chars, e.g. e4xe5#
        move = Label(string, id="single")
        container = self.query_one("#moves")
        container.mount(move)
        move.scroll_visible()

    def add_both_moves(self, move: list, number):
        self.query_one("#single").remove()
        string = f" {number}. {move[0]:>6} {move[1]:>6}" 
        move = Label(string)
        container = self.query_one("#moves")
        container.mount(move)
        move.scroll_visible()

    def update_moves(self, moves: list):
        if len(moves) % 2 == 0:
            self.add_both_moves(moves[-2:], len(moves)//2)
        else:
            self.add_single_move(moves[-1], len(moves)//2+1)

    def reset(self):
        labels = self.query("ScrollableContainer > Label")
        if labels:
            for label in labels:
                label.remove()
        self.query_one("#fen").update(f"fen:\n{board.fen()}")





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
info_box = InfoBox(board)


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
        for row, rank in enumerate(board.chess_board):
            for col, piece in enumerate(rank):
                square = self.query_one(f"#r{row}c{col}")
                square.piece_art = Text(piece.piece_art, style="black") if piece else ""
                square.standard_style()

        king, check, attacking_piece = board.detect_check()
        if check:
            self.query_one(f"#r{king.row}c{king.col}").highlight_check()

    def restart(self):
        global board
        board = Board()
        selected_piece.reset()
        info_box.reset()
        self.update_board()

    @on(Button.Pressed, "#restart")
    def button_restart(self):
        self.restart()

    @on(Button.Pressed, "#quit")
    def quit(self):
        exit()

    @on(Button.Pressed, "#copyfen")
    def copy_fen(self):
        pyperclip.copy(board.fen())

    @on(Button.Pressed, ".PickerButton")
    def handle_select_piece(self, event: Button.Pressed):
        new_piece = event.button.id
        board.promote_pawn(new_piece)
        board.game_end = False
        self.query_one(ChoosePiece).remove()
        self.update_board()

    def action_reset_board(self):
        self.restart()

    def action_kill_piece(self):
        selected_piece.kill_piece = True

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield visual_board
            yield info_box
        yield Footer()

    @on(Button.Pressed, "ChessSquareVisual")
    def handle_square_pressed(self, event: Button.Pressed):
        square_pressed = event.button
        piece = board.chess_board[square_pressed.row][square_pressed.col]

        if selected_piece.kill_piece:
            board.capture(square_pressed.row, square_pressed.col)
            self.update_board()
            selected_piece.kill_piece = False
            return

        # --- Selecting piece to move ---
        if (not selected_piece.piece or (piece.color == board.turn if piece else False)) and not selected_piece.piece is piece:
            if piece and piece.color == board.turn:
                self.update_board()
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
            if selected_piece.piece:
                if (square_pressed.row,
                    square_pressed.col,
                ) in selected_piece.piece.legal_moves:
                    board.move(selected_piece.piece, square_pressed.row, square_pressed.col)

                    # --- promotion ---
                    if isinstance(selected_piece.piece, Pawn) and selected_piece.piece.row in [0, 7]:
                        piece_picker = ChoosePiece(selected_piece.piece.color)
                        self.query_one("#sidebar").mount(piece_picker)
        
                    self.query_one(InfoBox).update_moves(board.moves_made)
            
            self.query_one("#fen").update(f"{board.fen()}")
            selected_piece.reset()
            self.update_board()

            if board.checkmate():
                self.query_one("#gamestate").update("Checkmate")

            if board.stalemate():
                self.query_one("#gamestate").update("Remis: Stalemate")

            if board.fifty_moves():
                self.query_one("#gamestate").update("Remis: 50 move rule")

            if board.repetition():
                self.query_one("#gamestate").update("Remis: repetition")
