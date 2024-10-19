"""
Classes for all chess pieces and board
"""

import numpy as np


def row_col_to_chess_notation(row, col):
    num_to_alph = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    return num_to_alph[col] + str(row + 1)


def chess_notation_to_row_col(chess_notation: str):
    output = chess_notation[1] - 1
    output += str(ord(chess_notation[0].lower()) - 97)
    return output


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
        self.en_passant_able: bool = False
        self.moves = []

    def update_position(self, row, col):
        self.row = row
        self.col = col

    def __repr__(self):
        return (self.piece_art, row_col_to_chess_notation(*self.pos))

    def __str__(self):
        return self.piece_art

    def update_legal_moves(self, board):
        self.legal_moves = []
        for row, col in self.moves:
            if all([row + self.row < 8, row + self.row >= 0, col + self.col < 8, col + self.col >= 0]):
                if (not board.chess_board[row + self.row][col + self.col] 
                    or board.chess_board[row + self.row][col + self.col].color != self.color
                ):
                    self.legal_moves.append((row + self.row, col + self.col))


class Pawn(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♙" if self.color == "W" else "♟"

    def update_legal_moves(self, board):

        direction = (
            1 if self.color == "W" else -1
        )  # Direction pawn moves based on color

        self.legal_moves = []

        if not board.chess_board[self.row + direction][self.col]:
            self.legal_moves.append((self.row + direction, self.col))

            if (
                self.row == 1
                and not board.chess_board[self.row + 2][self.col]
                and self.color == "W"
            ):
                self.legal_moves.append((self.row + 2, self.col))
                self.en_passant_able = True
                self.moves_since_en_passant_able = 0

            elif (
                self.row == 6
                and not board.chess_board[self.row - 2][self.col]
                and self.color == "B"
            ):
                self.legal_moves.append((self.row - 2, self.col))
                self.en_passant_able = True
                self.moves_since_en_passant_able = 0

        if self.col < 7:
            if board.chess_board[self.row + direction][self.col + 1]:
                if (
                    board.chess_board[self.row + direction][self.col + 1].color
                    != self.color
                ):
                    self.legal_moves.append((self.row + direction, self.col + 1))

        if self.col > 0:
            if board.chess_board[self.row + direction][self.col - 1]:
                if (
                    board.chess_board[self.row + direction][self.col - 1].color
                    != self.color
                ):
                    self.legal_moves.append((self.row + direction, self.col - 1))

        if self.color == "W" and self.row == 4:
            if self.col > 0:
                if isinstance(board.chess_board[self.row][self.col - 1], Pawn):
                    if board.chess_board[self.row][self.col - 1].en_passant_able:
                        self.legal_moves.append((self.row + 1, self.col - 1))

            if self.col < 7:
                if isinstance(board.chess_board[self.row][self.col + 1], Pawn):
                    if board.chess_board[self.row][self.col + 1].en_passant_able:
                        self.legal_moves.append((self.row + 1, self.col + 1))


class Slider(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.moves = []
    
    def update_legal_moves(self, board):
        self.legal_moves = []
        for dir_row, dir_col in self.moves:
            row, col = dir_row + self.row, dir_col + self.col
            while all([row < 8, row >= 0, col < 8, col >= 0]):
                if (not board.chess_board[row][col] 
                ):
                    self.legal_moves.append((row, col))

                else:
                    if board.chess_board[row][col].color != self.color:
                        self.legal_moves.append((row, col))
                    break

                col += dir_col
                row += dir_row


class Rook(Slider):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♖" if self.color == "W" else "♜"
        self.has_moved = False
        self.moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class Knight(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♘" if self.color == "W" else "♞"
        self.moves = [(1, 2), (-1, -2), (1, -2), (-1, 2), (2, 1), (-2, -1), (2, -1), (-2, 1)]


class Bishop(Slider):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♗" if self.color == "W" else "♝"
        self.moves = [(1,1), (1,-1), (-1,1), (-1,-1)]


class Queen(Slider):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♕" if self.color == "W" else "♛"
        self.moves = [(1,1), (1,-1), (-1,1), (-1,-1), (1, 0), (-1, 0), (0, 1), (0, -1)]


class King(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♔" if self.color == "W" else "♚"
        self.has_moved = False
        self.moves =  [ 
                    (1, -1), (1, 0), (1, 1),
                    (0, -1),         (0, 1),
                    (-1,-1), (-1,0), (-1,1)]




























































            if (
                not board.chess_board[self.row - 1][self.col]
                or board.chess_board[self.row - 1][self.col].color != self.color
            ):
                self.legal_moves.append((self.row - 1, self.col))

            if self.col > 0:
                if (
                    not board.chess_board[self.row - 1][self.col - 1]
                    or board.chess_board[self.row - 1][self.col - 1].color != self.color
                ):
                    self.legal_moves.append((self.row - 1, self.col - 1))

        if self.col > 0:
            if (
                not board.chess_board[self.row][self.col - 1]
                or board.chess_board[self.row][self.col - 1].color != self.color
            ):
                self.legal_moves.append((self.row, self.col - 1))

            if self.row < 7:
                if (
                    not board.chess_board[self.row + 1][self.col - 1]
                    or board.chess_board[self.row + 1][self.col - 1].color != self.color
                ):
                    self.legal_moves.append((self.row + 1, self.col - 1))


class Board:

    def __init__(self):
        self.chess_board = self.setup_board()
        self.turn = "W"

    def __str__(self):
        board_str = "\n"
        for row in reversed(self.chess_board):
            row_str = " ".join(str(piece) if piece else "." for piece in row)
            board_str += row_str + "\n"
        return board_str

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
        self.chess_board[piece.row][piece.col] = None
        piece.update_position(*(row, col))
        self.chess_board[row][col] = piece
        direction = 1 if piece.color == "W" else -1

        # --- en passant ---
        if (
            isinstance(piece, Pawn)
            and isinstance(self.chess_board[row - direction][col], Pawn)
            and self.chess_board[row - direction][col].en_passant_able
        ):
            self.capture(row - direction, col)

        for row in self.chess_board:
            for piece in row:
                if isinstance(piece, Pawn) and piece.en_passant_able:
                    if piece.moves_since_en_passant_able == 2:
                        piece.en_passant_able = False
                    else:
                        piece.moves_since_en_passant_able += 1

        # --- turn finished ---
        self.turn = {"W": "B", "B": "W"}[self.turn]

    def capture(self, row, col):
        self.chess_board[row][col] = None
