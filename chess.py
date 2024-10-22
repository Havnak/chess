"""
Classes for all chess pieces and board
"""

import copy
import numpy as np

def row_col_to_chess_notation(row, col) -> str:
    num_to_alph = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    return num_to_alph[col] + str(row + 1)


def chess_notation_to_row_col(chess_notation: str):
    return (ord(chess_notation[0].lower()) - 97, chess_notation[1] - 1)

def on_straight(row1,col1, row2, col2) -> bool:
    return (row1 == row2 or col1 == col2)

def on_diagonal(row1, col1, row2, col2) -> bool:
    """ """
    return (row1 - col1 == row2 - col2) or (row1 + col1 == row2 + col2)

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

def check(board) -> tuple:
    """
    Returns:
        king, bool
    """
    for king in board.kings.values():
        for piece in board.pieces:
            if piece.color == king.color:
                continue

            if piece.piece_type in ["b", "q"]:
                if on_diagonal(*king.pos, *piece.pos):
                    if not piece_between(*king.pos, *piece.pos, board):
                        return king, True

            if piece.piece_type in ["r", "q"]:
                if on_straight(*king.pos, *piece.pos):
                    if not piece_between(*king.pos, *piece.pos, board):
                        return king, True

            if piece.piece_type == "p":
                for row, col in piece.attacking_moves:
                    if all([
                            king.row - row< 8,
                            king.row - row>= 0,
                            king.col - col < 8,
                            king.col - col >= 0,
                            ]
                    ):
                        if board[king.row - row][king.col - col]:
                            if board[king.row - row][king.col - col].color != king.color:
                                return king, True

    return None, False

def check_after_move(piece, row, col, board, color):
    board_copy = copy.deepcopy(board)
    board_copy.iscopy = True
    piece_copy = board_copy[piece.row][piece.col]
    board_copy.move(piece_copy, row, col)
    board_copy.turn = color
    king, is_checked = check(board_copy)
    if not is_checked: 
        return False
    if king.color == color:
        return True

def checkmate_after_move(piece, row, col, board, color):
    board_copy = copy.deepcopy(board)
    board_copy.iscopy = True
    piece_copy = board_copy[piece.row][piece.col]
    board_copy.move(piece_copy, row, col)
    board_copy.turn = color
    checkmate = board_copy.checkmate()

    if checkmate: return True
    return False

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


    def get_legal_moves(self, board):
        self.update_legal_moves(board)
        return self.legal_moves

    def ispinned(self, board):
        king = board.kings[self.color]
        if on_line(*self.pos, *king.pos): # Only check pinning if you are on line with the king  

            if piece_between(*self.pos, *king.pos, board): return False, (0, 0) # Cant be pinned if there are pieces between you and the king
            
            for piece in board.pieces:
                if piece.piece_type in ["b", "q"] and piece.color != self.color:
                    if on_diagonal(*piece.pos, *king.pos):
                        pieces_between = piece_between(*piece.pos, *king.pos, board)
                        if len(pieces_between)==1:  # Only self is between attacking piece and king
                            if pieces_between[0] is self:
                                return True, get_direction(*self.pos, *piece.pos)

                if piece.piece_type in ["r", "q"] and piece.color != self.color:
                    if on_straight(*piece.pos, *king.pos):
                        pieces_between = piece_between(*piece.pos, *king.pos, board)
                        if len(pieces_between)==1: # Only self is between attacking piece and king
                            if pieces_between[0] is self:
                                return True, get_direction(*self.pos, *piece.pos)
        return False, (0, 0) 

    def update_legal_moves(self, board):
        self.legal_moves = []
        moves = copy.copy(self.moves)

        if board.game_end: return
    
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
                    if not check_after_move(self, row + self.row, col + self.col, board, self.color):
                        self.legal_moves.append((row + self.row, col + self.col))

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

        if board.game_end: return

        # --- moves ---

        row, col = self.moves
        if not pinned or pin_direction == (row, col):
            if not (board[self.row + row][self.col + col]):
                if not check_after_move(self, self.row + row, self.col + col, board, self.color):
                    self.legal_moves.append((self.row + row, self.col + col))
                    if ((self.row, self.color) in [(1, "W"), (6, "B")]
                        and not board[self.row + 2*row][self.col + 2*col]
                    ):
                        if not check_after_move(self, self.row + 2*row, self.col + 2*col, board, self.color):
                            self.legal_moves.append((self.row + 2*row, self.col + 2*col))

        # --- attacks ---
        for row, col in self.attacking_moves:
            if not pinned or (row, col) == pin_direction:
                if all([
                        row + self.row < 8,
                        row + self.row >= 0,
                        col + self.col < 8,
                        col + self.col >= 0,
                        ]
                ):
                    if isinstance(board[self.row + row][self.col + col], Piece):
                        if board[self.row + row][self.col + col].color != self.color:
                            if not check_after_move(self, self.row + row, self.col + col, board, self.color):
                                self.legal_moves.append((self.row + row, self.col + col))

        # --- en passant ---
        if (self.row, self.color) in [(3, "B"),(4, "W")]:
            for col in [1, -1]:
                if all([
                        row + self.row < 8,
                        row + self.row >= 0,
                        col + self.col < 8,
                        col + self.col >= 0,
                        ]
                ):
                    if (self.row + 1 - 2*(self.color == "B"), self.col + col) == board.en_passant_able:
                        if not check_after_move(self, self.row + 1 - 2*(self.color == "B"), self.col + col, board, self.color):
                            self.legal_moves.append((self.row + 1 - 2*(self.color == "B"), self.col + col))


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

    def casteling_moves(self, board):
        row, col = self.row, self.col
        if check(board):
            return

        if self.piece_type == "k":
            if self.color == "W":
                if "K" in board.casteling:
                    if not piece_between(*self.pos, self.row, 7, board):
                        if not (check_after_move(self, row, col + 1, board, self.color) or check_after_move(self, row, col + 2, board, self.color)):
                            self.legal_moves.append((row, col+2))

                if "Q" in board.casteling:
                    if not piece_between(*self.pos, self.row, 0, board):
                        if not (check_after_move(self, row, col - 1, board, self.color) or check_after_move(self, row, col - 2, board, self.color)):
                            self.legal_moves.append((row, col-2))
                    
            else:
                if "k" in board.casteling:
                    if not piece_between(*self.pos, self.row, 7, board):
                        if not (check_after_move(self, row, col + 1, board, self.color) or check_after_move(self, row, col + 2, board, self.color)):
                            self.legal_moves.append((row, col+2))

                if "q" in board.casteling:
                    if not piece_between(*self.pos, self.row, 0, board):
                        if not (check_after_move(self, row, col - 1, board, self.color) or check_after_move(self, row, col - 2, board, self.color)):
                            self.legal_moves.append((row, col-2))
    
    def update_legal_moves(self, board):
        super().update_legal_moves(board)
        if board.game_end: return
        self.casteling_moves(board)


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
        if board.game_end: return

        # --- logic for pinning ---
        moves = copy.copy(self.moves)
        pinned, direction = self.ispinned(board)

        if pinned:
            if direction in moves:
                dir_row, dir_col = direction
                row, col = dir_row + self.row, dir_col + self.col
                while all([row < 8, row >= 0, col < 8, col >= 0]):
                    if not board[row][col]:
                        if not check_after_move(self, row, col, board, self.color):
                            self.legal_moves.append((row, col))

                    else:
                        if board[row][col].color != self.color:
                            if not check_after_move(self, row, col, board, self.color):
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
                    if not check_after_move(self, row, col, board, self.color):
                        self.legal_moves.append((row, col))

                else:
                    if board[row][col].color != self.color:
                        if not check_after_move(self, row, col, board, self.color):
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
        self.casteling = "KQkq"
        self.kings = {}
        self.pieces = []
        self.chess_board = self.setup_board()
        self.turn = "W"
        self.en_passant_able = ()
        self.moves_made = []
        self.iscopy = False
        self.halfmoves = 0
        self.fullmoves = 1
        self.game_end = False
        self.positions = []
        

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

    def fen(self):
        fen = ""
        for row in reversed(self.chess_board):
            empty_squares = 0
            for square in row:
                if square:
                    if empty_squares > 0: fen += str(empty_squares)
                    fen += square.piece_type.upper() if square.color == "W" else square.piece_type
                    empty_squares = 0
                else:
                    empty_squares += 1
            if empty_squares > 0: fen += str(empty_squares)
            fen += "/"
        fen = fen[:-1] + " " # remove last "/"
        casteling = "".join(self.casteling.split("-"))
        fen += self.turn.lower() + " " + (casteling if casteling else "-")+ " "

        en_passant_target_square = self.en_passant_able
        if en_passant_target_square: fen += row_col_to_chess_notation(*en_passant_target_square) + " "
        else: fen += "- "
        
        fen += str(self.halfmoves) + " " + str(self.fullmoves)

        return fen

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
        self.__init__()

    def get_all_legal_moves(self):
        legal_moves = []
        for piece in self.pieces:
            if piece.color == self.turn:
                legal_moves += piece.get_legal_moves(self)
        return legal_moves

    def promote_pawn(self, pawn, new_piece): # TODO
        board[pawn.row][pawn.col] = new_piece
        self.pieces.remove(pawn)
        self.pieces.append(new_piece)

    def checkmate(self):
        if len(self.get_all_legal_moves()) == 0:
            _, in_check = check(self)
            if in_check:
                self.game_end = True
                return True
        return False

    def stalemate(self):
        if len(self.get_all_legal_moves()) == 0:
            _, in_check = check(self)
            if not in_check:
                self.game_end = True
                return True
        return False

    def fifty_moves(self):
        if self.halfmoves == 100: 
            self.game_end = True
            return True
        return False

    def repetition(self):
        current_fen = self.fen().split(" ")[0]
        if sum([1 if current_fen in position else 0 for position in self.positions]) > 2:
            self.game_end = True
            return True
        return False
    
    def remis(self):
        # TODO
        return False

    def update_moves_made(self, piece, row, col):
        capture = ""
        if self[row][col]:
            capture = "x"

        previous_position = ""
        legal_moves = self.get_all_legal_moves()
        if sum([1 if (row, col) == move else 0 for move in legal_moves]) > 1:
            previous_position = row_col_to_chess_notation(*piece.pos)

        check = ""
        if check_after_move(piece, row, col, self, {"W": "B", "B": "W"}[piece.color]):
            check = "+"
            if checkmate_after_move(piece, row, col, self, {"W": "B", "B": "W"}[piece.color]):
                check = "#"

        self.moves_made.append(previous_position + capture + row_col_to_chess_notation(row, col) + check)

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
            if (row, col) == self.en_passant_able:
                self.capture(row - direction, col)

        self.en_passant_able = ()
        if isinstance(piece, Pawn):
            if ((piece.row, piece.color) in [(1,"W"), (6, "B")] # If pawn is on start row
                and row == piece.row + 2*direction
                ):
                    self.en_passant_able = (row-direction, col)
            
        # --- promotion needs interaction, therefore it's handled in the UI ---

        if not self.iscopy:
            self.update_moves_made(piece, row, col)

        # --- casteling ---
        if piece.piece_type == "k":
            if piece.color == "W":
                if piece.pos == (0, 4):
                    if "K" in self.casteling and (row, col) == (0, 6):
                        self.move(self[0][7], 0, 5)
                        self.turn = {"W": "B", "B": "W"}[self.turn] # We are making 2 moves, and therefore we need to toggle turn again
                        if not self.iscopy: 
                            del self.moves_made[-2]
                            self.moves_made[-1] = "O-O"

                    if "Q" in self.casteling and (row, col) == (0, 2):
                        self.move(self[0][0], 0, 3)
                        self.turn = {"W": "B", "B": "W"}[self.turn]
                        if not self.iscopy: 
                            del self.moves_made[-2]
                            self.moves_made[-1] = "O-O-O"
                    
                self.casteling = "".join(["-" if castle.isupper() else castle for castle in self.casteling])

            else:
                if piece.pos == (7, 4):
                    if "k" in self.casteling and (row, col) == (7, 6):
                        self.move(self[7][7], 7, 5)
                        self.turn = {"W": "B", "B": "W"}[self.turn]
                        if not self.iscopy: 
                            del self.moves_made[-2]
                            self.moves_made[-1] = "O-O"

                    if "q" in self.casteling and (row, col) == (7, 2):
                        self.move(self[7][0], 7, 3)
                        self.turn = {"W": "B", "B": "W"}[self.turn]
                        if not self.iscopy: 
                            del self.moves_made[-2]
                            self.moves_made[-1] = "O-O-O"

                self.casteling = "".join(["-" if castle.islower() else castle for castle in self.casteling])


        if piece.piece_type == "r":
            if piece.color == "W":
                if piece.col == 0:
                    self.casteling = "".join(["-" if castle == "Q" else castle for castle in self.casteling])
                if piece.col == 7:
                    self.casteling = "".join(["-" if castle == "K" else castle for castle in self.casteling])

            else:
                if piece.col == 0:
                    self.casteling = "".join(["-" if castle == "q" else castle for castle in self.casteling])
                if piece.col == 7:
                    self.casteling = "".join(["-" if castle == "k" else castle for castle in self.casteling])

        self[piece.row][piece.col] = None
        self.halfmoves += 1
        if isinstance(piece, Pawn) or self[row][col]:
            self.halfmoves = 0
            self.positions = []

        self.capture(row, col) # Before moving, capture piece if capture is going to happen
        piece.update_position(row, col)
        self.chess_board[row][col] = piece
        # --- turn finished ---
        if self.turn == "B": self.fullmoves += 1
        self.positions.append(self.fen().split(" ")[0])
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
    b = Board()
    b.move(b[0][1], 2, 2)
    b.move(b[7][1], 5, 2)
    b.move(b[2][2], 0, 1)
    b.move(b[5][2], 7, 1)
    b.move(b[0][1], 2, 2)
    b.move(b[7][1], 5, 2)
    b.move(b[2][2], 0, 1)
    b.move(b[5][2], 7, 1)
    b.move(b[0][1], 2, 2)
    b.move(b[7][1], 5, 2)
    b.move(b[2][2], 0, 1)
    b.move(b[5][2], 7, 1)
    print(len(b.positions))
    print(b.positions)
    print(b.repetition())
    print(b)
