from tkinter import *
from utilities.images_dict import Images
from collections import defaultdict

# TODO: checkmate
    # TODO: king cant take checking bishop
# TODO: stalemate
# TODO: en passant
# TODO: add scores
# TODO: add clocks
# TODO: reset button
# TODO: change pieces icons


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

    def add_piece(self, name, image, row=0, column=0):
        # Add a piece to the playing board'''
        self.canvas.create_image(0, 0, image=image, tags=(name, "piece"),
                                 anchor="c")
        self.place_piece(name, row, column)

    def place_piece(self, name, row, col):

        old_coords = self.pieces_coords[name]
        valid = self.valid_move(name, old_coords,(row, col))
        if valid:
            # if target square is occupied then delete the taken piece
            if self.coords_pieces[(row, col)]:
                dead_piece = self.coords_pieces[(row, col)]
                # TODO: find optimal solution
                self.canvas.coords(dead_piece, -self.size, -self.size)
                self.pieces_coords[dead_piece] = None
            # free previous square in coord_pieces dict
            if old_coords:
                if self.checked(name, old_coords[1], old_coords[0], col, row, self.opponent_color()):
                    #self.do_check()
                    self.check = True
                    self.check_label.config(text="CHECK MOTHEFUCKER!")
                else:
                    self.check_label.config(text="no checks")

                self.coords_pieces[old_coords] = None
            if (row == 7 or row == 0) and name.split("_")[1] == "pawn":
                self.pawn_promotion(name, row, col)
            else:
                self.pieces_coords[name] = (row, col)
                self.coords_pieces[(row, col)] = name
                x0 = (col * self.size) + int(self.size/2)
                y0 = (row * self.size) + int(self.size/2)
                self.canvas.coords(name, x0, y0)


        return valid

    def do_check(self):
        self.check = True
        self.check_label.config(text="CHECK MOTHEFUCKER!")

    def undo_check(self):
        self.check = False
        self.check_label.config(text="")

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
        for name in self.pieces_coords:
            self.place_piece(name, self.pieces_coords[name][0], self.pieces_coords[name][1])
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")

    def select(self, e):
        # TODO: fix selecting empty square bug
        if self.selected:
            row, col = self.coords_to_row_col(e.x, e.y)
            self.canvas.delete("selected")
            valid = self.place_piece(self.selected_piece, row, col)
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

    # def move(self, e):
    #     self.canvas.coords("white_pawn_3", e.x, e.y)

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

    def valid_move(self, name, old_coords, new_coords):
        piece_type = name.split("_")[1]
        piece_color = name.split("_")[0]
        # Allow all moves that set up the board
        if not old_coords:
            return True
        # Only allow turn based moves
        if (piece_color == self.player_1_color and self.player != 1) or \
                (piece_color != self.player_1_color and self.player == 1):
            return False
        y1, x1 = old_coords[0], old_coords[1]
        y2, x2 = new_coords[0], new_coords[1]
        # Own pieces can't be taken
        take = True if self.coords_pieces[(y2, x2)] else False
        if take:
            color_taken = self.coords_pieces[(y2, x2)].split("_")[0]
            if self.player == 1 and self.player_1_color == color_taken or \
                    self.player == 2 and self.player_1_color != color_taken:
                return False
        # The move can't result in your own king being checked
        color = self.current_color()
        if self.checked(name, x1, y1, x2, y2, color):
            return False
        if piece_type == "pawn":
            return self.valid_pawn_move(x1, y1, x2, y2, take)
        elif piece_type == "knight":
            return self.valid_knight_move(x1, y1, x2, y2)
        elif piece_type == "bishop":
            return self.valid_bishop_move(x1, y1, x2, y2)
        elif piece_type == "rook":
            return self.valid_rook_move(x1, y1, x2, y2)
        # TODO: refactor for consistency
        elif piece_type == "queen":
            if self.valid_rook_move(x1, y1, x2, y2) or \
                    self.valid_bishop_move(x1, y1, x2, y2):
                return True
        elif piece_type == "king":
            return self.valid_king_move(x1, y1, x2, y2)

        return False
    def check(self, name, old_coords, new_coords):
        # piece_type = name.split("_")[1]
        # piece_color = name.split("_")[0]
        # y1, x1 = old_coords[0], old_coords[1]
        # y2, x2 = new_coords[0], new_coords[1]
        # if piece_type == "queen":
        pass


    def valid_rook_move(self, x1, y1, x2, y2):
        if (x1 == x2 or y1 == y2) and (x1 != x2 or y1 != y2):
            # upward movement
            if x1 == x2 and y1 > y2:
                for i in range(1, abs(y1 - y2)):
                    if self.coords_pieces[(y1 - i, x1)]:
                        return False
            # downward movement
            elif x1 == x2 and y1 < y2:
                for i in range(1, abs(y1 - y2)):
                    if self.coords_pieces[(y1 + i, x1)]:
                        return False
            # rightward movement
            elif x1 < x2 and y1 == y2:
                for i in range(1, abs(x1 - x2)):
                    if self.coords_pieces[(y1, x1 + i)]:
                        return False
            # leftward movement
            elif x1 > x2 and y1 == y2:
                for i in range(1, abs(x1 - x2)):
                    if self.coords_pieces[(y1, x1 - i)]:
                        return False
            return True
        else:
            return False

    def valid_bishop_move(self, x1, y1, x2, y2):
        if abs(x1 - x2) == abs(y1 - y2):
            # up and right movement
            if x1 < x2 and y1 > y2:
                for i in range(1, abs(x1 - x2)):
                    if self.coords_pieces[(y1 - i, x1 + i)]:
                        return False
            # down and right movement
            elif x1 < x2 and y1 < y2:
                for i in range(1, abs(x1 - x2)):
                    if self.coords_pieces[(y1 + i, x1 + i)]:
                        return False
            # up and left movement
            elif x1 > x2 and y1 > y2:
                for i in range(1, abs(x1 - x2)):
                    if self.coords_pieces[(y1 - i, x1 - i)]:
                        return False
            # down and left movement
            elif x1 > x2 and y1 < y2:
                for i in range(1, abs(x1 - x2)):
                    if self.coords_pieces[(y1 + i, x1 - i)]:
                        return False
            return True
        else:
            return False

    def valid_pawn_move(self, x1, y1, x2, y2, take):
        player = self.player
        # One move forward
        if not take and ((x1 == x2 and y1 == y2 + 1 and player == 1) or
                         (x1 == x2 and y1 == y2 - 1 and player == 2)):
            return True
        # Two moves forward and first move
        elif not take and ((y1 == 1 or y1 == 6) and
                           ((x1 == x2 and y1 == y2 + 2 and player == 1) or
                            (x1 == x2 and y1 == y2 - 2 and player == 2))):
            return True
        # One square diagonal and take
        elif take and ((abs(x1 - x2) == 1 and y1 == y2 + 1 and player == 1) or
                       (abs(x1 - x2) == 1 and y1 == y2 - 1 and player == 2)):
            return True
        return False

    def valid_knight_move(self, x1, y1, x2, y2):
        if (abs(x1 - x2) == 2 and abs(y1 - y2) == 1) or \
                (abs(x1 - x2) == 1 and abs(y1 - y2) == 2):
            return True

    def valid_king_move(self, x1, y1, x2, y2):
        if abs(x1-x2) == 1 and abs(y1-y2) == 1 or \
                x1 == x2 and abs(y1-y2) == 1 or \
                y1 == y2 and abs(x1-x2) == 1:
            return True
        else:
            return False

    def checked(self, name, x1, y1, x2, y2, color):
        # assume no check
        check = False
        # save taken piece
        old_piece = self.coords_pieces[(y2, x2)]
        # assign new coords to pieces
        self.pieces_coords[old_piece] = None
        self.pieces_coords[name] = (y2, x2)
        # free former square
        self.coords_pieces[(y1, x1)] = None
        # place piece
        self.coords_pieces[(y2, x2)] = name
        # TODO: Fix logic
        # find out kings position
        king_y, king_x = tuple(self.pieces_coords[color+"_"+"king"])

        # check diagonals for pawns, queens or bishops
        i = 1
        # up and right
        while 0 <= king_y-i <= 7 and 0 <= king_x+i <= 7:
            piece = self.coords_pieces[(king_y-i, king_x+i)]
            if piece:
                piece_color = piece.split("_")[0]
                piece_type = piece.split("_")[1]
                if piece_color == color or \
                   piece_type in {"rook", "knight"} or  \
                        piece_type == "pawn" and i > 1 or \
                        piece_type == "king" and i > 1:
                    break
                else:
                    if (piece_type in {"bishop", "queen"}) or \
                       (piece_type == "pawn" and i == 1) or \
                       (piece_type == "king" and i == 1):
                        check = True
            i += 1
        # up and left
        i = 1
        while 0 <= king_y-i <= 7 and 0 <= king_x-i <= 7:
            piece = self.coords_pieces[(king_y-i, king_x-i)]
            if piece:
                piece_color = piece.split("_")[0]
                piece_type = piece.split("_")[1]
                if piece_color == color or \
                   piece_type in {"rook", "knight"} or  \
                        piece_type == "pawn" and i > 1 or \
                        piece_type == "king" and i > 1:
                    break
                else:
                    if (piece_type in {"bishop", "queen"}) or \
                       (piece_type == "pawn" and i == 1) or \
                       (piece_type == "king" and i == 1):
                        check = True
            i += 1
        # down and right
        i = 1
        while 0 <= king_y+i <= 7 and 0 <= king_x+i <= 7:
            piece = self.coords_pieces[(king_y+i, king_x+i)]
            if piece:
                piece_color = piece.split("_")[0]
                piece_type = piece.split("_")[1]
                if piece_color == color or \
                   piece_type in {"rook", "knight"} or  \
                        piece_type == "pawn" and i > 1 or \
                        piece_type == "king" and i > 1:
                    break
                else:
                    if (piece_type in {"bishop", "queen"}) or \
                       (piece_type == "king" and i == 1):
                        check = True
            i += 1
        # down and left
        i = 1
        while 0 <= king_y+i <= 7 and 0 <= king_x-i <= 7:
            piece = self.coords_pieces[(king_y+i, king_x-i)]
            if piece:
                piece_color = piece.split("_")[0]
                piece_type = piece.split("_")[1]
                if piece_color == color or \
                   piece_type in {"rook", "knight"} or  \
                        piece_type == "pawn" and i > 1 or \
                        piece_type == "king" and i > 1:
                    break
                else:
                    if (piece_type in {"bishop", "queen"}) or \
                       (piece_type == "king" and i == 1):
                        check = True
            i += 1
        # check straight lines for rooks or queens
        # up
        i = 1
        while 0 <= king_y-i <= 7:
            piece = self.coords_pieces[(king_y-i, king_x)]
            if piece:
                piece_color = piece.split("_")[0]
                piece_type = piece.split("_")[1]
                if piece_color == color or piece_type not in {"rook", "queen"}:
                    break
                else:
                    if piece_type in {"rook", "queen"} or \
                       piece_type == "king" and i == 1:
                        check = True
            i += 1
        # down
        i = 1
        while 0 <= king_y+i <= 7:
            piece = self.coords_pieces[(king_y+i, king_x)]
            if piece:
                piece_color = piece.split("_")[0]
                piece_type = piece.split("_")[1]
                if piece_color == color or (piece_type not in {"rook", "queen"}):
                    break
                else:
                    if piece_type in {"rook", "queen"} or \
                       piece_type == "king" and i == 1:
                        check = True
            i += 1
        # right
        i = 1
        while 0 <= king_x+i <= 7:
            piece = self.coords_pieces[(king_y, king_x+i)]
            if piece:
                piece_color = piece.split("_")[0]
                piece_type = piece.split("_")[1]
                if piece_color == color or (piece_type not in {"rook", "queen"}):
                    break
                else:
                    if piece_type in {"rook", "queen"} or \
                       piece_type == "king" and i == 1:
                        check = True
            i += 1
        # left
        i = 1
        while 0 <= king_x-i <= 7:
            piece = self.coords_pieces[(king_y, king_x-i)]
            if piece:
                piece_color = piece.split("_")[0]
                piece_type = piece.split("_")[1]
                if piece_color == color or (piece_type not in {"rook", "queen"}):
                    break
                else:
                    if piece_type in {"rook", "queen"} or \
                       piece_type == "king" and i == 1:
                        check = True
            i += 1
        # check knight checks
        # up
        p1 = self.coords_pieces[(king_y-2, king_x+1)]
        p2 = self.coords_pieces[(king_y-2, king_x-1)]
        # right
        p3 = self.coords_pieces[(king_y+1, king_x+2)]
        p4 = self.coords_pieces[(king_y-1, king_x+2)]
        # down
        p5 = self.coords_pieces[(king_y+2, king_x-1)]
        p6 = self.coords_pieces[(king_y+2, king_x+1)]
        # left
        p7 = self.coords_pieces[(king_y+1, king_x-2)]
        p8 = self.coords_pieces[(king_y-1, king_x-2)]
        opp_king_color = "white" if color == "black" else "black"
        if opp_king_color+"_"+"knight" in str(p1)+str(p2)+str(p3)+str(p4)+str(p5) +\
                str(p6)+str(p7)+str(p8):
            check = True

        # restore position
        self.coords_pieces[(y2, x2)] = old_piece
        self.pieces_coords[old_piece] = (y2, x2)
        self.coords_pieces[(y1, x1)] = name
        self.pieces_coords[name] = (y1, x1)

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
