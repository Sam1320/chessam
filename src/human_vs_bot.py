from src import gui
from tkinter import *
import random

# TODO: bot doesnt take en passant
# TODO: bug when promoting against bot
# TODO: Store game states to be able to undo
# TODO: FIX BOT QUEEN MOVING LIKE CRAZY
# DONE: castling
# DONE: fix all that broke after great refactor
# TODO: create abstract gui class and different guis for each type of game
# TODO: automate bot piece promotion selection
# TODO: add castling and en passant as possible moves
# TODO: verify double check
# TODO: stalemate
# TODO: en passant
# TODO: add scores
# TODO: add clocks
# TODO: reset button
# TODO: change pieces icons
# TODO: use either row and col or x and y but not both
# TODO: easy way to locate kings


class HumanBot(gui.GameBoard):

    def place_piece(self, piece, position):

        y1, x1 = piece.position
        y2, x2 = position
        valid = piece.valid_move(x2, y2, self.coords_pieces,
                                 self.pieces_coords, self.player,
                                 self.name_piece)
        if valid:

            self.coords_pieces[(y1, x1)] = None
            # if target square is occupied then delete the taken piece
            if self.coords_pieces[(y2, x2)]:
                dead_piece = self.coords_pieces[(y2, x2)]
                # TODO: find optimal solution
                self.canvas.coords(dead_piece.name, -self.size, -self.size)
                # free previous square in coord_pieces dict
                self.pieces_coords[dead_piece] = None
                dead_piece.taken = True

            # en passant
            if piece.type == "pawn" and self.name_piece["en_passant"]:
                to_take = self.name_piece["en_passant"]
                y3, x3 = to_take.position
                if x3 == x2 and y3 == y1:
                    self.canvas.coords(to_take.name, -self.size, -self.size)
                    self.pieces_coords[to_take] = None

            # en passant possible next move
            if piece.type == "pawn" and abs(y1 - y2) == 2:
                self.name_piece["en_passant"] = piece
            else:
                self.name_piece["en_passant"] = None

            # Pawn promotion
            if (y2 == 7 or y2 == 0) and piece.type == "pawn":
                if self.player == 1:
                    self.pawn_promotion(piece, y2, x2)
                else:
                    self.promote(piece, "queen", y2, x2)

            # Normal move
            else:
                self.pieces_coords[piece] = (y2, x2)
                self.coords_pieces[(y2, x2)] = piece
                piece.move(x2, y2)
                x0 = (x2 * self.size) + int(self.size / 2)
                y0 = (y2 * self.size) + int(self.size / 2)
                self.canvas.coords(piece.name, x0, y0)

            # Castling
            if piece.type == "king" and abs(x1 - x2) == 2:
                rook_x = 7 if x1 < x2 else 0
                rook = self.get_piece(piece.color + "_rook_" + str(rook_x))
                new_rook_x = 5 if rook_x == 7 else 3
                rook_y = rook.position[0]
                self.pieces_coords[rook] = (rook_y, new_rook_x)
                self.coords_pieces[(rook_y, new_rook_x)] = rook
                rook.move(new_rook_x, rook_y)
                x0 = (new_rook_x * self.size) + int(self.size / 2)
                y0 = (rook_y * self.size) + int(self.size / 2)
                self.canvas.coords(rook.name, x0, y0)

            # Checks
            if self.king_checked(self.opponent_color()):
                if not self.protect_possible(piece, x2, y2):
                    self.check_label.config(text="CHECKMATE!")
                else:
                    self.check = True
                    self.check_label.config(text="CHECK!")
            else:
                self.check_label.config(text="no checks")

        return valid

    def promote(self, piece, new_type, row, col):
        self.canvas.coords(piece.name, -self.size, -self.size)

        player = 2 if self.player == 1 else 1
        piece.taken = True
        new_piece = self.create_piece(piece.color, new_type, (row, col), player)
        self.canvas.create_image(0, 0,
                                 image=self.images_dic[piece.color+"_"+new_type],
                                 tags=(new_piece.name, "piece"),
                                 anchor="c")
        self.pieces_coords[new_piece] = (row, col)
        self.coords_pieces[(row, col)] = new_piece
        x0 = (col * self.size) + int(self.size / 2)
        y0 = (row * self.size) + int(self.size / 2)
        self.canvas.coords(new_piece.name, x0, y0)

    def available_moves(self):
        possible_moves = {}
        for p in self.pieces_coords:
            if p: #something weird happening when castling line could be removed
                if not p.taken and p.color == self.current_color():
                    moves = p.possible_moves(
                        coords_pieces=self.coords_pieces,
                        pieces_coords=self.pieces_coords,
                        name_piece=self.name_piece,
                        player=self.player)
                    if moves:
                        possible_moves[p] = moves
        return possible_moves

    def random_move(self):
        possible_moves = self.available_moves()
        if possible_moves:
            piece = random.choice(list(possible_moves.keys()))
            move = random.choice(possible_moves[piece])
            # TODO: FIX this for fucks sake
            move = (move[1], move[0])
            return piece, move

    def available_attacks(self):
        possible_moves = self.available_moves()
        attacking_moves = {}
        if possible_moves:
            for piece, moves in possible_moves.items():
                # TODO: JUST USE x and y and NOT row and col
                attacks = [i for i in moves if
                           self.coords_pieces[(i[1], i[0])]]
                if attacks:
                    attacking_moves[piece] = attacks
        return attacking_moves

    def random_attack(self):
        attacking_moves = self.available_attacks()
        if attacking_moves:
            piece = random.choice(list(attacking_moves.keys()))
            move = random.choice(attacking_moves[piece])
            # TODO: JUST USE x and y and NOT row and col
            move = (move[1], move[0])
            return piece, move
        return self.random_move()

    def move_player2(self):
            # piece, move = self.random_move()
            piece, move = self.random_attack()
            self.place_piece(piece, move)

    def select(self, e):
        # TODO: fix selecting empty square bug
        if self.selected:
            row, col = self.coords_to_row_col(e.x, e.y)
            self.canvas.delete("selected")
            valid = self.place_piece(self.selected_piece, (row, col))
            self.selected_piece = None
            self.selected = False
            if valid:
                self.player = 2 if self.player == 1 else 1
                self.move_player2()
                self.player = 2 if self.player == 1 else 1
                self.turn_label.config(text="Turn: Player " +str(self.player))
        else:
            row, col = self.coords_to_row_col(e.x, e.y)
            x1 = (col * self.size)
            y1 = (row * self.size)
            x2 = x1 + self.size
            y2 = y1 + self.size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="black",
                                         fill="red", tags="selected")
            self.canvas.tag_raise("piece")
            piece = self.coords_pieces[(row, col)]
            if piece:
                self.selected = True
                self.selected_piece = piece


if __name__ == "__main__":
    root = Tk()
    board = HumanBot(root)
    board.grid(row=0, columnspan=6, padx=4, pady=4)
    board.setup_board()
    # Avoid window resizing
    root.resizable(0, 0)
    root.mainloop()
