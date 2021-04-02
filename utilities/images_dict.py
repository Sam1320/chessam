from tkinter import PhotoImage


class Images:
    images = {}
    @staticmethod
    def load_images():
        path = r'C:\Users\Sam\Documents\Python Scripts\Chess\images'
        images = {"white_rook": PhotoImage(file=path + '\white_rook_50px.png'),
                  "white_pawn": PhotoImage(file=path + '\white_pawn_50px.png'),
                  "white_knight": PhotoImage(file=path + '\white_knight_50px.png'),
                  "white_bishop": PhotoImage(file=path + '\white_bishop_50px.png'),
                  "white_queen": PhotoImage(file=path + '\white_queen_50px.png'),
                  "white_king": PhotoImage(file=path + '\white_king_50px.png'),
                  "black_pawn": PhotoImage(file=path + r'\black_pawn_50px.png'),
                  "black_rook": PhotoImage(file=path + r'\black_rook_50px.png'),
                  "black_knight": PhotoImage(file=path + r'\black_knight_50px.png'),
                  "black_bishop": PhotoImage(file=path + r'\black_bishop_50px.png'),
                  "black_queen": PhotoImage(file=path + r'\black_queen_50px.png'),
                  "black_king": PhotoImage(file=path + r'\black_king_50px.png'),
                  }
        return images
