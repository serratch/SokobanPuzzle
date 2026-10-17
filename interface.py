import sys
import time
from collections import deque
import pygame
from sokoban_puzzle import SokobanPuzzle
from boards import BOARDS
from search import BFS

ALGORITHMS = {"BFS": BFS}

def run_algorithm(func, initial_state):
    """Lance un algorithme et normalise son résultat en (nœud_but, stats)."""
    start = time.time()
    result = func(initial_state)
    if isinstance(result, tuple):
        goal, raw_stats = result
    else:
        goal, raw_stats = result, {}

    if isinstance(raw_stats, dict):
        stats = raw_stats.copy()
    elif isinstance(raw_stats, (int, float)):
        stats = {"steps": raw_stats}
    else:
        stats = {}

    stats.setdefault("time", time.time() - start)
    return goal, stats

LEVELS = {
    f"Niveau {number}": board
    for number, board in BOARDS.items()
}

WIN_W, WIN_H = 1100, 680
BOARD_AREA = pygame.Rect(20, 20, 700, 640)   # zone où on dessine la grille
PANEL_X = 740                                # début du panneau de droite

# Couleurs
BG = (30, 33, 40)
FLOOR = (252, 222, 178)
FLOOR_LINE = (235, 205, 160)
WALL = (120, 120, 125)
WALL_LINE = (70, 70, 75)
BOX = (150, 90, 40)
BOX_DARK = (95, 55, 20)
BOX_OK = (240, 215, 40)
TARGET = (200, 60, 60)
SKIN = (255, 224, 189)
SHIRT = (255, 192, 203)
WHITE = (240, 240, 240)
GREY = (150, 155, 165)
GREEN = (80, 190, 110)
BTN = (60, 66, 82)
BTN_HOVER = (85, 93, 115)
BTN_ACTIVE = (60, 130, 200)


class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self, screen, font, active=False):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        color = BTN_ACTIVE if active else (BTN_HOVER if hover else BTN)
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        label = font.render(self.text, True, WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))


def draw_board(screen, state, area):
    """Dessine la grille d'un état dans la zone 'area'."""
    if not state.board or not state.board[0]:
        return
    ts = min(area.width // len(state.board[0]), area.height // len(state.board))  # taille d'une case
    ox = area.x + (area.width - ts * len(state.board[0])) // 2
    oy = area.y + (area.height - ts * len(state.board)) // 2

    for r in range(len(state.board)):
        for c in range(len(state.board[0])):
            cell = state.board[r][c]
            rect = pygame.Rect(ox + c * ts, oy + r * ts, ts, ts)

            if cell == " " and _is_outside(state, r, c):
                continue  # on ne dessine pas l'extérieur de l'entrepôt

            if cell == "O":
                pygame.draw.rect(screen, WALL, rect)
                pygame.draw.rect(screen, WALL_LINE, rect, 1)
                # petites lignes de briques
                pygame.draw.line(screen, WALL_LINE, (rect.x, rect.centery), (rect.right, rect.centery))
                pygame.draw.line(screen, WALL_LINE, (rect.centerx, rect.y), (rect.centerx, rect.centery))
                pygame.draw.line(screen, WALL_LINE, (rect.x + ts // 4, rect.centery), (rect.x + ts // 4, rect.bottom))
                continue

            # sol
            pygame.draw.rect(screen, FLOOR, rect)
            pygame.draw.rect(screen, FLOOR_LINE, rect, 1)

            # cible (sous la caisse / le joueur si présent)
            if cell in ("S", ".", "*"):
                m = ts // 4
                pygame.draw.rect(screen, TARGET, rect.inflate(-2 * m, -2 * m), 3)
                pygame.draw.line(screen, TARGET, (rect.x + m, rect.y + m), (rect.right - m, rect.bottom - m), 3)
                pygame.draw.line(screen, TARGET, (rect.right - m, rect.y + m), (rect.x + m, rect.bottom - m), 3)

            # caisse
            if cell in ("B", "*"):
                box_rect = rect.inflate(-ts // 6, -ts // 6)
                pygame.draw.rect(screen, BOX_OK if cell == "*" else BOX, box_rect, border_radius=4)
                pygame.draw.rect(screen, BOX_DARK, box_rect, 3, border_radius=4)
                for i in (1, 2):
                    y = box_rect.y + i * box_rect.height // 3
                    pygame.draw.line(screen, BOX_DARK, (box_rect.x, y), (box_rect.right, y), 2)

            # joueur
            if cell in ("R", "."):
                cx, cy = rect.center
                pygame.draw.rect(screen, SHIRT, (cx - ts // 4, cy, ts // 2, ts // 3), border_radius=4)
                pygame.draw.circle(screen, SKIN, (cx, cy - ts // 8), ts // 4)
                pygame.draw.circle(screen, (20, 20, 20), (cx - ts // 12, cy - ts // 7), max(2, ts // 20))
                pygame.draw.circle(screen, (20, 20, 20), (cx + ts // 12, cy - ts // 7), max(2, ts // 20))


_outside_cache = {}


def _is_outside(state, r, c):
    """Une case vide est 'à l'extérieur' si elle peut rejoindre le bord de la grille
    sans traverser de mur (on ne la dessine pas)."""
    walls_key = tuple("".join("O" if ch == "O" else "x" for ch in row) for row in state.board)
    if walls_key not in _outside_cache:
        outside = set()
        queue = deque()
        for rr in range(len(state.board)):
            for cc in range(len(state.board[0])):
                if (rr in (0, len(state.board) - 1) or cc in (0, len(state.board[0]) - 1)) and state.board[rr][cc] != "O":
                    outside.add((rr, cc))
                    queue.append((rr, cc))
        while queue:
            rr, cc = queue.popleft()
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = rr + dr, cc + dc
                if 0 <= nr < len(state.board) and 0 <= nc < len(state.board[0]) \
                        and (nr, nc) not in outside and state.board[nr][nc] != "O":
                    outside.add((nr, nc))
                    queue.append((nr, nc))
        _outside_cache[walls_key] = outside
    return (r, c) in _outside_cache[walls_key]


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Sokoban - Projet 1 - Problem Solving")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("arial", 20)
    font_small = pygame.font.SysFont("arial", 16)
    font_big = pygame.font.SysFont("arial", 28, bold=True)

    level_names = list(LEVELS.keys())
    level_index = 0

    # ----- boutons -----
    level_buttons = [Button((PANEL_X + i * 53, 70, 47, 36), str(i + 1)) for i in range(len(level_names))]
    algo_buttons = {name: Button((PANEL_X, 160 + i * 46, 340, 38), f"Résoudre avec {name}")
                    for i, name in enumerate(ALGORITHMS)}
    y0 = 160 + len(ALGORITHMS) * 46 + 10
    # On garde seulement le bouton pour recommencer le niveau.
    btn_reset = Button((PANEL_X, y0, 340, 38), "Recommencer")
    animation_delay = 300  # millisecondes entre deux déplacements de la solution

    # ----- variables d'état de l'application -----
    initial = None
    current = None        # état affiché
    path = []             # liste des états de la solution
    step = 0              # indice dans path
    playing = False
    last_tick = 0
    results = {}          # nom algo pour statistiques (pour le tableau)
    message = ""
    manual_moves = 0

    def load_level(i):
        nonlocal level_index, initial, current, path, step, playing, results, message, manual_moves
        level_index = i
        initial = SokobanPuzzle(LEVELS[level_names[i]])
        current = initial
        path, step, playing, results = [], 0, False, {}
        message = "Flèches du clavier = jouer à la main"
        manual_moves = 0

    load_level(0)

    running = True
    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # choix du niveau
            for i, b in enumerate(level_buttons):
                if b.clicked(event):
                    load_level(i)

            # lancer un algorithme
            for name, b in algo_buttons.items():
                if b.clicked(event):
                    load_level(level_index)
                    message = f"Calcul {name} en cours..."
                    # on affiche le message avant de bloquer pendant le calcul
                    screen.fill(BG)
                    txt = font_big.render(message, True, WHITE)
                    screen.blit(txt, (PANEL_X, 400))
                    pygame.display.flip()

                    goal, stats = run_algorithm(ALGORITHMS[name], initial)
                    if goal is None:
                        results[name] = {**stats, "cost": None}
                        message = "Aucune solution trouvée."
                    else:
                        path = [node.state for node in goal.get_path()]
                        results[name] = {**stats, "cost": goal.g, "solution": goal.get_solution()}
                        step = 0
                        message = "Solution trouvée ! Lecture automatique..."
                        playing = True
                        last_tick = pygame.time.get_ticks()

            if btn_reset.clicked(event):
                load_level(level_index)

            # jeu manuel avec les flèches
            if event.type == pygame.KEYDOWN and not path:
                keys = {pygame.K_UP: "Up", pygame.K_DOWN: "Down",
                        pygame.K_LEFT: "Left", pygame.K_RIGHT: "Right"}
                if event.key in keys and not current.is_goal():
                    for action, succ in current.successors():
                        if action == keys[event.key]:
                            current = succ
                            manual_moves += 1
                            break
                    if current.is_goal():
                        message = f"Bravo ! Gagné en {manual_moves} coups."

        # ---------------- animation de la solution ----------------
        if playing and path:
            if now - last_tick >= animation_delay:
                last_tick = now
                if step < len(path) - 1:
                    step += 1
                else:
                    playing = False
        if path:
            current = path[step]
            if step == len(path) - 1:
                message = "But atteint !"

        screen.fill(BG)
        draw_board(screen, current, BOARD_AREA)

        screen.blit(font_big.render("Sokoban", True, WHITE), (PANEL_X, 20))
        screen.blit(font_small.render("Choix du niveau :", True, GREY), (PANEL_X, 50 - 2))
        for i, b in enumerate(level_buttons):
            b.draw(screen, font, active=(i == level_index))
        screen.blit(font_small.render("Algorithme :", True, GREY), (PANEL_X, 135))
        for b in algo_buttons.values():
            b.draw(screen, font)

        btn_reset.draw(screen, font)

        # panneau d'informations
        y = y0 + 60
        pygame.draw.line(screen, GREY, (PANEL_X, y - 8), (PANEL_X + 340, y - 8))
        if path:
            screen.blit(font.render(f"Étape : {step} / {len(path) - 1}", True, WHITE), (PANEL_X, y))
        else:
            screen.blit(font.render(f"Coups joués : {manual_moves}", True, WHITE), (PANEL_X, y))
        y += 34
        for name, st in results.items():
            screen.blit(font.render(f"Résultats {name}", True, GREEN), (PANEL_X, y))
            y += 28
            cost = st["cost"] if st["cost"] is not None else "-"
            lines = [
                f"Coût de la solution : {cost}",
                f"Nœuds développés : {st.get('expanded', '-')}",
                f"Nœuds générés : {st.get('generated', '-')}",
                f"Temps : {st['time']:.3f} s",
            ]
            for line in lines:
                screen.blit(font_small.render(line, True, WHITE), (PANEL_X + 10, y))
                y += 24
            y += 6

        # message en bas
        screen.blit(font_small.render(message, True, GREEN if "Bravo" in message or "atteint" in message else GREY),
                    (PANEL_X, WIN_H - 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
