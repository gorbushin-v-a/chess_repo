from itertools import chain


NO_PIECE = 0
PIECES = (W_PAWN, W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN, W_KING, B_PAWN, B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN, B_KING) =\
    list(chain(range(1, 7), range(9, 15)))

piece_string_to_int = {'P': W_PAWN,
                       'N': W_KNIGHT,
                       'B': W_BISHOP,
                       'R': W_ROOK,
                       'Q': W_QUEEN,
                       'K': W_KING,
                       'p': B_PAWN,
                       'n': B_KNIGHT,
                       'b': B_BISHOP,
                       'r': B_ROOK,
                       'q': B_QUEEN,
                       'k': B_KING}


def get_idx_from_coords(coords):
    x, y = coords
    m, n = x, abs(y - 7)
    return m + 8 * n


def is_free(field, coords):
    return not field[get_idx_from_coords(coords)]


def is_allowed(field, coords_to, coords_from):
    return 0 <= coords_to[0] < 8 and 0 <= coords_to[1] < 8 and (not is_same_color(field, coords_to, coords_from) or is_free(field, coords_to))


def is_same_color(field, coords1, coords2):
    return (field[get_idx_from_coords(coords1)] >> 3) & 1 == (field[get_idx_from_coords(coords2)] >> 3) & 1


def _get_diagonal(field, coords):
    moves = []
    x, y = coords
    for i in (-1, 1):
        for j in (-1, 1):
            for k in range(1, 8):
                if 0 <= x + i * k < 8 and 0 <= y + j * k < 8:
                    if is_free(field, (x + i * k, y + j * k)):
                        moves.append((x + i * k, y + j * k))
                    elif not is_same_color(field, coords, (x + i * k, y + j * k)):
                        moves.append((x + i * k, y + j * k))
                        break
                    else:
                        break
    return moves


def _get_orthogonal(field, coords):
    moves = []
    x, y = coords
    for i, j in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        for k in range(1, 8):
            if 0 <= x + i * k < 8 and 0 <= y + j * k < 8:
                if is_free(field, (x + i * k, y + j * k)):
                    moves.append((x + i * k, y + j * k))
                elif not is_same_color(field, coords, (x + i * k, y + j * k)):
                    moves.append((x + i * k, y + j * k))
                    break
                else:
                    break
    return moves


def get_knight_moves(field, coords):
    moves = []
    x, y = coords
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if abs(dx) + abs(dy) == 3 and 0 <= x + dx < 8 and 0 <= y + dy < 8:
                if not is_same_color(field, (x + dx, y + dy), coords) or is_free(field, (x + dx, y + dy)):
                    moves.append((x + dx, y + dy))
    return moves


def get_bishop_moves(field, coords):
    return _get_diagonal(field, coords)


def get_rook_moves(field, coords):
    return _get_orthogonal(field, coords)


def get_queen_moves(field, coords):
    return _get_diagonal(field, coords) + _get_orthogonal(field, coords)


def get_king_moves(field, coords):
    moves = []
    x, y = coords
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if 0 <= x + dx < 8 and 0 <= y + dy < 8:
                if is_free(field, (x + dx, y + dy)) or not is_same_color(field, coords, (x + dx, y + dy)):
                    moves.append((x + dx, y + dy))
    return moves


def get_pawn_moves(field, coords):
    moves = []
    x, y = coords

    dir = 1 if field[get_idx_from_coords(coords)] < 8 else -1

    if is_free(field, (x, y + dir)):
        moves.append((x, y + dir))

    if (y - dir == 0 or y - dir == 7) and is_allowed(field, (x, y + dir * 2), coords):
        moves.append((x, y + dir * 2))

    if not is_free(field, (x + 1, y + dir)) and not is_same_color(field, coords, (x + 1, y + dir)):
        moves.append((x + 1, y + dir))
    if not is_free(field, (x - 1, y + dir)) and not is_same_color(field, coords, (x - 1, y + dir)):
        moves.append((x - 1, y + dir))

    return moves


if __name__ == "__main__":
    board_fen = "rnbqkbnr/pppppppp/8/1KP5/8/P7/1PPPPPPP/RNBQKBNR"
    squares = [None] * 64

    index = 0
    for char in board_fen:
        if char in 'KQRBNPkqrbnp':
            squares[index] = piece_string_to_int[char]
            index += 1
        elif char in '12345678':
            for _ in range(int(char)):
                squares[index] = NO_PIECE
                index += 1
        elif char == '/':
            pass
        else:
            raise Exception("Unknown character in FEN: {}".format(char))

    print(squares)
    print(get_king_moves(squares, (1, 4)))
