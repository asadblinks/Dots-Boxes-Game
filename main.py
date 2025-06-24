import pygame

SCREEN = WIDTH, HEIGHT = 300, 300
CELLSIZE = 40
PADDING = 20
ROWS = COLS = (WIDTH - 4 * PADDING) // CELLSIZE
pygame.init()
GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE = (255, 255, 255)
RED = (252, 91, 122)
BLUE = (78, 193, 246)
GREEN = (0, 255, 0)
BLACK = (12, 12, 12)

font = pygame.font.SysFont('cursive', 25)

class Cell:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.index = self.r * ROWS + self.c

        rectangle_points = (
            self.c * CELLSIZE + 2 * PADDING,
            self.r * CELLSIZE + 3 * PADDING,
            CELLSIZE,
            CELLSIZE
        )

        self.rect = pygame.Rect(rectangle_points)
        self.left = self.rect.left
        self.top = self.rect.top
        self.right = self.rect.right
        self.bottom = self.rect.bottom

        self.edges = [
            [(self.left, self.top), (self.right, self.top)],
            [(self.right, self.top), (self.right, self.bottom)],
            [(self.right, self.bottom), (self.left, self.bottom)],
            [(self.left, self.bottom), (self.left, self.top)]
        ]

        self.sides = [False, False, False, False]
        self.winner = None

    def checkwin(self, winner):
        if not self.winner:
            if self.sides == [True]*4:
                self.winner = winner
                if winner == 'X':
                    self.color = GREEN
                else:
                    self.color = RED
                self.text = font.render(self.winner, True, BLACK)

                return 1
        return 0

    def update(self, win):
        if self.winner:
            pygame.draw.rect(win, self.color, self.rect)
            win.blit(self.text, (self.rect.centerx-5, self.rect.centery-7))

        for index, side in enumerate(self.sides):
            if side:
                line_x, line_y = self.edges[index]
                pygame.draw.line(win, BLACK, line_x, line_y, 2)

def create_cells():
    cells = []
    for r in range(ROWS):
        for c in range(COLS):
            cell = Cell(r, c)
            cells.append(cell)
    return cells

def reset_cells():
    pos = None
    ccell = None
    up = False
    right = False
    bottom = False
    left = False
    return pos, ccell, up, right, bottom, left

def reset_score():
    fillcount = 0
    p1_score = 0
    p2_score = 0
    return fillcount, p1_score, p2_score

def reset_player():
    turn = 0
    players = ['X', 'O']
    player = players[turn]
    next_turn = False
    return turn, players, player, next_turn

gameover = False
cells = create_cells()
pos, ccell, up, right, bottom, left = reset_cells()
fillcount, p1_score, p2_score = reset_score()
turn, players, player, next_turn = reset_player()

run = True
while run:
    GAME_WINDOW.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            pos = None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                run = False

            if event.key == pygame.K_r:
                gameover = False
                cells = create_cells()
                pos, ccell, up, right, bottom, left = reset_cells()
                fillcount, p1_score, p2_score = reset_score()
                turn, players, player, next_turn = reset_player()

            if not gameover:
                if event.key == pygame.K_UP:
                    up = True
                if event.key == pygame.K_RIGHT:
                    right = True
                if event.key == pygame.K_DOWN:
                    bottom = True
                if event.key == pygame.K_LEFT:
                    left = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                up = False
            if event.key == pygame.K_RIGHT:
                right = False
            if event.key == pygame.K_DOWN:
                bottom = False
            if event.key == pygame.K_LEFT:
                left = False

    for r in range(ROWS+1):
        for c in range(COLS+1):
            pygame.draw.circle(GAME_WINDOW, BLACK, (c*CELLSIZE + 2*PADDING, r*CELLSIZE + 3*PADDING), 2)

    for cell in cells:
        cell.update(GAME_WINDOW)
        if pos and cell.rect.collidepoint(pos):
            ccell = cell

    if ccell:
        index = ccell.index
        if not ccell.winner:
            pygame.draw.circle(GAME_WINDOW, RED, (ccell.rect.centerx, ccell.rect.centery), 2)

        if up and not ccell.sides[0]:
            ccell.sides[0] = True
            if index - ROWS >= 0:
                cells[index-ROWS].sides[2] = True
                next_turn = True
        if right and not ccell.sides[1]:
            ccell.sides[1] = True
            if (index + 1) % COLS > 0:
                cells[index+1].sides[3] = True
                next_turn = True
        if bottom and not ccell.sides[2]:
            ccell.sides[2] = True
            if index + ROWS < len(cells):
                cells[index+ROWS].sides[0] = True
                next_turn = True
        if left and not ccell.sides[3]:
            ccell.sides[3] = True
            if (index % COLS) > 0:
                cells[index-1].sides[1] = True
                next_turn = True

        res = ccell.checkwin(player)
        if res:
            fillcount += res
            if player == 'X':
                p1_score += 1
            else:
                p2_score += 1
            if fillcount == ROWS * COLS:
                print(p1_score, p2_score)
                gameover = True

        if next_turn:
            turn = (turn + 1) % len(players)
            player = players[turn]
            next_turn = False

    p1img = font.render(f'Player 1 : {p1_score}', True, BLUE)
    p1rect = p1img.get_rect()
    p1rect.x, p1rect.y = 2*PADDING, 15

    p2img = font.render(f'Player 2 : {p2_score}', True, BLUE)
    p2rect = p2img.get_rect()
    p2rect.right, p2rect.y = WIDTH-2*PADDING, 15

    GAME_WINDOW.blit(p1img, p1rect)
    GAME_WINDOW.blit(p2img, p2rect)
    if player == 'X':
        pygame.draw.line(GAME_WINDOW, RED, (p1rect.x, p1rect.bottom+2),
                            (p1rect.right, p1rect.bottom+2), 1)
    else:
        pygame.draw.line(GAME_WINDOW, RED, (p2rect.x, p2rect.bottom+2),
                            (p2rect.right, p2rect.bottom+2), 1)

    if gameover:
        rect = pygame.Rect((50, 100, WIDTH-100, HEIGHT-200))
        pygame.draw.rect(GAME_WINDOW, WHITE, rect)
        pygame.draw.rect(GAME_WINDOW, RED, rect, 2)

        over = font.render('Game Over', True, WHITE)
        GAME_WINDOW.blit(over, (rect.centerx-over.get_width()/2, rect.y + 10))

        winner = '1' if p1_score > p2_score else '2'
        winner_img = font.render(f'Player {winner} Won', True, GREEN)
        GAME_WINDOW.blit(winner_img, (rect.centerx-winner_img.get_width()/2, rect.centery- 10))

        msg = 'Press r:restart, q:quit'
        msgimg = font.render(msg, True, RED)
        GAME_WINDOW.blit(msgimg, (rect.centerx-msgimg.get_width()/2, rect.centery + 20))

    pygame.draw.rect(GAME_WINDOW, WHITE, (0,0,WIDTH,HEIGHT),2, border_radius=10)
    pygame.display.update()

pygame.quit()