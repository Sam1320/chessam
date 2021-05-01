class Piece:
    def __init__(self, name, position=(0, 0)):
        self.name = name
        self.position = position
        self.color = name.split("_")[0]
        self.type = name.split("_")[1]

    @staticmethod
    def on_board(x, y):
        if (0 <= x <= 7) and (0 <= y <= 7):
            return True
        return False

    def set_position(self, position):
        self.position = position

    def friend_here(self, x, y, coords_pieces):
        taken = coords_pieces[(y, x)]
        if taken:
            color_taken = taken.color
            if self.color == color_taken:
                return True
        return False


class Pawn(Piece):
    def __init__(self, name, position):
        super().__init__(name, position)
        self.value = 1
        self.player = 1 if self.position[0] == 6 else 2

    def possible_moves(self, coords_pieces):
        y1, x1 = self.position
        moves = []
        # move upwards if player 1 else move downwards
        sign = -1 if self.player == 1 else 1
        options = [(sign*1, 1), (sign*1, 0), (sign*1, -1), (sign*2, 0)]
        for col, row in options:
            if self.valid_move(x1+col, y1+row, coords_pieces):
                moves.append((x1+col, y1+row))
        return moves

    def valid_move(self, x2, y2, coords_pieces):
        # Check if valid square
        if not self.on_board(x2, y2):
            return False
        y1, x1 = self.position
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


class Rook(Piece):
    def __init__(self, name, position):
        super().__init__(name, position)
        self.value = 5
        self.player = 1 if self.position[0] == 7 else 2

    def possible_moves(self, coords_pieces):
        y1, x1 = self.position
        moves = []
        for i in range(1, 8):
            if self.valid_move(x1+i, y1, coords_pieces):
                moves.append((x1+i, y1))
            if self.valid_move(x1-i, y1, coords_pieces):
                moves.append((x1-i, y1))
            if self.valid_move(x1, y1+i, coords_pieces):
                moves.append((x1, y1+i))
            if self.valid_move(x1, y1-i, coords_pieces):
                moves.append((x1, y1-i))
        return moves

    def valid_move(self, x2, y2, coords_pieces):
        if not self.on_board(x2, y2):
            return False
        y1, x1 = self.position
        if (x1 == x2 or y1 == y2) and (x1 != x2 or y1 != y2):
            # upward movement
            if x1 == x2 and y1 > y2:
                for i in range(1, abs(y1 - y2)):
                    if coords_pieces[(y1 - i, x1)]:
                        return False
            # downward movement
            elif x1 == x2 and y1 < y2:
                for i in range(1, abs(y1 - y2)):
                    if coords_pieces[(y1 + i, x1)]:
                        return False
            # rightward movement
            elif x1 < x2 and y1 == y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(y1, x1 + i)]:
                        return False
            # leftward movement
            elif x1 > x2 and y1 == y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(y1, x1 - i)]:
                        return False
            return True
        else:
            return False


class Knight(Piece):
    def __init__(self, name, position):
        super().__init__(name, position)
        self.value = 3
        self.player = 1 if position[0] == 7 else 2

    def possible_moves(self, coords_pieces):
        y, x = self.position
        moves = []
        options = [(-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2),
                   (-2, -1), (-2, 1)]
        for row, col in options:
            if self.valid_move(x+col, y+row, coords_pieces):
                moves.append((x+col, y+row))
        return moves

    def valid_move(self, x2, y2, coords_pieces):
        if not self.on_board(x2, y2):
            return False
        x1, y1 = self.position
        if max(abs(x1-x2), abs(y1-y2)) == 1:
            if not self.friend_here(x2, y2, coords_pieces):
                return True
        return False


class Bishop(Piece):
    def __init__(self, name, position):
        super().__init__(name, position)
        self.value = 3
        self.player = 1 if position[0] == 7 else 2

    def possible_moves(self, coords_pieces):
        y1, x1 = self.position
        moves = []
        for i in range(1, 8):
            if self.valid_move(x1-i, y1+i, coords_pieces):
                moves.append((x1-i, y1+i))
            if self.valid_move(x1+i, y1+i, coords_pieces):
                moves.append((x1+i, y1+i))
            if self.valid_move(x1+i, y1-i, coords_pieces):
                moves.append((x1+i, y1-i))
            if self.valid_move(x1-i, y1-i, coords_pieces):
                moves.append((x1-i, y1-i))
        return moves

    def valid_move(self, x2, y2, coords_pieces):
        y1, x1 = self.position
        if not self.on_board(x2, y2):
            return False
        if abs(x1 - x2) == abs(y1 - y2):
            # up and right movement
            if x1 < x2 and y1 > y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(y1 - i, x1 + i)]:
                        return False
            # down and right movement
            elif x1 < x2 and y1 < y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(y1 + i, x1 + i)]:
                        return False
            # up and left movement
            elif x1 > x2 and y1 > y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(y1 - i, x1 - i)]:
                        return False
            # down and left movement
            elif x1 > x2 and y1 < y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(y1 + i, x1 - i)]:
                        return False
            return True
        else:
            return False


class Queen(Piece):
    def __init__(self, name, position):
        super().__init__(name, position)
        self.value = 3
        self.player = 1 if position[0] == 7 else 2

    def possible_moves(self, coords_pieces):
        rook = Rook(self.color, self.position)
        bishop = Bishop(self.color, self.position)
        moves = []

        moves.extend(bishop.possible_moves(coords_pieces))
        moves.extend(rook.possible_moves(coords_pieces))
        return moves

    def valid_move(self, x2, y2, coords_pieces):
        rook = Rook(self.color, self.position)
        bishop = Bishop(self.color, self.position)

        return rook.valid_move(x2, y2, coords_pieces) or \
            bishop.valid_move(x2, y2, coords_pieces)


class King(Piece):
    def __init__(self, name, position):
        super().__init__(name, position)
        self.value = 3
        self.player = 1 if position[0] == 7 else 2

    def possible_moves(self, coords_pieces):
        y, x = self.position
        moves = []
        options = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                   (0, -1), (-1, -1)]
        for row, col in options:
            if self.valid_move(x+col, y+row, coords_pieces):
                moves.append((x+col, y+row))
        return moves

    def valid_move(self, x2, y2, coords_pieces):
        if not self.on_board(x2, y2):
            return False
        x1, y1 = self.position
        if max(abs(x1-x2), abs(y1-y2)) == 1:
            if not self.friend_here(x2, y2, coords_pieces):
                return True
        return False

    def checked(self, coords_pieces):
        pass
