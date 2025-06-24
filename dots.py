import pygame
import random

WHITE = (255, 255, 255)
RED = (252, 91, 122)
BLUE = (78, 193, 246)
GREEN = (0, 255, 0)
BLACK = (12, 12, 12)
FONT_SIZE = 24
CELLSIZE = 80
PAD = 100

pygame.font.init()
font = pygame.font.SysFont("verdana", FONT_SIZE)

class Cell:

    def __init__(self, r, c, reset=False):
        self.r = r
        self.c = c
        self.reset = reset
        self.color = None
        self.text = None
        self.edge_threshold = 10
        self.instances = list()

        self.rect = pygame.Rect((self.c, self.r, CELLSIZE, CELLSIZE))

        self.left = self.rect.left
        self.top = self.rect.top
        self.right = self.rect.right
        self.bottom = self.rect.bottom

        self.edges = {
            self.left: [(self.left, self.top), (self.left, self.bottom)],
            self.top: [(self.left, self.top), (self.right, self.top)],
            self.right: [(self.right, self.top), (self.right, self.bottom)],
            self.bottom: [(self.left, self.bottom), (self.right, self.bottom)]
        }

        #    Sides = [LEFT,  TOP,   RIGHT, BOTTOM]
        self.sides = [False, False, False, False]

    def set_instances(self, items):
        self.instances = items.copy()

    def get_instances(self):
        return self.instances.copy()

    def update(self, window_panel):
        # Display function to draw line when cell's side is clicked
        if all(self.sides):
            pygame.draw.rect(window_panel, self.color, self.rect)
            text = font.render(self.text, True, BLACK)
            window_panel.blit(text, (self.rect.centerx - 10, self.rect.centery - 15))

        for i, side in enumerate(self.sides):
            if side:
                edge_side = list(self.edges.keys())[i]
                line_start = tuple(v - 1 if v == edge_side else v for v in self.edges[edge_side][0])
                line_end = tuple(v - 1 if v == edge_side else v for v in self.edges[edge_side][1])
                pygame.draw.line(window_panel, BLACK, line_start, line_end, 2)

    def update_sides(self, edge_value, user):
        # Update cell's side and other cell around it.
        # e.g if cell left side is clicked then the cell's right side will be updated on adjacent cell

        cell_fill = 0
        for cell_obj in self.get_instances():
            if edge_value in cell_obj.edges.keys() and self.edges[edge_value] in list(cell_obj.edges.values()):
                s_ind = list(cell_obj.edges.keys()).index(edge_value)
                cell_obj.sides[s_ind] = True
                if all(cell_obj.sides):
                    cell_fill += 1
                    cell_obj.color = GREEN if user == 'X' else RED
                    cell_obj.text = user
                # print(cell_obj.rect, cell_obj.sides)
        return cell_fill

    def is_edge_click(self, mouse_position, is_turn_next, user):
        x, y = mouse_position
        dist_left = abs(x - self.rect.left)
        dist_right = abs(x - self.rect.right)
        dist_top = abs(y - self.rect.top)
        dist_bottom = abs(y - self.rect.bottom)

        if dist_left < self.edge_threshold:
            edge_clicked = self.left
        elif dist_right < self.edge_threshold:
            edge_clicked = self.right
        elif dist_top < self.edge_threshold:
            edge_clicked = self.top
        elif dist_bottom < self.edge_threshold:
            edge_clicked = self.bottom
        else:
            edge_clicked = 0

        n_cell_fill = 0
        if edge_clicked:
            side_index = list(self.edges.keys()).index(edge_clicked)
            if not self.sides[side_index]:
                n_cell_fill = self.update_sides(edge_clicked, user)
                is_turn_next = True
                if n_cell_fill:
                    is_turn_next = False
        return is_turn_next, n_cell_fill

class Game:
    def __init__(self):
        self.id = None
        self.ready = False
        self.grid_ready = False
        self.reset(False)

    def set_gameID(self, id):
        self.id = id

    def get_gameID(self):
        return self.id

    def reset(self, reset=False):
        self.turn = random.randint(0, 1)
        self.players = ['X', 'O']
        self.moves = [False] * len(self.players)
        self.player = self.players[self.turn]
        self.moves[self.turn] = True
        self.next_turn = False
        self.p1_score = self.p2_score = 0
        self.gameover = False
        self.cells_completed = 0
        if reset:
            self.set_cells()

    def initialize_game(self, cells_dim):
        self.cells_dim = cells_dim
        ROWS = COLS = self.cells_dim
        PADDING = PAD // 2
        self.ROW_GRID = [r * CELLSIZE + 2 * PADDING for r in range(ROWS + 1)]
        self.HEIGHT = max(self.ROW_GRID) + PADDING
        self.COL_GRID = [c * CELLSIZE + PADDING for c in range(COLS + 1)]
        self.WIDTH = max(self.COL_GRID) + PADDING
        self.total_cells = ROWS * COLS
        self.set_cells()

    def window_dimension(self):
        return self.WIDTH, self.HEIGHT

    def set_cells(self):
        self.game_cells = list()
        for r in self.ROW_GRID[:-1].copy():
            for c in self.COL_GRID[:-1].copy():
                cell = Cell(r, c)
                self.game_cells.append(cell)
        self.grid_ready = True

    def get_cells(self):
        return self.game_cells.copy()

    def draw_grid(self, win):
        for r in self.ROW_GRID.copy():
            for c in self.COL_GRID.copy():
                pygame.draw.circle(win, BLACK, (c, r), 4)

    def is_cell_clicked(self, cell, mouse_cord):
        cell.set_instances(self.get_cells())
        self.next_turn, n_cells = cell.is_edge_click(mouse_cord, self.next_turn, self.player)
        if n_cells:
            self.cells_completed += n_cells
            if self.player == 'X':
                self.p1_score += n_cells
            else:
                self.p2_score += n_cells

            self.gameover = self.cells_completed == self.total_cells

        if self.next_turn:
            self.moves = [False] * len(self.players)
            self.turn = (self.turn + 1) % len(self.players)
            self.player = self.players[self.turn]
            self.moves[self.turn] = True
            self.next_turn = False

    def get_move(self, player):
        """
        :param player: [0, 1]
        :return: True or False
        """
        return self.moves[player]

    def run(self):
        WIDTH, HEIGHT = self.window_dimension()
        GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dots and Boxes")
        cells = self.get_cells()

        mouse_cord = None
        run = True
        clock = pygame.time.Clock()
        while run:
            clock.tick(60)
            GAME_WINDOW.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_cord = event.pos

                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_cord = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        run = False

                    if event.key == pygame.K_r:
                        self.reset(True)
                        cells = self.get_cells()

            self.draw_grid(GAME_WINDOW)

            if mouse_cord:
                pygame.draw.circle(GAME_WINDOW, RED, mouse_cord, 2)

            for cell in cells:
                if mouse_cord and cell.rect.collidepoint(mouse_cord):
                    self.is_cell_clicked(cell, mouse_cord)
                cell.update(GAME_WINDOW)

            p1img = font.render('Player 1: {}'.format(self.p1_score), True, BLUE)
            p1rect = p1img.get_rect()
            text_pads = PAD // 3
            p1rect.x, p1rect.y = text_pads, 25

            p2img = font.render('Player 2: {}'.format(self.p2_score), True, BLUE)
            p2rect = p2img.get_rect()
            p2rect.right, p2rect.y = WIDTH - text_pads, 25

            GAME_WINDOW.blit(p1img, p1rect)
            GAME_WINDOW.blit(p2img, p2rect)

            turn_rectangle = p1rect if self.player == 'X' else p2rect
            pygame.draw.line(GAME_WINDOW, RED, (turn_rectangle.x, turn_rectangle.bottom + 2), (turn_rectangle.right, turn_rectangle.bottom + 2), 4)

            if self.gameover:
                rect = pygame.Rect((50, 100, WIDTH - 100, HEIGHT - 200))
                pygame.draw.rect(GAME_WINDOW, WHITE, rect)
                pygame.draw.rect(GAME_WINDOW, RED  , rect, 2)

                over = font.render('Game Over', True, BLACK)
                GAME_WINDOW.blit(over, (rect.centerx - over.get_width() // 2, rect.y + 10))

                winner = '1' if self.p1_score > self.p2_score else '2'
                winner_img = font.render(f'Player {winner} Won', True, GREEN)
                GAME_WINDOW.blit(winner_img, (rect.centerx - winner_img.get_width() // 2, rect.centery - 10))

                msg = 'Press r:restart, q:quit'
                msgimg = font.render(msg, True, RED)
                GAME_WINDOW.blit(msgimg, (rect.centerx - msgimg.get_width() // 2, rect.centery + 20))

            pygame.display.update()

        pygame.quit()

