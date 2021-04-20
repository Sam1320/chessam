from abc import ABC, abstractmethod


class Piece(ABC):

    color: str
    value: int
    position: tuple

    @abstractmethod
    def move(self, x1, y1, x2, y2, coords_pieces):
        pass


class Pawn(Piece):
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.value = 1
        self.player = 1 if position[0] == 6 else 2

    def possible_moves(self, coords_pieces):
        x1, y1 = self.position
        moves = []
        # move upwards if player 1 else move downwards
        sign = -1 if self.player == 1 else 1
        options = [(sign*1, 1), (sign*1, 0), (sign*1, -1), (sign*2, 0)]
        for col, row in options:
            if self.valid_move(x1, y1, x1+col, y1+row, coords_pieces):
                moves.append((x1+col, y1+row))
        return moves

    def valid_move(self, x1, y1, x2, y2, coords_pieces):
        # Own pieces can't be taken
        taken = coords_pieces[(y2, x2)]
        if taken:
            color_taken = taken.color
            if self.color == color_taken:
                return False
        # One move forward
        if not taken and ((x1 == x2 and y1 == y2 + 1 and self.player == 1) or
                          (x1 == x2 and y1 == y2 - 1 and self.player == 2)):
            return True
        # Two moves forward and first move
        elif not taken and ((y1 == 1 or y1 == 6) and
                            ((x1 == x2 and y1 == y2 + 2 and self.player == 1) or
                            (x1 == x2 and y1 == y2 - 2 and self.player == 2))):
            return True
        # One square diagonal and take
        elif taken and ((abs(x1 - x2) == 1 and y1 == y2 + 1 and self.player == 1) or
                        (abs(x1 - x2) == 1 and y1 == y2 - 1 and self.player == 2)):
            return True
        return False

    def move(self, x1, y1, x2, y2, coords_pieces):
        pass



pawn1.move()
# print(pawn1.type)
