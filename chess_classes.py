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

    def update_position(self, row, col):
        self.row = row
        self.col = col

    def __repr__(self):
        return (self.piece_art, row_col_to_chess_notation(*self.pos))

    def __str__(self):
        return self.piece_art

    def update_legal_moves(self, board):
        """Placeholder for child-specific implemented function"""
        pass


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

        def update_legal_moves1(self, board):
            self.legal_moves = []


class Rook(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♖" if self.color == "W" else "♜"


class Knight(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♘" if self.color == "W" else "♞"


class Bishop(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♗" if self.color == "W" else "♝"


class Queen(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♕" if self.color == "W" else "♛"


class King(Piece):
    def __init__(self, color, **kwargs):
        super().__init__(color, **kwargs)
        self.piece_art = "♔" if self.color == "W" else "♚"


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


if __name__ == "__main__":
    B = Board()
    print(B)

    B.move(B.chess_board[1][0], *(2, 0))
    B.move(B.chess_board[2][0], *(3, 0))
    print(B)
