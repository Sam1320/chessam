from tkinter import *
from utilities.images_dict import Images
from collections import defaultdict
from src.Pieces import *

# DONE: castling
# DONE: fix all that broke after great refactor

# TODO: verify double check
# TODO: stalemate
# TODO: en passant
# TODO: add scores
# TODO: add clocks
# TODO: reset button
# TODO: change pieces icons
# TODO: use either row and col or x and y but not both
# TODO: easy way to locate kings


class GameBoard(Frame):
    def __init__(self, parent, rows=8, columns=8, size=64, color1="white",
                 color2="gray"):

        super(GameBoard, self).__init__(master=parent)
        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.pieces_coords = defaultdict(lambda: None)
        self.coords_pieces = defaultdict(lambda: None)
        self.name_piece = defaultdict(lambda: None)
        self.images_dic = Images.load_images()
        self.check_label = Label(text="No checks", width=20)
        self.check_label.grid(row=2, column=1, pady=1)
        self.turn_label = Label(text="Turn: Player 1", width=20)
        self.select_label = Label(text="row:  col:  ", width=20)
        self.select_label.grid(row=2, column=2, pady=1)
        self.turn_label.grid(row=2, column=3, pady=1)
        canvas_width = columns * size
        canvas_height = rows * size
        self.selected = False
        self.selected_piece = None
        self.player = 1
        self.player_1_color = "white"
        self.check = False
        self.king_moved = {"white": False, "black": True}
        # 1 is right rook, 0 is left rook
        self.rook_moved = {1: False, 0: False}
        self.canvas = Canvas(self, borderwidth=0, highlightthickness=0,
                             width=canvas_width, height=canvas_height,
                             background="bisque")
        self.canvas.grid(row=0, columnspan=6, padx=2, pady=2)
        # This binding will cause a refresh if the user interactively
        # changes the window size
        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind("<Button-1>", self.select)

    @staticmethod
    def create_piece(color, piece_type, position, player):
        if piece_type == "pawn":
            piece = Pawn(color, position, player)
        elif piece_type == "rook":
            piece = Rook(color, position, player)
        elif piece_type == "bishop":
            piece = Bishop(color, position, player)
        elif piece_type == "knight":
            piece = Knight(color, position, player)
        elif piece_type == "queen":
            piece = Queen(color, position, player)
        elif piece_type == "king":
            piece = King(color, position, player)
        else:
            raise Exception(f"{piece_type} is not a valid piece_type.")
        assert piece
        return piece

    def add_piece(self, color, piece_type, player,  image, row, column):
        # Add a piece to the playing board'''
        piece = self.create_piece(color, piece_type, (row, column), player)
        self.canvas.create_image(0, 0, image=image, tags=(piece.name, "piece"),
                                 anchor="c")
        self.pieces_coords[piece] = piece.position
        self.name_piece[piece.name] = piece
        self.coords_pieces[piece.position] = piece


        x0 = (piece.position[1] * self.size) + int(self.size/2)
        y0 = (piece.position[0] * self.size) + int(self.size/2)
        self.canvas.coords(piece.name, x0, y0)

    def get_piece(self, name):
        for p in self.pieces_coords:
            if p.name == name:
                return p

    def place_piece(self, piece, position):

        y1, x1 = piece.position
        y2, x2 = position
        valid = piece.valid_move(x2, y2, self.coords_pieces,
                                 self.pieces_coords, self.player, self.name_piece)
        if valid:

            self.coords_pieces[(y1, x1)] = None
            # if target square is occupied then delete the taken piece
            if self.coords_pieces[(y2, x2)]:
                dead_piece = self.coords_pieces[(y2, x2)]
                # TODO: find optimal solution
                self.canvas.coords(dead_piece.name, -self.size, -self.size)
                # free previous square in coord_pieces dict
                self.pieces_coords[dead_piece] = None

            # en passant
            if piece.type =="pawn" and self.name_piece["en_passant"]:
                to_take = self.name_piece["en_passant"]
                y3, x3 = to_take.position
                if x3 == x2 and y3 == y1:
                    self.canvas.coords(to_take.name, -self.size, -self.size)
                    self.pieces_coords[to_take] = None

            # en passant possible next move
            if piece.type == "pawn" and abs(y1-y2) == 2:
                self.name_piece["en_passant"] = piece
            else:
                self.name_piece["en_passant"] = None


            # Pawn promotion
            if (y2 == 7 or y2 == 0) and piece.type == "pawn":
                self.pawn_promotion(piece, y2, x2)
            # Normal move
            else:
                self.pieces_coords[piece] = (y2, x2)
                self.coords_pieces[(y2, x2)] = piece
                piece.move(x2, y2)
                x0 = (x2 * self.size) + int(self.size/2)
                y0 = (y2 * self.size) + int(self.size/2)
                self.canvas.coords(piece.name, x0, y0)

            # Castling
            if piece.type == "king" and abs(x1-x2) == 2:
                rook_x = 7 if x1 < x2 else 0
                rook = self.get_piece(piece.color+"_rook_"+str(rook_x))
                new_rook_x = 5 if rook_x == 7 else 3
                rook_y = rook.position[0]
                self.pieces_coords[rook] = (rook_y, new_rook_x)
                self.coords_pieces[(rook_y, new_rook_x)] = rook
                rook.move(new_rook_x, rook_y)
                x0 = (new_rook_x * self.size) + int(self.size/2)
                y0 = (rook_y * self.size) + int(self.size/2)
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

    def king_checked(self, color):
        check = False
        for p in self.pieces_coords:
            if p:
                if p.color == color and p.type == "king":
                    check = p.checked(self.coords_pieces)
                    break
        return check

    def protect_possible(self, piece, x2, y2):
        return self.block_possible(piece, x2, y2) or \
               self.evade_possible() or \
               self.take_possible(x2, y2)

    def block_possible(self, piece, x2, y2):
        king = None
        for p in self.pieces_coords:
            if p:
                if p.color == self.opponent_color() and p.type == "king":
                    king = p
        king_y, king_x = king.position
        # determine the direction of the check
        up = True if king_y < y2 else False
        down = True if king_y > y2 else False
        left = True if king_x < x2 else False
        right = True if king_x > x2 else False

        block = None
        # can't block if it is one square away or if its a knight
        distance = max(abs(king_x-x2), abs(king_y-y2))
        if distance == 1 or piece.type == "knight":
            block = False
        else:
            for i in range(1, distance):
                if up and not (left or right):
                    x, y = x2, y2-i
                elif up and right:
                    x, y = x2+i, y2-i
                elif right and not (up or down):
                    x, y = x2+i, y2
                elif down and right:
                    x, y = x2+i, y2+i
                elif down and not (left or right):
                    x, y = x2, y2+i
                elif down and left:
                    x, y = x2-i, y2+i
                elif left and not (up or down):
                    x, y = x2-i, y2
                # up and left
                else:
                    x, y = x2-i, y2-i
                block = self.move_possible(x, y, self.opponent_color())
                if block:
                    break
        return block

    def evade_possible(self):
        evade = False
        king = None
        for piece in self.pieces_coords:
            if piece:
                if piece.color == self.opponent_color() and piece.type == "king":
                    king = piece
        king_y, king_x = king.position
        for i, j in [(1, 1), (1, -1), (-1, 1), (-1, -1),
                     (1, 0), (0, 1), (-1, 0), (0, -1)]:
            if not ((0 <= king_y+i <= 7) and (0 <= king_x+j <= 7)):
                continue
            taken = self.coords_pieces[(king_y+i, king_x+j)]
            if taken:
                if taken.color != self.opponent_color():
                    evade = not self.checked(king,
                                             king_x, king_y,
                                             king_x+j, king_y+i,
                                             self.opponent_color())
            else:
                evade = not self.checked(king,
                                         king_x, king_y,
                                         king_x + j, king_y + i,
                                         self.opponent_color())
            if evade:
                break
        return evade

    def take_possible(self, x2, y2):
        take = self.move_possible(x2, y2, self.opponent_color())
        return take

    def move_possible(self, x, y, color):
        block = False
        player = 1 if self.player_1_color == color else 2
        for piece, coords in self.pieces_coords.items():
            if not piece or not coords:
                continue
            if color == piece.color:
                block = piece.valid_move(x, y, self.coords_pieces,
                                         self.pieces_coords, player, self.name_piece)
                if block:
                    break
        return block

    def pawn_promotion(self, name, row, col):
        color = self.current_color()
        self.promote_queen_button = Button(
            image=self.images_dic[color + "_queen"],
            command=lambda: self.promote(name, "queen", row, col))
        self.promote_knight_button = Button(
            image=self.images_dic[color + "_knight"],
            command=lambda: self.promote(name, "knight", row, col))
        self.promote_rook_button = Button(
            image=self.images_dic[color + "_rook"],
            command=lambda: self.promote(name, "rook", row, col))
        self.promote_bishop_button = Button(
            image=self.images_dic[color + "_bishop"],
            command=lambda: self.promote(name, "bishop", row, col))
        self.promote_knight_button.grid(row=1, column=1, sticky="ew")
        self.promote_queen_button.grid(row=1, column=2, sticky="ew")
        self.promote_rook_button.grid(row=1, column=3, sticky="ew")
        self.promote_bishop_button.grid(row=1, column=4, sticky="ew")

    def refresh(self, event):
        # Redraw the board, possibly in response to window being resized
        xsize = int((event.width-1) / self.columns)
        ysize = int((event.height-1) / self.rows)
        self.size = min(xsize, ysize)
        self.canvas.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black",
                                             fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2
        for piece in self.pieces_coords:
            self.place_piece(piece, piece.position)
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")


    def setup_board(self):
        images = self.images_dic
        white_player = 1 if self.player_1_color == "white" else 2
        black_player = 2 if white_player == 1 else 1
        for c in range(self.columns):
            self.add_piece("white", "pawn", white_player, self.images_dic["white_pawn"], 6, c)
            self.add_piece("black", "pawn", black_player, images["black_pawn"], 1, c)
            if c == 0 or c == 7:
                self.add_piece("white", "rook", white_player, images["white_rook"], 7, c)
                self.add_piece("black", "rook", black_player, images["black_rook"], 0, c)
            if c == 1 or c == 6:
                self.add_piece("white", "knight", white_player, images["white_knight"], 7, c)
                self.add_piece("black", "knight",black_player, images["black_knight"], 0, c)
            if c == 2 or c == 5:
                self.add_piece("white", "bishop", white_player, images["white_bishop"], 7, c)
                self.add_piece("black", "bishop", black_player, images["black_bishop"], 0, c)
            if c == 3:
                self.add_piece("white", "queen", white_player, images["white_queen"], 7, c)
                self.add_piece("black", "queen", black_player, images["black_queen"], 0, c)
            if c == 4:
                self.add_piece("white", "king", white_player, images["white_king"], 7, c)
                self.add_piece("black", "king", black_player, images["black_king"], 0, c)

        # Kings track rooks to know if they can castle latter
        white_king = self.name_piece["white_king_4"]
        black_king = self.name_piece["black_king_4"]
        white_king.add_rooks(self.name_piece)
        black_king.add_rooks(self.name_piece)

    def coords_to_row_col(self, x, y):
        size = self.size
        if y < size:
            row = 0
        elif y < size*2:
            row = 1
        elif y < size*3:
            row = 2
        elif y < size*4:
            row = 3
        elif y < size*5:
            row = 4
        elif y < size*6:
            row = 5
        elif y < size*7:
            row = 6
        else:
            row = 7

        if x < size:
            col = 0
        elif x < size*2:
            col = 1
        elif x < size*3:
            col = 2
        elif x < size*4:
            col = 3
        elif x < size*5:
            col = 4
        elif x < size*6:
            col = 5
        elif x < size*7:
            col = 6
        else:
            col = 7
        return row, col

    def current_color(self):
        return "white" if self.player_1_color == "white" and \
                          self.player == 1 else "black"

    def opponent_color(self):
        return "black" if self.current_color() == "white" else "white"

    def checked(self, piece, x1, y1, x2, y2, color):
        # assume no check
        check = False
        # simulate move
        old_piece = self.coords_pieces[(y2, x2)]
        self.pieces_coords[old_piece] = None
        self.pieces_coords[piece] = (y2, x2)
        self.coords_pieces[(y1, x1)] = None
        self.coords_pieces[(y2, x2)] = piece
        piece.move(x2, y2)

        for p in self.pieces_coords:
            if p.color == color and p.type == "king":
                check = p.checked(self.coords_pieces)
                break

        # restore position
        self.coords_pieces[(y2, x2)] = old_piece
        self.pieces_coords[old_piece] = (y2, x2)
        self.coords_pieces[(y1, x1)] = piece
        self.pieces_coords[piece] = (y1, x1)
        piece.move(x1, y1)

        return check

    def promote(self, piece, new_type, row, col):
        self.canvas.coords(piece.name, -self.size, -self.size)

        color = self.opponent_color()
        player = 2 if self.player == 1 else 1
        new_piece = self.create_piece(color, new_type, (row, col), player)
        self.canvas.create_image(0, 0,
                                 image=self.images_dic[color+"_"+new_type],
                                 tags=(new_piece.name, "piece"),
                                 anchor="c")
        self.pieces_coords[new_piece] = (row, col)
        self.coords_pieces[(row, col)] = new_piece
        x0 = (col * self.size) + int(self.size / 2)
        y0 = (row * self.size) + int(self.size / 2)
        self.canvas.coords(new_piece.name, x0, y0)
        self.promote_queen_button.destroy()
        self.promote_knight_button.destroy()
        self.promote_bishop_button.destroy()
        self.promote_rook_button.destroy()


if __name__ == "__main__":
    root = Tk()
    board = GameBoard(root)
    #board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    board.grid(row=0, columnspan=6, padx=4, pady=4)
    board.setup_board()
    # Avoid window resizing
    root.resizable(0, 0)
    root.mainloop()
