from copy import deepcopy

class Piece:
    def __init__(self, color, position, player):
        self.position = position
        self.color = color
        self.player = player
        self.type = None
        self.moved = False
        self.taken = False

    @staticmethod
    def on_board(x, y):
        if (0 <= x <= 7) and (0 <= y <= 7):
            return True
        return False

    # The king is the only piece that overrides this method
    def castle(self, x, y, pieces_coords, coords_pieces):
        return False

    def move(self, x, y):
        self.position = (x, y)
        if not self.moved:
            self.moved = True


    def set_position(self, position):
        self.position = position

    def friend_here(self, x, y, coords_pieces):
        taken = coords_pieces[(x, y)]
        if taken:
            if self.color == taken.color:
                return True
        return False

    def my_turn(self, player):
        # Only allow turn based moves
        if self.player == player:
            return True
        return False

    def my_king_checked(self, x2, y2, coords_pieces, pieces_coords):
        x1, y1 = self.position
        # assume no check
        check = False
        # simulate move
        old_piece = coords_pieces[(x2, y2)]
        pieces_coords[old_piece] = None
        pieces_coords[self] = (x2, y2)
        self.set_position((x2, y2))
        coords_pieces[(x1, y1)] = None
        coords_pieces[(x2, y2)] = self

        if self.type == "king":
            check = self.checked(coords_pieces)
        else:
            for piece in pieces_coords:
                if piece:
                    if piece.color == self.color and piece.type == "king":
                        check = piece.checked(coords_pieces)
                        break

        # restore position
        coords_pieces[(x2, y2)] = old_piece
        pieces_coords[old_piece] = (x2, y2)
        coords_pieces[(x1, y1)] = self
        pieces_coords[self] = (x1, y1)
        self.set_position((x1, y1))
        return check

    def legal_move(self, x, y, coords_pieces, pieces_coords, player):
        pieces_coords_copy = deepcopy(pieces_coords)
        coords_pieces_copy = deepcopy(coords_pieces)
        if self.on_board(x, y) \
                and self.my_turn(player) \
                and not self.friend_here(x, y, coords_pieces_copy) \
                and not self.my_king_checked(x, y, coords_pieces_copy, pieces_coords_copy):
            return True
        return False


class Pawn(Piece):
    def __init__(self, color, position, player):
        super().__init__(color, position, player)
        self.type = "pawn"
        self.name = self.color + "_" + self.type + "_" + str(position[1])
        self.value = 1

    def possible_moves(self, coords_pieces, pieces_coords, player, name_piece):
        x1, y1 = self.position
        moves = []
        # move upwards if player 1 else move downwards
        sign = -1 if self.player == 1 else 1
        options = [(1, sign*1), (0, sign*1), (-1, sign*1), (0, sign*2)]
        for x, y in options:
            if self.valid_move(x1+x, y1+y, coords_pieces, pieces_coords, player, name_piece):
                moves.append((x1+x, y1+y))
        return moves

    def valid_move(self, x2, y2, coords_pieces, pieces_coords, player, name_piece):
        # Check if valid square
        if not self.legal_move(x2, y2, coords_pieces, pieces_coords, player):
            return False

        x1, y1 = self.position
        taken = coords_pieces[(x2, y2)]
        passant = name_piece["en_passant"]
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
        # En passant
        elif passant:
            y3, x3 = passant.position
            if x3 == x2 and y3 == y1:
                return True
        return False




class Rook(Piece):
    def __init__(self, color, position, player):
        super().__init__(color, position, player)
        self.type = "rook"
        self.name = self.color + "_" + self.type + "_" + str(position[1])
        self.value = 5

    def possible_moves(self, coords_pieces, pieces_coords, player, name_piece):
        x1, y1 = self.position
        moves = []
        for i in range(1, 8):
            if self.valid_move(x1+i, y1, coords_pieces, pieces_coords, player, name_piece):
                moves.append((x1+i, y1))
            if self.valid_move(x1-i, y1, coords_pieces, pieces_coords, player, name_piece):
                moves.append((x1-i, y1))
            if self.valid_move(x1, y1+i, coords_pieces, pieces_coords, player, name_piece):
                moves.append((x1, y1+i))
            if self.valid_move(x1, y1-i, coords_pieces, pieces_coords, player, name_piece):
                moves.append((x1, y1-i))
        return moves

    def valid_move(self, x2, y2, coords_pieces, pieces_coords, player, name_piece):
        if not self.legal_move(x2, y2, coords_pieces, pieces_coords, player):
            return False
        x1, y1 = self.position
        if (x1 == x2 or y1 == y2) and (x1 != x2 or y1 != y2):
            # upward movement
            if x1 == x2 and y1 > y2:
                for i in range(1, abs(y1 - y2)):
                    if coords_pieces[(x1, y1-i)]:
                        return False
            # downward movement
            elif x1 == x2 and y1 < y2:
                for i in range(1, abs(y1 - y2)):
                    if coords_pieces[(x1, y1+i)]:
                        return False
            # rightward movement
            elif x1 < x2 and y1 == y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(x1, y1+i)]:
                        return False
            # leftward movement
            elif x1 > x2 and y1 == y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(x1, y1-i)]:
                        return False
            return True
        else:
            return False


class Knight(Piece):
    def __init__(self, color, position, player):
        super().__init__(color, position, player)
        self.type = "knight"
        self.name = self.color + "_" + self.type + "_" + str(position[1])
        self.value = 3

    def possible_moves(self, coords_pieces, pieces_coords, player, name_piece):
        x1, y1 = self.position
        moves = []
        options = [(-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2),
                   (-2, -1), (-2, 1)]
        for x, y in options:
            if self.valid_move(x1+x, y1+y, coords_pieces, pieces_coords, player, name_piece):
                moves.append((x1+x, y1+y))
        return moves

    def valid_move(self, x2, y2, coords_pieces, pieces_coords, player, name_piece):
        if not self.legal_move(x2, y2, coords_pieces, pieces_coords, player):
            return False
        x1, y1 = self.position
        if (abs(x1 - x2) == 2 and abs(y1 - y2) == 1) or \
                (abs(x1 - x2) == 1 and abs(y1 - y2) == 2):
            return True
        return False


class Bishop(Piece):
    def __init__(self, color, position, player):
        super().__init__(color, position, player)
        self.type = "bishop"
        self.name = self.color + "_" + self.type + "_" + str(position[1])
        self.value = 3

    def possible_moves(self, coords_pieces, pieces_coords, player, name_piece):
        x1, y1 = self.position
        moves = []
        for i in range(1, 8):
            if self.valid_move(x1-i, y1+i, coords_pieces, pieces_coords, player, name_piece):
                moves.append((x1-i, y1+i))
            if self.valid_move(x1+i, y1+i, coords_pieces, pieces_coords, player, name_piece):
                moves.append((x1+i, y1+i))
            if self.valid_move(x1+i, y1-i, coords_pieces, pieces_coords, player, name_piece):
                moves.append((x1+i, y1-i))
            if self.valid_move(x1-i, y1-i, coords_pieces, pieces_coords, player, name_piece):
                moves.append((x1-i, y1-i))
        return moves

    def valid_move(self, x2, y2, coords_pieces, pieces_coords, player, name_piece):
        if not self.legal_move(x2, y2, coords_pieces, pieces_coords, player):
            return False
        x1, y1 = self.position
        if abs(x1 - x2) == abs(y1 - y2):
            # up and right movement
            if x1 < x2 and y1 > y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(x1 + i, y1 - i)]:
                        return False
            # down and right movement
            elif x1 < x2 and y1 < y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(x1 + i, y1 + i)]:
                        return False
            # up and left movement
            elif x1 > x2 and y1 > y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(x1 - i, y1 - i)]:
                        return False
            # down and left movement
            elif x1 > x2 and y1 < y2:
                for i in range(1, abs(x1 - x2)):
                    if coords_pieces[(x1 - i, y1 + i)]:
                        return False
            return True
        else:
            return False


class Queen(Piece):
    def __init__(self, color, position, player):
        super().__init__(color, position, player)
        self.type = "queen"
        self.name = self.color + "_" + self.type + "_" + str(position[1])
        self.value = 9

    def possible_moves(self, coords_pieces, pieces_coords, player, name_piece):
        rook = Rook(self.color, self.position, player)
        bishop = Bishop(self.color, self.position, player)
        moves = []

        moves.extend(bishop.possible_moves(coords_pieces, pieces_coords, player, name_piece))
        moves.extend(rook.possible_moves(coords_pieces, pieces_coords, player, name_piece))
        return moves

    def valid_move(self, x2, y2, coords_pieces, pieces_coords, player, name_piece):
        rook = Rook(self.color, self.position, player)
        bishop = Bishop(self.color, self.position, player)

        return rook.valid_move(x2, y2, coords_pieces, pieces_coords, player, name_piece) or \
            bishop.valid_move(x2, y2, coords_pieces, pieces_coords, player, name_piece)


class King(Piece):
    def __init__(self, color, position, player):
        super().__init__(color, position, player)
        self.type = "king"
        self.name = self.color + "_" + self.type + "_" + str(position[1])
        self.value = 3
        self.moved = False
        self.rooks = None

    def add_rooks(self, name_piece):
        rook_left = name_piece[f"{self.color}_rook_0"]
        rook_right = name_piece[f"{self.color}_rook_7"]
        assert rook_left and rook_right
        self.rooks = {0: rook_left, 1: rook_right}

    def possible_moves(self, coords_pieces, pieces_coords, player, name_piece):
        x1, y1 = self.position
        moves = []
        options = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1),
                   (0, -1), (-1, -1)]
        for x, y in options:
            if self.valid_move(x1+x, y1+y, coords_pieces, pieces_coords, player, name_piece):
                moves.append((x1+x, y1+y))
        return moves

    def valid_move(self, x2, y2, coords_pieces, pieces_coords, player, name_piece):
        if not self.legal_move(x2, y2, coords_pieces, pieces_coords, player):
            return False
        x1, y1 = self.position
        if max(abs(x1-x2), abs(y1-y2)) == 1:
            if not self.friend_here(x2, y2, coords_pieces):
                return True
        elif self.castle(x2, y2, coords_pieces, pieces_coords):
            return True
        return False

    def castle(self, x2, y2, coords_pieces, pieces_coords):
        x1, y1 = self.position

        diff = x2-x1
        if (abs(diff) == 2
                and not coords_pieces[(x1, y1 + int((diff / 2)))]
                and not coords_pieces[(x2, y2)]
                and not self.moved
                and not self.rooks[x1 < x2].moved)\
                and not self.my_king_checked(x1+int((diff/2)), y1, coords_pieces, pieces_coords):

            return True
        return False

    def checked(self, coords_pieces):
        # assume no checks
        check = False
        # check diagonals for pawns, queens or bishops
        i = 1
        x, y = self.position
        # up and right
        while 0 <= y-i <= 7 and 0 <= x+i <= 7:
            piece = coords_pieces[(x+i, y-i)]
            if piece:
                if piece.color != self.color and \
                        ((piece.type in {"bishop", "queen"}) or
                         (piece.type == "pawn" and i == 1 and self.player == 1)
                         or (piece.type == "king" and i == 1)):
                    check = True
                break
            i += 1
        # up and left
        i = 1
        while 0 <= y-i <= 7 and 0 <= x-i <= 7:
            piece = coords_pieces[(x-i, y-i)]
            if piece:
                if piece.color != self.color and \
                        ((piece.type in {"bishop", "queen"}) or
                         (piece.type == "pawn" and i == 1 and self.player == 1)
                         or (piece.type == "king" and i == 1)):
                    check = True
                break
            i += 1
        # down and right
        i = 1
        while 0 <= y+i <= 7 and 0 <= x+i <= 7:
            piece = coords_pieces[(x+i, y+i)]
            if piece:
                if piece.color != self.color and \
                        ((piece.type in {"bishop", "queen"}) or
                         (piece.type == "pawn" and i == 1 and self.player == 2)
                         or (piece.type == "king" and i == 1)):
                    check = True
                break
            i += 1
        # down and left
        i = 1
        while 0 <= y+i <= 7 and 0 <= x-i <= 7:
            piece = coords_pieces[(x-i, y+i)]
            if piece:
                if piece.color != self.color and \
                        ((piece.type in {"bishop", "queen"}) or
                         (piece.type == "pawn" and i == 1 and self.player == 2)
                         or (piece.type == "king" and i == 1)):
                    check = True
                break
            i += 1
        # check straight lines for rooks or queens
        # up
        i = 1
        while 0 <= y-i <= 7:
            piece = coords_pieces[(x, y-i)]
            if piece:
                if piece.color != self.color and \
                        ((piece.type in {"rook", "queen"} or
                         piece.type == "king" and i == 1)):
                    check = True
                break
            i += 1
        # down
        i = 1
        while 0 <= y+i <= 7:
            piece = coords_pieces[(x, y+i)] 
            if piece:
                if piece.color != self.color and \
                        ((piece.type in {"rook", "queen"} or
                         piece.type == "king" and i == 1)):
                    check = True
                break
            i += 1
        # right
        i = 1
        while 0 <= x+i <= 7:
            piece = coords_pieces[(x+i, y)]
            if piece:
                if piece.color != self.color and \
                        ((piece.type in {"rook", "queen"} or
                         piece.type == "king" and i == 1)):
                    check = True
                break
            i += 1
        # left
        i = 1
        while 0 <= x-i <= 7:
            piece = coords_pieces[(x-i, y)]
            if piece:
                if piece.color != self.color and \
                        ((piece.type in {"rook", "queen"} or
                         piece.type == "king" and i == 1)):
                    check = True
                break
            i += 1
        # check knight checks
        # up
        knight_positions = [(-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2),
                            (-2, -1), (-2, 1)]
        for i, j in knight_positions:
            piece = coords_pieces[(x+j, y-i)]
            if piece:
                if piece.type == "knight" and piece.color != self.color:
                    check = True
                    break
        return check
