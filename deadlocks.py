DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
HORIZONTAL = (0, 1)
VERTICAL = (1, 0)


def case(board, i, j):
    if 0 <= i < len(board) and 0 <= j < len(board[i]):
        return board[i][j]
    return 'O'


def est_coin(board, i, j):
    mur_vertical = case(board, i - 1, j) == 'O' or case(board, i + 1, j) == 'O'
    mur_horizontal = case(board, i, j - 1) == 'O' or case(board, i, j + 1) == 'O'
    return mur_vertical and mur_horizontal


def est_mur(state, i, j):
    board = state.board
    for wi, wj in DIRECTIONS:
        if case(board, i + wi, j + wj) != 'O':
            continue

        ai, aj = wj, wi
        mort = True
        for sens in (1, -1):
            k = 0
            while True:
                pi = i + ai * k * sens
                pj = j + aj * k * sens
                if case(board, pi, pj) == 'O':
                    break
                if (pi, pj) in state.targets:
                    mort = False
                    break
                if case(board, pi + wi, pj + wj) != 'O':
                    mort = False
                    break
                k += 1
            if not mort:
                break

        if mort:
            return True
    return False


def est_bloquee_sur_axe(board, i, j, axe, vus):
    di, dj = axe
    voisins = [(i - di, j - dj), (i + di, j + dj)]

    for vi, vj in voisins:
        if case(board, vi, vj) == 'O':
            return True

    for vi, vj in voisins:
        if case(board, vi, vj) in ('B', '*'):
            if est_gelee(board, vi, vj, vus):
                return True

    return False


def est_gelee(board, i, j, vus):
    if (i, j) in vus:
        return True
    vus = vus | {(i, j)}
    return (est_bloquee_sur_axe(board, i, j, HORIZONTAL, vus)
            and est_bloquee_sur_axe(board, i, j, VERTICAL, vus))

def est_deadlock(state):
    for i, row in enumerate(state.board):
        for j, cell in enumerate(row):
            if cell == 'B':
                if est_coin(state.board, i, j):
                    return True
                if est_mur(state, i, j):
                    return True
                if est_gelee(state.board, i, j, frozenset()):
                    return True
    return False
