from src import gui
from tkinter import *


class HumanHuman(gui.GameBoard):
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


if __name__ == "__main__":
    root = Tk()
    board = HumanHuman(root)
    #board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    board.grid(row=0, columnspan=6, padx=4, pady=4)
    board.setup_board()
    # Avoid window resizing
    root.resizable(0, 0)
    root.mainloop()