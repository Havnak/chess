"""
Classes for all chess pieces and board
"""

import copy
import numpy as np

def row_col_to_chess_notation(row, col):
    num_to_alph = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    return num_to_alph[col] + str(row + 1)


def chess_notation_to_row_col(chess_notation: str):
    return (ord(chess_notation[0].lower()) - 97, chess_notation[1] - 1)

def on_straight(row1,col1, row2, col2) -> bool:
    return (row1 == row2 or col1 == col2)

def on_diagonal(row1, col1, row2, col2) -> bool:
    """ """
    if on_straight(row1, col1, row2, col2):
        return False

    diagonals = [np.array([1, 1, 0]), np.array([1, -1, 0]), np.array([-1, 1, 0]), np.array([-1, -1, 0])]
    vector_pos1_pos2 = np.array([row2-row1, col2-col1, 0])
    return not np.all([np.cross(vector_pos1_pos2, diagonal) for diagonal in diagonals]) # Vectors are parallel if cross product is 0, added 0 in z-direction for deprecation warning

def on_line(row1, col1, row2, col2) -> bool:
    return on_straight(row1, col1, row2, col2) or on_diagonal(row1, col1, row2, col2)

def distance(row1, col1, row2, col2) -> float:
    """
    returns:
        <float> of euclidian distance between (row1, col1) and (row2, col2)
    """
    return np.sqrt((row2-row1)**2 + (col2-col1)**2)

def get_direction(row1, col1, row2, col2) -> tuple:
    """
    returns:
        <tuple> of direction vector from pos(row1, col1) to pos(row2, col2)
    """
    if 0 not in [row2 - row1, col2 - col1]:
        return round((row2-row1)/abs(row2-row1)), round((col2-col1)/abs(col2-col1))
    if (row2-row1) != 0:
        return round((row2-row1)/abs(row2-row1)), round(col2-col1)
    if (col2-col1) != 0:
        return round(row2-row1), round((col2-col1)/abs(col2-col1))

def piece_between(row1, col1, row2, col2, board) -> list:
    """
    Return:
        list of pieces between pos(row1, col1) and pos(row2, col2) 
        or [] if none
    """
    pieces_between = []
    d = distance(row1, col1, row2, col2)
    for row in board:
        for piece in row:
            if not piece: continue
            if piece.pos in [(row1, col1), (row2, col2)]: continue
            if (on_line(row1, col1, row2, col2)):
                if np.isclose(distance(*piece.pos, row1, col1) + distance(*piece.pos, row2, col2), d): # If B is between A and C, distance(A, C) is the same as distance(A, B) + distance(B, C)
                    pieces_between.append(piece)
    return pieces_between


class Piece:
    """
    Parent class for pieces

    variables:
        color<str>: hex color
        row<int>
        col<int>
        legal_moves<list[tuple(int)]>: list of tuples of legal moves [(row, col)]
    """

    def __init__(self, color, row, col):
        self.color = color
        self.row = row
        self.col = col
        self.pos = (row, col)
        self.legal_moves = []
        self.piece_art = ""
        self.moves = []
        self.piece_type = ""

    def __repr__(self):
        return f"{type(self).__name__}({self.color}, {row_col_to_chess_notation(*self.pos)})"

    def __str__(self):
        return self.piece_art

    def update_position(self, row, col):
        self.row = row
        self.col = col
        self.pos = row, col


    def ispinned(self, board):
        king = board.kings[self.color]
        if on_line(*self.pos, *king.pos): # Only check pinning if you are on line with the king  

            if piece_between(*self.pos, *king.pos, board): return False, (0, 0) # Cant be pinned if there are pieces between you and the king
            
            for piece in board.pieces:
                if piece.piece_type in ["b", "q"]:
                    if on_diagonal(*piece.pos, *king.pos):
                        pieces_between = piece_between(*piece.pos, *king.pos, board)
                        if len(pieces_between)==1:
                            if pieces_between[0] is self:
                                return True, get_direction(*self.pos, *piece.pos)

                if piece.piece_type in ["r", "q"]:
                    if on_straight(*piece.pos, *king.pos):
                        pieces_between = piece_between(*piece.pos, *king.pos, board)
                        if len(pieces_between)==1:
                            if pieces_between[0] is self:
                                return True, get_direction(*self.pos, *piece.pos)
        return False, (0, 0) 


    def update_legal_moves(self, board):
        self.legal_moves = []
        moves = copy.copy(self.moves)
        
        # --- logic for pinning ---
        pinned, direction = self.ispinned(board)
        if pinned:
            moves = []

        for row, col in moves:
            if all(
                [
                    row + self.row < 8,
                    row + self.row >= 0,
                    col + self.col < 8,
                    col + self.col >= 0,
                ]
            ):
                if (
                    not board[row + self.row][col + self.col]
                    or board[row + self.row][col + self.col].color != self.color
                ):
                    self.legal_moves.append((row + self.row, col + self.col))

    def get_legal_moves(self, board):
        self.update_legal_moves(board)
        return self.legal_moves

    


class Pawn(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♙" if self.color == "W" else "♟"
        self.piece_type = "p"
        if color == "W":
            self.moves = (1, 0)
            self.attacking_moves = [(1, 1), (1, -1)]

        if color == "B":
            self.moves = (-1, 0)
            self.attacking_moves = [(-1, 1), (-1, -1)]

    def update_legal_moves(self, board):
        self.legal_moves = []
        pinned, pin_direction = self.ispinned(board)

        # --- moves ---

        row, col = self.moves
        if not pinned or pin_direction == (row, col):
            if not (board[self.row + row][self.col + col]):
                self.legal_moves.append((self.row + row, self.col + col))
                if ((self.row, self.color) in [(1, "W"), (6, "B")]
                    and not board[self.row + 2*row][self.col + 2*col]
                ):
                    self.legal_moves.append((self.row + 2*row, self.col + 2*col))

        # --- attacks ---
        for row, col in self.attacking_moves:
            if not pinned or (row, col) == pin_direction:
                if isinstance(board[self.row + row][self.col + col], Piece):
                    if board[self.row + row][self.col + col].color != self.color:
                        self.legal_moves.append((self.row + row, self.col + col))

        # --- en passant ---
        if (self.row, self.color) in [(3, "B"),(4, "W")]:
            for col in [1, -1]:
                if (self.row, self.col + col) == board.en_passant_able:
                    self.legal_moves.append((self.row + direction, self.col + col))


class King(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_type = "k"
        self.piece_art = "♔" if self.color == "W" else "♚"
        self.has_moved = False
        self.moves = [
            (1, 1),
            (1, -1),
            (1, 0),
            (-1, 1),
            (-1, -1),
            (-1, 0),
            (0, 1),
            (0, -1),
        ]


class Knight(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_type = "n"
        self.piece_art = "♘" if self.color == "W" else "♞"
        self.moves = [
            (1, 2),
            (-1, -2),
            (1, -2),
            (-1, 2),
            (2, 1),
            (-2, -1),
            (2, -1),
            (-2, 1),
        ]



class Slider(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.moves = []

    def update_legal_moves(self, board):
        self.legal_moves = []

        # --- logic for pinning ---
        moves = copy.copy(self.moves)
        pinned, direction = self.ispinned(board)

        if pinned:
            if direction in moves:
                dir_row, dir_col = direction
                row, col = dir_row + self.row, dir_col + self.col
                while all([row < 8, row >= 0, col < 8, col >= 0]):
                    if not board[row][col]:
                        self.legal_moves.append((row, col))

                    else:
                        if board[row][col].color != self.color:
                            self.legal_moves.append((row, col))
                        break

                    col += dir_col
                    row += dir_row
                return
        # ---

        for dir_row, dir_col in moves:
            row, col = dir_row + self.row, dir_col + self.col
            while all([row < 8, row >= 0, col < 8, col >= 0]):
                if not board[row][col]:
                    self.legal_moves.append((row, col))

                else:
                    if board[row][col].color != self.color:
                        self.legal_moves.append((row, col))
                    break

                col += dir_col
                row += dir_row


class Rook(Slider):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_type = "r"
        self.piece_art = "♖" if self.color == "W" else "♜"
        self.has_moved = False
        self.moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class Bishop(Slider):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_type = "b"
        self.piece_art = "♗" if self.color == "W" else "♝"
        self.moves = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


class Queen(Slider):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_type = "q"
        self.piece_art = "♕" if self.color == "W" else "♛"
        self.moves = [
            (1, 1),
            (1, -1),
            (1, 0),
            (-1, 1),
            (-1, -1),
            (-1, 0),
            (0, 1),
            (0, -1),
        ]



def check(board) -> tuple:
    output = (None, False)
    for row in board:
        for piece in row:
            if output[1]:
                return output

            if isinstance(piece, King):
                king: King = piece
                direction = 1 if king.color == "W" else -1
                output = (
                    king,
                    (
                        # --- Check pawn ---
                        any(
                            isinstance(board[row][col], Pawn)
                            and board[row][col].color != king.color
                            for row, col in [
                                (king.row + direction, king.col + 1),
                                (king.row + direction, king.col - 1),
                            ]
                        )
                        # --- Check straight line ---
                        or any(
                            (
                                isinstance(board[row][col], Rook)
                                or isinstance(board[row][col], Queen)
                            )
                            and board[row][col].color != king.color
                            for row, col in Rook(
                                king.color, row=king.row, col=king.col
                            ).get_legal_moves(board)
                        )
                        # --- Check diagonals ---
                        or any(
                            (
                                isinstance(board[row][col], Bishop)
                                or isinstance(board[row][col], Queen)
                            )
                            and board[row][col].color != king.color
                            for row, col in Bishop(
                                king.color, row=king.row, col=king.col
                            ).get_legal_moves(board)
                        )
                        # --- Check horse ---
                        or any(
                            (
                                isinstance(board[row][col], Knight)
                                and board[row][col].color != king.color
                            )
                            for row, col in Knight(
                                king.color, row=king.row, col=king.col
                            ).get_legal_moves(board)
                        )
                    ),
                )
    return output


class Board:
    """
    Board class, all game logic happens here.

    functions:
        setup_board(): Sets up game, pieces on starting positions

        move(piece, row, col): handles moving logic

        reset(): calls setup_board() and sets white to turn

        capture(row, col): removes piece on chess_borad[row][col]
    """

    def __init__(self):
        self.kings = {}
        self.pieces = []
        self.chess_board = self.setup_board()
        self.turn = "W"
        self.en_passant_able = ()
        

    def __str__(self):
        board_str = "\n"
        for row in reversed(self.chess_board):
            row_str = " ".join(str(piece) if piece else "." for piece in row)
            board_str += row_str + "\n"
        return board_str

    def __getitem__(self, index):
        return self.chess_board[index]

    def __setitem__(self, index, value):
        self.chess_board[index] = value

    def __len__(self):
        return len(self.chess_board)

    def setup_board(self):
        board = []

        row1 = [
            Rook("W", row=0, col=0),
            Knight("W", row=0, col=1),
            Bishop("W", row=0, col=2),
            Queen("W", row=0, col=3),
            King("W", row=0, col=4),
            Bishop("W", row=0, col=5),
            Knight("W", row=0, col=6),
            Rook("W", row=0, col=7),
        ]

        row2 = [Pawn("W", row=1, col=col) for col in range(8)]
        row7 = [Pawn("B", row=6, col=col) for col in range(8)]

        row8 = [
            Rook("B", row=7, col=0),
            Knight("B", row=7, col=1),
            Bishop("B", row=7, col=2),
            Queen("B", row=7, col=3),
            King("B", row=7, col=4),
            Bishop("B", row=7, col=5),
            Knight("B", row=7, col=6),
            Rook("B", row=7, col=7),
        ]

        board.append(row1)
        board.append(row2)

        for _ in range(4):
            board.append([None] * 8)

        board.append(row7)
        board.append(row8)

        self.pieces += row1 + row2 + row7 + row8
        self.kings["W"] = row1[4]
        self.kings["B"] = row8[4]

        return board

    def reset(self):
        self.chess_board = self.setup_board()
        self.turn = "W"

    def move(self, piece: Piece, row, col):
        """
        Move Piece to [row, col]

        Arguments:
            piece<Piece>: piece to be moved
            square<[row, col]>: square moved to
        """

        direction = 1 if piece.color == "W" else -1

        # --- en passant ---
        if (isinstance(piece, Pawn)):
            if (row - direction, col) == self.en_passant_able:
                self.capture(row - direction, col)

        self.en_passant_able = ()
        if isinstance(piece, Pawn):
            if ((piece.row, piece.color) in [(1,"W"), (6, "B")] # If pawn is on start row
                and row == piece.row + 2*direction
                ):
                    self.en_passant_able = (row, col)

        self.chess_board[piece.row][piece.col] = None
        self.capture(row, col) # Before moving, capture piece if capture is going to happen
        piece.update_position(row, col)
        self.chess_board[row][col] = piece
        
        # --- turn finished ---
        self.turn = {"W": "B", "B": "W"}[self.turn]

    def detect_check(self):
        return check(self)

    def capture(self, row, col):
        """ ** Must be called before updating attacking pieces position ** """
        self.chess_board[row][col] = None
        for piece in self.pieces:
            if piece.pos == (row, col):
                self.pieces.remove(piece)


if __name__ == "__main__":
    print("Hi:)")
