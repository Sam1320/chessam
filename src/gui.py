from tkinter import *
from utilities.images_dict import Images


class GameBoard(Frame):
    def __init__(self, parent, rows=8, columns=8, size=64, color1="white",
                 color2="gray"):

        super(GameBoard, self).__init__(master=parent)
        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.pieces = {}
        self.images_dic = Images.load_images()

        canvas_width = columns * size
        canvas_height = rows * size

        self.canvas = Canvas(self, borderwidth=0, highlightthickness=0,
                             width=canvas_width, height=canvas_height,
                             background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        # This binding will cause a refresh if the user interactively
        # changes the window size
        self.canvas.bind("<Configure>", self.refresh)

    def add_piece(self, name, image, row=0, column=0):
        # Add a piece to the playing board'''
        self.canvas.create_image(0, 0, image=image, tags=(name, "piece"),
                                 anchor="c")
        self.place_piece(name, row, column)

    def place_piece(self, name, row, column):
        # Place a piece at the given row/column
        self.pieces[name] = (row, column)
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)

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
        for name in self.pieces:
            self.place_piece(name, self.pieces[name][0], self.pieces[name][1])
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")

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


if __name__ == "__main__":
    root = Tk()
    board = GameBoard(root)
    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    board.setup_board()
    root.mainloop()
