"""
Classes for all chess pieces and board
"""

class Piece():
    def __init__(self, color):
        self.color = color
        self.position = ""
        self.legal_moves = ""
        self.piece_art = ""

    def __str__(self):
        return self.piece_art

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.piece_art = "♙" if self.color == "W" else "♟"

    def update_legal_moves(self, Board):
        pass

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.piece_art = "♖" if self.color == "W" else "♜"

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.piece_art = "♘" if self.color == "W" else "♞"

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.piece_art = "♗" if self.color == "W" else "♝"

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.piece_art = "♕" if self.color == "W" else "♛"

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.piece_art = "♔" if self.color == "W" else "♚"



class Board():
   
    def __init__(self):
        self.chess_board = self.setup_board()

    def setup_board(self):
        board = []

        row1 = [Rook("W"), Knight("W"), Bishop("W"), Queen("W"), King("W"), Bishop("W"), Knight("W"), Rook("W")]
        row2 = [Pawn("W") for _ in range(8)]

        row7 = [Pawn("B") for _ in range(8)]
        row8 = [Rook("B"), Knight("B"), Bishop("B"), Queen("B"), King("B"), Bishop("B"), Knight("B"), Rook("B")]

        board.append(row1)
        board.append(row2)

        for _ in range(4): board.append([None] * 8) # Empty rows

        board.append(row7)
        board.append(row8)
        return board

        
    def __str__(self):
        board_str = "\n"
        for row in self.chess_board:
            row_str = ' '.join(str(piece) if piece else '.' for piece in row)
            board_str += row_str + "\n"
        return board_str

class Game():
    def __init__(self):
        self.turn = "W"

    
                    

if __name__ == "__main__":
    B = Board()
    print(B)
