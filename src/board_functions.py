from copy import deepcopy
import random
import numpy as np


def check_en_passant(name_piece, piece, x2, y2):
    """ verifies if moving piece to x2, y2 is a valid en passant move."""
    if not (name_piece["en_passant"] and piece.type == "pawn"):
        return False
    else:
        x1, y1 = piece.position
        to_take = name_piece["en_passant"]
        x3, y3 = to_take.position
        if x3 == x2 and y3 == y1:
            return True
        return False


def do_move(node, piece_move):
    """takes a board state 'node' executes the move in 'piece_move' and returns the updated board state."""
    next_node = deepcopy(node)
    pieces_coords = next_node["pieces_coords"]
    coords_pieces = next_node["coords_pieces"]
    name_piece = next_node["name_piece"]
    next_node["turn"] = 2 if next_node["turn"] == 1 else 1
    next_node["current_color"] = "white" if next_node["current_color"] == "black" else "black"

    piece, move = piece_move
    # modify the copy not the original
    piece = coords_pieces[piece.position]

    x1, y1 = piece.position
    x2, y2 = move

    if check_en_passant(name_piece, piece, x2, y2):
        old_piece = name_piece["en_passant"]
    else:
        old_piece = coords_pieces[(x2, y2)]
    pieces_coords[old_piece] = None
    pieces_coords[piece] = (x2, y2)
    coords_pieces[(x1, y1)] = None
    coords_pieces[(x2, y2)] = piece
    piece.move(x2, y2)
    return next_node


def is_terminal_node(node):
    """checks if there are no more possible moves in node."""
    game_over = node["game_over"]
    if game_over:
        return True


def available_moves(node):
    """returns all available moves of current player."""
    pieces_coords = node["pieces_coords"]
    current_color = node["current_color"]
    coords_pieces = node["coords_pieces"]
    name_piece = node["name_piece"]
    player = node["turn"]

    possible_moves = {}
    for p in pieces_coords:
        if p:
            if not p.taken and p.color == current_color:
                moves = p.possible_moves(
                    coords_pieces=coords_pieces,
                    pieces_coords=pieces_coords,
                    name_piece=name_piece,
                    player=player)
                if moves:
                    possible_moves[p] = moves
    return possible_moves


def random_move(node):
    """returns a random piece an move given a board state 'node'."""
    possible_moves = available_moves(node)
    if possible_moves:
        piece = random.choice(list(possible_moves.keys()))
        move = random.choice(possible_moves[piece])
        return piece, move


def available_attacks(node):
    """returns all available attacks of current player or random piece and move in case no attacks are found."""
    coords_pieces = node["coords_pieces"]
    name_piece = node["name_piece"]

    possible_moves = available_moves(node)
    attacking_moves = {}
    if possible_moves:
        for piece, moves in possible_moves.items():
            attacks = []
            for move in moves:
                if coords_pieces[move]:
                    attacks.append(move)
                elif check_en_passant(name_piece, piece, move[0], move[1]):
                    attacks.append(move)
            if attacks:
                attacking_moves[piece] = attacks
    if not attacking_moves:
        piece = random.choice(list(possible_moves.keys()))
        move = random.choice(possible_moves[piece])
        return None, piece, move
    else:
        return attacking_moves, None, None


def random_attack(node):
    """returns a random piece and attacking move given a board state 'node'."""
    attacking_moves, piece, move = available_attacks(node)
    if attacking_moves:
        piece = random.choice(list(attacking_moves.keys()))
        move = random.choice(attacking_moves[piece])
        return piece, move
    return piece, move


def score_move(node, piece_move, nsteps):
    """returns the board assessment after executing 'piece_move' and anticipating 'nsteps' steps in th future."""
    next_node = do_move(node, piece_move)
    eval = minimax(next_node, nsteps, False, alpha=-np.inf, beta=np.inf)
    return eval


def n_step_lookahead(node, nsteps):
    """returns the move with the highest score after looking 'nsteps' steps in the future."""
    valid_moves = available_moves(node)
    scores = {}
    for piece, moves in valid_moves.items():
        for move in moves:
            score = score_move(node, (piece, move), nsteps-1)
            scores[(piece, move)] = score
    # Get a list of columns (moves) that maximize the heuristic
    max_score = max(scores.values())
    max_moves = [piece_move for piece_move in scores.keys() if
                scores[piece_move] == max_score]
    if max_moves:
        piece, move = random.choice(max_moves)
        return piece, move
    return -1


def board_eval(node, player):
    """returns simple static board evaluation score."""
    pieces_coords = node["pieces_coords"]
    score = 0
    for piece, coords in pieces_coords.items():
        if piece and coords:
            if piece.player == player:
                score += piece.value
            else:
                score -= piece.value
    return score


def minimax(node, depth, maximizing_player, alpha, beta):
    player = node["player"]
    is_terminal = is_terminal_node(node)
    if depth == 0 or is_terminal:
        return board_eval(node, player)

    valid_moves = available_moves(node)
    if maximizing_player:
        value = -np.inf
        for piece, moves in valid_moves.items():
            for move in moves:
                child = do_move(node, (piece, move))
                value = max(value, minimax(child, depth-1, False, alpha, beta))
                alpha = max(alpha, value)
                if beta <= alpha:
                    return value
        return value
    else:
        value = np.inf
        for piece, moves in valid_moves.items():
            for move in moves:
                child = do_move(node, (piece, move))
                value = min(value, minimax(child, depth-1, True, alpha, beta))
                beta = min(value, beta)
                if beta <= alpha:
                    return value
        return value


def board_to_FEN(board):
    """Converts board to FEN notation."""
    coords_pieces = board["coords_pieces"]
    color = board["current_color"]
    name_piece = board["name_piece"]
    en_passant = name_piece["en_passant"]
    n_move = board["move_count"]

    fen = ""
    # board
    for y in range(8):
        empty = 0
        for x in range(8):
            piece = coords_pieces[(x, y)]
            if piece:
                if empty:
                    fen += str(empty)
                    empty = 0
                if piece.color == "white":
                    if piece.type == "knight":
                        fen += "N"
                    else:
                        fen += piece.type[0].upper()
                else:
                    if piece.type == "knight":
                        fen += "n"
                    else:
                        fen += piece.type[0]
            else:
                empty +=1
        if empty:
            fen += str(empty)
        if y != 7:
            fen += "/"
    # color
    fen += " "+color[0]

    wk = name_piece["white_king_4"]
    bk = name_piece["black_king_4"]
    left_castle_w = not wk.rooks[0].moved
    right_castle_w = not wk.rooks[1].moved
    left_castle_b = not bk.rooks[0].moved
    right_castle_b = not bk.rooks[1].moved

    castle = ""
    if right_castle_w:
        castle += "K"
    if left_castle_w:
        castle += "Q"
    if right_castle_b:
        castle += "k"
    if left_castle_b:
        castle += "q"
    if not castle:
        castle = "-"
    fen += " "+castle

    # en passant
    if en_passant:
        x, y = en_passant.position
        square = xy_to_square(x, y)
        fen += " "+square
    else:
        fen += " -"

    fen += " "+str(0)
    fen += " "+str(n_move)

    return fen


def move_to_piece_move(move):
    """Converts move in FEN notation to piece and move pair."""
    file_to_x = {key: value for key, value in zip("abcdefgh", range(8))}
    file1, rank1, file2, rank2 = move

    x1 = file_to_x[file1]
    x2 = file_to_x[file2]
    y1 = 8-int(rank1)
    y2 = 8-int(rank2)

    return (x1, y1), (x2, y2)


def xy_to_square(x, y):
    """Converts xy grid coordinates to square coordinates in chess notation."""
    x_to_file = {key: value for key, value in zip(range(8), "abcdefgh")}
    y = 7-y
    return x_to_file[x]+str(y)

