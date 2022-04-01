import subprocess

import sys
import subprocess
import time
import os
from tkinter import *
import glob
import env
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", f"{env.base_path}/requirements.txt"])

import chess
import chess.engine

from src import gui
from src.board_functions import *



# TODO: Store game states to be able to undo
# TODO: verify double check
# TODO: add clocks
# TODO: reset button
# TODO: change pieces icons

# DONE: implement alpha beta prunning
# DONE: minimax not working properly (making uneven piece trades)
# DONE: stalemate
# DONE: add scores
# DONE: one_step bot doesnt take en passant
# DONE: fix selecting empty square bug
# DONE: attacking bot doesnt take en passant
# DONE: add castling and en passant as possible moves
# DONE: Long castle
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
    """Class used to store the game state information and display the board.

    Attributes
    ------
    bot: str
        type of bot to play against. {n_step, random, random_attack, stockfish}
    steps: int
        number of steps to look ahead. (depth of the minimax tree search)
    """
    def __init__(self, parent, bot='n_step', steps=1):
        super(HumanBot, self).__init__(parent)

        stockfish_exec = glob.glob(os.path.join(env.base_path, 'stockfish*'))[0]
        stockfish_path = os.path.join(env.base_path, stockfish_exec)

        self.bot = bot
        self.steps = steps
        if self.bot == 'stockfish':
            self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
            self.limit = chess.engine.Limit(time=.5)

    def promotion(self, piece, x, y):
        """Triggers different pawn promotion methods depending if the player is human or bot."""
        if self.player == 1:
            self.pawn_promotion(piece, x, y)
        else:
            # in the current version the bot always promotes to a queen
            self.promote_bot(piece, "queen", x, y)

    def promote_bot(self, piece, new_type, x, y):
        """Automatic bot promotion and game state update."""
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

    def move_player2(self):
        """Plays a move based on the bot selected and current board state."""

        # store board state in denser representation to search the game tree
        node = {"pieces_coords": self.pieces_coords,
                "coords_pieces": self.coords_pieces,
                "name_piece": self.name_piece,
                "player": self.player,
                "turn": self.player,
                "game_over": self.game_over,
                "current_color": self.current_color(),
                "move_count": self.move_count}

        if self.bot == 'stockfish':
            fen = board_to_FEN(node)
            board = chess.Board(fen)
            result = self.engine.play(board, self.limit)
            piece_location, move = move_to_piece_move(str(result.move))
            piece = self.coords_pieces[piece_location]

        elif self.bot == 'random':
            piece, move = random_move(node)
        elif self.bot == 'random_attack':
            piece, move = random_attack(node)
        else:
            piece, move = n_step_lookahead(node, self.steps)
        self.place_piece(piece, move)

    def select(self, e):
        """This function gets called when the user clicks on the board. It highlights the selected square and also all
        the valid squares where the selected piece can be placed. After the user places the piece the bot is activated
        and the response move is played."""
        if self.selected:
            x, y = self.coords_to_col_row(e.x, e.y)
            self.canvas.delete("selected")
            valid = self.place_piece(self.selected_piece, (x, y))
            self.selected_piece = None
            self.selected = False
            if valid and not self.game_over:
                self.player = 2 if self.player == 1 else 1
                start = time.perf_counter()
                # play bot move
                self.move_player2()
                self.move_count += 1
                elapsed = time.perf_counter() - start
                print(elapsed)
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
        """Draws a rectangle on the coordinates specified in the 'moves' list."""
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
    board = HumanBot(root, bot='stockfish', steps=3)
    board.grid(row=0, columnspan=6, padx=4, pady=4)
    board.setup_board()
    # Avoid window resizing
    root.resizable(0, 0)
    root.mainloop()
