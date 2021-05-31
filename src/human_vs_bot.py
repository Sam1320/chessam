from src import gui
from tkinter import *
import random

# TODO: bot doesnt take en passant
# TODO: Store game states to be able to undo
# TODO: add castling and en passant as possible moves
# TODO: verify double check
# TODO: stalemate
# TODO: add scores
# TODO: add clocks
# TODO: reset button
# TODO: change pieces icons
# DONE: bug when promoting against bot
# DONE: FIX BOT QUEEN MOVING LIKE CRAZY
# DONE: castling
# DONE: fix all that broke after great refactor
# DONE: create abstract gui class and different guis for each type of game
# DONE: automate bot piece promotion selection
# DONE: en passant
# DONE: easy way to locate kings
# DONE: use either row and col or x and y but not both



class HumanBot(gui.GameBoard):
    def __init__(self, parent):
        super(HumanBot, self).__init__(parent)
        self.type = "human_vs_bot"

    def promotion(self, piece, x, y):
        if self.player == 1:
            self.pawn_promotion(piece, x, y)
        else:
            self.promote_bot(piece, "queen", x, y)

    def promote_bot(self, piece, new_type, x, y):
        self.canvas.coords(piece.name, -self.size, -self.size)
        piece.taken = True
        player = 2 if self.player == 1 else 1
        new_piece = self.create_piece(piece.color, new_type, (x, y), player)
        self.canvas.create_image(0, 0,
                                 image=self.images_dic[piece.color+"_"+new_type],
                                 tags=(new_piece.name, "piece"),
                                 anchor="c")
        self.pieces_coords[new_piece] = (x, y)
        self.coords_pieces[(x, y)] = new_piece
        x0 = (x * self.size) + int(self.size / 2)
        y0 = (y * self.size) + int(self.size / 2)
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
            return piece, move

    def available_attacks(self):
        possible_moves = self.available_moves()
        attacking_moves = {}
        if possible_moves:
            for piece, moves in possible_moves.items():
                attacks = []
                for move in moves:
                    if self.coords_pieces[move]:
                        attacks.append(move)
                    elif self.check_en_passant(piece, move[0], move[1]):
                        attacks.append(move)
                if attacks:
                    attacking_moves[piece] = attacks
        return attacking_moves

    def random_attack(self):
        attacking_moves = self.available_attacks()
        if attacking_moves:
            piece = random.choice(list(attacking_moves.keys()))
            move = random.choice(attacking_moves[piece])
            return piece, move
        return self.random_move()

    def move_player2(self):
            # piece, move = self.random_move()
            piece, move = self.random_attack()
            self.place_piece(piece, move)

    def select(self, e):
        # TODO: fix selecting empty square bug
        if self.selected:
            x, y = self.coords_to_col_row(e.x, e.y)
            self.canvas.delete("selected")
            valid = self.place_piece(self.selected_piece, (x, y))
            self.selected_piece = None
            self.selected = False
            if valid:
                self.player = 2 if self.player == 1 else 1
                self.move_player2()
                self.player = 2 if self.player == 1 else 1
                self.turn_label.config(text="Turn: Player " +str(self.player))
        else:
            x, y = self.coords_to_col_row(e.x, e.y)
            x1 = (x * self.size)
            y1 = (y * self.size)
            x2 = x1 + self.size
            y2 = y1 + self.size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="black",
                                         fill="red", tags="selected")
            self.canvas.tag_raise("piece")
            piece = self.coords_pieces[(x, y)]
            if piece:
                self.selected = True
                self.selected_piece = piece
                pos_moves = piece.possible_moves(self.coords_pieces, self.pieces_coords, self.player, self.name_piece)
                self.mark_possible_moves(pos_moves)

    def mark_possible_moves(self, moves):
        for x, y in moves:
            x1 = x * self.size
            y1 = y * self.size
            x2 = x1 + self.size
            y2 = y1 + self.size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="black",
                                         fill="red", tags="selected")
            self.canvas.tag_raise("piece")

if __name__ == "__main__":
    root = Tk()
    board = HumanBot(root)
    board.grid(row=0, columnspan=6, padx=4, pady=4)
    board.setup_board()
    # Avoid window resizing
    root.resizable(0, 0)
    root.mainloop()
