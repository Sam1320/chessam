from tkinter import *
from utilities.images_dict import Images
from collections import defaultdict
from src.Pieces import *

# TODO: verify double check
# TODO: castling
# TODO: stalemate
# TODO: en passant
# TODO: add scores
# TODO: add clocks
# TODO: reset button
# TODO: change pieces icons
# TODO: create piece objects and delegate responsibilities
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

        self.canvas = Canvas(self, borderwidth=0, highlightthickness=0,
                             width=canvas_width, height=canvas_height,
                             background="bisque")
        self.canvas.grid(row=0, columnspan=6, padx=2, pady=2)

        # This binding will cause a refresh if the user interactively
        # changes the window size
        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind("<Button-1>", self.select)

    @staticmethod
    def create_piece(name, position):
        piece_type = name.split("_")[1]
        if piece_type == "pawn":
            piece = Pawn(name, position)
        elif piece_type == "rook":
            piece = Rook(name, position)
        elif piece_type == "bishop":
            piece = Bishop(name, position)
        elif piece_type == "knight":
            piece = Knight(name, position)
        elif piece_type == "Queen":
            piece = Queen(name, position)
        else:
            piece = King(name, position)
        return piece

    def add_piece(self, name, image, row, column):
        # Add a piece to the playing board'''
        self.canvas.create_image(0, 0, image=image, tags=(name, "piece"),
                                 anchor="c")
        piece = self.create_piece(name, (row, column))
        self.pieces_coords[piece] = piece.position
        self.coords_pieces[piece.position] = piece
        x0 = (piece.position[1] * self.size) + int(self.size/2)
        y0 = (piece.position[0] * self.size) + int(self.size/2)
        self.canvas.coords(piece.name, x0, y0)

    def place_piece(self, piece, position):

        y1, x1 = piece.position
        y2, x2 = position
        valid = piece.valid_move(x2, y2, self.coords_pieces,
                                 self.pieces_coords, self.player)
        if valid:
            self.coords_pieces[(y1, x1)] = None
            # if target square is occupied then delete the taken piece
            if self.coords_pieces[(y2, x2)]:
                dead_piece = self.coords_pieces[(y2, x2)]
                # TODO: find optimal solution
                self.canvas.coords(dead_piece, -self.size, -self.size)
                # free previous square in coord_pieces dict
                self.pieces_coords[dead_piece] = None

            if (y2 == 7 or y2 == 0) and piece.name == "pawn":
                self.pawn_promotion(piece, y2, x2)
            else:
                self.pieces_coords[piece] = (y2, x2)
                self.coords_pieces[(y2, x2)] = piece
                x0 = (x2 * self.size) + int(self.size/2)
                y0 = (y2 * self.size) + int(self.size/2)
                self.canvas.coords(piece.name, x0, y0)

            #######
            if self.king_checked(self.opponent_color()):
                if not self.protect_possible(piece, x2, y2):
                    self.check_label.config(text="CHECKMATE!")
                else:
                    self.check = True
                    self.check_label.config(text="CHECK!")
            else:
                self.check_label.config(text="no checks")

            ######

        return valid

    def king_checked(self, color):
        check = False
        for p in self.pieces_coords:
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
        for piece in self.pieces_coords:
            if piece.color == self.opponent_color() and piece.type == "king":
                king = piece
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
        for piece, coords in self.pieces_coords.items():
            if not piece or not coords:
                continue
            if color == piece.color:
                block = piece.valid_move(x, y, self.coords_pieces)
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
                self.turn_label.config(text="Turn: Player " +str(self.player))
        else:
            row, col = self.coords_to_row_col(e.x, e.y)
            x1 = (col * self.size)
            y1 = (row * self.size)
            x2 = x1 + self.size
            y2 = y1 + self.size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="black",
                                         fill="red", tags="selected")
            self.select_label.config(text="row: "+str(row)+" col: "+str(col))
            self.canvas.tag_raise("piece")
            self.selected = True
            self.selected_piece = self.coords_pieces[(row, col)]

    def setup_board(self):
        images = self.images_dic
        for c in range(self.columns):
            self.add_piece("white_pawn_" + str(c), self.images_dic["white_pawn"], 6, c)
            self.add_piece("black_pawn_" + str(c), images["black_pawn"], 1, c)
            if c == 0 or c == 7:
                self.add_piece("white_rook_" + str(c), images["white_rook"], 7, c)
                self.add_piece("black_rook_" + str(c), images["black_rook"], 0, c)
            if c == 1 or c == 6:
                self.add_piece("white_knight_" + str(c), images["white_knight"], 7, c)
                self.add_piece("black_knight_" + str(c), images["black_knight"], 0, c)
            if c == 2 or c == 5:
                self.add_piece("white_bishop_" + str(c), images["white_bishop"], 7, c)
                self.add_piece("black_bishop_" + str(c), images["black_bishop"], 0, c)
            if c == 3:
                self.add_piece("white_queen", images["white_queen"], 7, c)
                self.add_piece("black_queen", images["black_queen"], 0, c)
            if c == 4:
                self.add_piece("white_king", images["white_king"], 7, c)
                self.add_piece("black_king", images["black_king"], 0, c)

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
        piece.set_position((y2, x2))

        for p in self.pieces_coords:
            if p.color == color and p.type == "king":
                check = p.checked(self.coords_pieces)
                break

        # restore position
        self.coords_pieces[(y2, x2)] = old_piece
        self.pieces_coords[old_piece] = (y2, x2)
        self.coords_pieces[(y1, x1)] = piece
        self.pieces_coords[piece] = (y1, x1)
        piece.set_position((y1, x1))

        return check

    def promote(self, name, new_type, row, col):
        self.canvas.coords(name, -self.size, -self.size)

        color = "white" if self.current_color() == "black" else "black"
        new_name = color+"_"+new_type+"_promoted_"+str(row)+str(col)
        self.canvas.create_image(0, 0,
                                 image=self.images_dic[color+"_"+new_type],
                                 tags=(new_name, "piece"),
                                 anchor="c")
        self.pieces_coords[new_name] = (row, col)
        self.coords_pieces[(row, col)] = new_name
        x0 = (col * self.size) + int(self.size / 2)
        y0 = (row * self.size) + int(self.size / 2)
        self.canvas.coords(new_name, x0, y0)
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
