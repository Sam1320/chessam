from src import gui
from tkinter import *
import random

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
            # self.select_label.config(text="row: "+str(row)+" col: "+str(col))
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
