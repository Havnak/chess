from textual.app import App, ComposeResult
from textual.widgets import Footer, Button, Label
from textual.containers import Grid, Container, Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
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
                        row=row, col=col, piece_art=piece_art, id=f"r{row}c{col}"
                    )

class InfoBox(Container):
    """ Widget to display information such as moves, game result, engine analysis and such """

    def __init__(self, board, **kwargs):
        super().__init__(**kwargs)
        self.moves_made = board.moves_made
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("", id="gamestate")
            with Grid():
                yield ScrollableContainer(id="moves")
                # yield EvaluationBar(id="evalFish")
    
    def add_single_move(self, move: str, number):
        string = f"{number}. {move:>6}" # Longest sting is 6 chars, e.g. e4xe5#
        move = Label(string, id="single")
        self.query_one("#moves").mount(move)

    def add_both_moves(self, move: list, number):
        self.query_one("#single").remove()
        string = f"{number}. {move[0]:>6} {move[1]:>6}" 
        move = Label(string)
        self.query_one("#moves").mount(move)

    def update_moves(self, moves: list):
        if len(moves) % 2 == 0:
            self.add_both_moves(moves[-2:], len(moves)//2)
        else:
            self.add_single_move(moves[-1], len(moves)//2+1)

    def reset(self):
        labels = self.query(Label)
        if labels:
            for label in labels:
                label.remove()



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

        king, check = board.detect_check()
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


    def action_reset_board(self):
        self.restart()

    def action_kill_piece(self):
        selected_piece.kill_piece = True

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield visual_board
            yield info_box
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
            selected_piece.square.standard_style()

            if (square_pressed.row,
                square_pressed.col,
            ) in selected_piece.piece.legal_moves:
                board.move(selected_piece.piece, square_pressed.row, square_pressed.col)

                # --- promotion ---
                if isinstance(selected_piece.piece, Pawn) and selected_piece.piece.row in [0, 7]:
                    raise NotImplementedError
                    # TODO: Pop up for selecting piece
                    board.promote_pawn(selected_piece.piece, new_piece)
                
                self.query_one(InfoBox).update_moves(board.moves_made)
            
            self.update_board()
            selected_piece.reset()

            if board.checkmate():
                self.query_one("#gamestate").update("Checkmate")

            if board.stalemate():
                self.query_one("#gamestate").update("Stalemate")

            if board.remis():
                self.query_one("#gamestate").update("Remis")
