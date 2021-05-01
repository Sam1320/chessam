from tkinter import *
from utilities.images_dict import Images
from src.Pieces import *


class GameBoard(Frame):
    def __init__(self, parent, rows=8, columns=8, size=64, color1="white",
                 color2="gray"):

        super(GameBoard, self).__init__(master=parent)
        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.pieces_coords = {}
        self.coords_pieces = {}
        self.images_dic = Images.load_images()
        self.coords_label = Label(text="")
        self.coords_label.pack(side="bottom", pady=2)
        self.select_label = Label(text="row:  col:  ")
        self.select_label.pack(side="bottom", pady=2)
        canvas_width = columns * size
        canvas_height = rows * size
        self.selected = False
        self.selected_piece = None

        self.canvas = Canvas(self, borderwidth=0, highlightthickness=0,
                             width=canvas_width, height=canvas_height,
                             background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        # This binding will cause a refresh if the user interactively
        # changes the window size
        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind("<Button-1>", self.select)
        self.canvas.bind("<Motion>", self.move)

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

    def add_piece(self, name, image, row=0, column=0):
        # Add a piece to the playing board'''
        self.canvas.create_image(0, 0, image=image, tags=(name, "piece"),
                                 anchor="c")
        piece = self.create_piece(name, (row, column))
        self.place_piece(piece, (row, column))

    def place_piece(self, piece, position):
        # Place a piece at the given row/column
        piece.set_position(position)
        self.pieces_coords[piece] = piece.position
        self.coords_pieces[piece.position] = piece
        x0 = (piece.position[1] * self.size) + int(self.size/2)
        y0 = (piece.position[0] * self.size) + int(self.size/2)
        self.canvas.coords(piece.name, x0, y0)

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
        if self.selected:
            row, col = self.coords_to_row_col(e.x, e.y)
            self.canvas.delete("selected")
            self.place_piece(self.selected_piece, (row, col))
            self.selected_piece = None
            self.selected = False
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
                self.add_piece("white_queen_" + str(c), images["white_queen"], 7, c)
                self.add_piece("black_queen_" + str(c), images["black_queen"], 0, c)
            if c == 4:
                self.add_piece("white_king_" + str(c), images["white_king"], 7, c)
                self.add_piece("black_king_" + str(c), images["black_king"], 0, c)

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

    def move(self, e):
        self.coords_label.config(text="x: " + str(e.x) + " y: " + str(e.y))

if __name__ == "__main__":
    root = Tk()
    board = GameBoard(root)
    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    board.setup_board()

    root.resizable(0, 0)
    root.mainloop()