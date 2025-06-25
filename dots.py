import pygame
import random
from typing import List, Tuple, Dict, Optional
from config import gc

pygame.font.init()
font = pygame.font.SysFont(gc.FONT_NAME, gc.FONT_SIZE)

class Cell:
    """A class representing a single cell in the Dots and Boxes game.

    Each cell is a square that can have lines drawn on any of its four sides.
    When all sides are drawn, the cell is completed and owned by the player who
    completed it.

    Attributes:
        r (int): Row coordinate of the cell
        c (int): Column coordinate of the cell
        color (Tuple[int, int, int]): RGB color value of the cell when filled
        text (Optional[str]): Text to display in the cell when completed
        sides (List[bool]): State of each side [LEFT, TOP, RIGHT, BOTTOM]
    """

    def __init__(self, r: int, c: int, reset: bool = False) -> None:
        """Initialize a new cell.

        Args:
            r: Row coordinate of the cell
            c: Column coordinate of the cell
            reset: Whether this is a reset operation
        """
        self.r = r
        self.c = c
        self.reset = reset
        self.color = gc.COLORS['WHITE']
        self.text: Optional[str] = None
        self.edge_threshold = gc.EDGE_THRESHOLD
        self.instances: List['Cell'] = []
        self.hovered_edge: Optional[int] = None  # Track which edge is being hovered

        self.rect = pygame.Rect((self.c, self.r, gc.CELL_SIZE, gc.CELL_SIZE))

        self.left = self.rect.left
        self.top = self.rect.top
        self.right = self.rect.right
        self.bottom = self.rect.bottom

        self.edges: Dict[int, List[Tuple[int, int]]] = {
            self.left: [(self.left, self.top), (self.left, self.bottom)],
            self.top: [(self.left, self.top), (self.right, self.top)],
            self.right: [(self.right, self.top), (self.right, self.bottom)],
            self.bottom: [(self.left, self.bottom), (self.right, self.bottom)]
        }

        # Sides = [LEFT, TOP, RIGHT, BOTTOM]
        self.sides: List[bool] = [False, False, False, False]

    def set_instances(self, items: List['Cell']) -> None:
        """Set the list of cell instances.

        Args:
            items: List of Cell objects to set as instances
        """
        self.instances = items.copy()

    def get_instances(self) -> List['Cell']:
        """Get a copy of the cell instances list.

        Returns:
            A copy of the cell instances list
        """
        return self.instances.copy()

    def update(self, window_panel: pygame.Surface) -> None:
        """Update the cell's visual representation.

        Draws the cell's current state to the window, including any completed
        sides and the cell fill if completed.

        Args:
            window_panel: Pygame surface to draw on
        """
        if all(self.sides):
            pygame.draw.rect(window_panel, self.color, self.rect)
            if self.text:
                text = font.render(self.text, True, gc.COLORS['BLACK'])
                window_panel.blit(text, (self.rect.centerx - 10, self.rect.centery - 15))

        # Draw completed lines
        for i, side in enumerate(self.sides):
            if side:
                edge_side = list(self.edges.keys())[i]
                line_start = tuple(
                    v - 1 if v == edge_side else v for v in self.edges[edge_side][0])
                line_end = tuple(
                    v - 1 if v == edge_side else v for v in self.edges[edge_side][1])
                pygame.draw.line(window_panel, gc.COLORS['BLACK'],
                               line_start, line_end, 4)
            # Draw hover effect
            elif self.hovered_edge == i:
                edge_side = list(self.edges.keys())[i]
                line_start = tuple(
                    v - 1 if v == edge_side else v for v in self.edges[edge_side][0])
                line_end = tuple(
                    v - 1 if v == edge_side else v for v in self.edges[edge_side][1])
                # Draw a semi-transparent line for hover effect
                hover_surface = pygame.Surface((window_panel.get_width(), window_panel.get_height()), pygame.SRCALPHA)
                pygame.draw.line(hover_surface, (*gc.COLORS['BLUE'][:3], 128),  # Semi-transparent blue
                               line_start, line_end, 4)
                window_panel.blit(hover_surface, (0, 0))

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
                    cell_obj.color = gc.COLORS['GREEN'] if user == 'X' else gc.COLORS['RED']
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

    def check_hover(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if mouse is hovering near any edge and update hover state.

        Args:
            mouse_pos: Current mouse position (x, y)

        Returns:
            bool: True if mouse is hovering near an edge
        """
        x, y = mouse_pos
        dist_left = abs(x - self.rect.left)
        dist_right = abs(x - self.rect.right)
        dist_top = abs(y - self.rect.top)
        dist_bottom = abs(y - self.rect.bottom)

        # Check if mouse is within the cell's extended boundaries
        if (self.rect.left - self.edge_threshold <= x <= self.rect.right + self.edge_threshold and
            self.rect.top - self.edge_threshold <= y <= self.rect.bottom + self.edge_threshold):

            # Find the nearest edge
            distances = [
                (dist_left, 0),    # LEFT
                (dist_top, 1),     # TOP
                (dist_right, 2),   # RIGHT
                (dist_bottom, 3)   # BOTTOM
            ]

            min_dist, edge_index = min(distances)

            if min_dist <= self.edge_threshold and not self.sides[edge_index]:
                self.hovered_edge = edge_index
                return True

        self.hovered_edge = None
        return False

class Game:
    """Main game controller class for Dots and Boxes.

    This class manages the game state, including player turns, scoring,
    and game progression.

    Attributes:
        id (Optional[str]): Unique identifier for the game
        ready (bool): Whether the game is ready to start
        grid_ready (bool): Whether the game grid is initialized
        turn (int): Current player's turn (0 or 1)
        players (List[str]): List of player identifiers
        moves (List[bool]): List tracking if it's each player's turn
        player (str): Current player's identifier
        p1_score (int): Player 1's score
        p2_score (int): Player 2's score
        gameover (bool): Whether the game has ended
        cells_completed (int): Number of completed cells
    """

    def __init__(self) -> None:
        """Initialize a new game instance."""
        self.id: Optional[str] = None
        self.ready = False
        self.grid_ready = False
        self.reset(False)

    def set_gameID(self, id: str) -> None:
        """Set the game's unique identifier.

        Args:
            id: Unique identifier for the game
        """
        self.id = id

    def get_gameID(self) -> Optional[str]:
        """Get the game's unique identifier.

        Returns:
            The game's unique identifier or None if not set
        """
        return self.id

    def reset(self, reset_grid: bool = False) -> None:
        """Reset the game state.

        Args:
            reset_grid: Whether to also reset the game grid
        """
        self.turn = random.randint(0, 1)
        self.players = ['X', 'O']
        self.moves = [False] * len(self.players)
        self.player = self.players[self.turn]
        self.moves[self.turn] = True
        self.next_turn = False
        self.p1_score = self.p2_score = 0
        self.gameover = False
        self.cells_completed = 0
        if reset_grid:
            self.set_cells()

    def initialize_game(self, cells_dim: int) -> None:
        """Initialize the game grid with specified dimensions.

        Args:
            cells_dim: Number of cells per row/column
        """
        self.cells_dim = cells_dim
        ROWS = COLS = self.cells_dim
        PADDING = gc.PADDING // 2
        self.ROW_GRID = [r * gc.CELL_SIZE + 2 * PADDING for r in range(ROWS + 1)]
        self.HEIGHT = max(self.ROW_GRID) + PADDING
        self.COL_GRID = [c * gc.CELL_SIZE + PADDING for c in range(COLS + 1)]
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
                pygame.draw.circle(win, gc.COLORS['BLACK'], (c, r), 4)

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

    def draw_turn_indicator(self, window: pygame.Surface, width: int) -> None:
        """Draw an enhanced visual indicator for the current player's turn.

        Args:
            window: The game window surface to draw on
            width: Width of the game window
        """
        # Draw player scores with enhanced styling
        p1_color = gc.COLORS['BLUE']
        p2_color = gc.COLORS['RED']

        # Player 1 score and indicator
        p1_text = f'Player 1: {self.p1_score}'
        p1_img = font.render(p1_text, True, p1_color)
        p1_rect = p1_img.get_rect()
        text_pads = gc.PADDING // 3
        p1_rect.x, p1_rect.y = text_pads, 25

        # Player 2 score and indicator
        p2_text = f'Player 2: {self.p2_score}'
        p2_img = font.render(p2_text, True, p2_color)
        p2_rect = p2_img.get_rect()
        p2_rect.right, p2_rect.y = width - text_pads, 25

        # Draw the scores
        window.blit(p1_img, p1_rect)
        window.blit(p2_img, p2_rect)

        # Determine current player's rectangle and color
        current_rect = p1_rect if self.player == 'X' else p2_rect
        current_color = p1_color if self.player == 'X' else p2_color

        # Draw active player indicator
        indicator_height = 4
        # Bottom line
        pygame.draw.line(window, current_color,
                        (current_rect.x, current_rect.bottom + 2),
                        (current_rect.right, current_rect.bottom + 2),
                        indicator_height)

        # Draw a subtle background highlight for current player
        highlight_rect = current_rect.inflate(20, 10)
        highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        highlight_color = (*current_color[:3], 30)  # Very transparent version of player color
        pygame.draw.rect(highlight_surface, highlight_color, highlight_surface.get_rect(), border_radius=5)
        window.blit(highlight_surface, highlight_rect)

    def show_menu(self) -> int:
        """Display the game menu and handle grid size selection."""
        pygame.init()
        menu_window = pygame.display.set_mode((gc.MENU_WIDTH, gc.MENU_HEIGHT))
        pygame.display.set_caption("Dots and Boxes - Menu")

        title_font = pygame.font.SysFont(gc.FONT_NAME, gc.FONT_SIZE * 2)
        button_font = pygame.font.SysFont(gc.FONT_NAME, gc.FONT_SIZE)

        # Create buttons for each grid size
        buttons = []
        button_height = 60
        button_width = 200
        spacing = 30  # Increased spacing

        # Draw title
        title = title_font.render("Dots and Boxes", True, gc.COLORS['BLACK'])
        title_rect = title.get_rect(centerx=gc.MENU_WIDTH // 2, y=50)

        # Draw subtitle with more space
        subtitle = button_font.render("Select Grid Size", True, gc.COLORS['BLUE'])
        subtitle_rect = subtitle.get_rect(centerx=gc.MENU_WIDTH // 2, y=title_rect.bottom + 40)

        # Adjust starting position for buttons to be below subtitle
        start_y = subtitle_rect.bottom + spacing

        for size in gc.GRID_SIZES:
            button_rect = pygame.Rect(
                (gc.MENU_WIDTH - button_width) // 2,
                start_y,
                button_width,
                button_height
            )
            buttons.append((button_rect, size))
            start_y += button_height + spacing

        selected_size = gc.DEFAULT_GRID_SIZE
        running = True

        while running:
            menu_window.fill(gc.COLORS['WHITE'])

            # Draw title and subtitle
            menu_window.blit(title, title_rect)
            menu_window.blit(subtitle, subtitle_rect)

            # Handle events
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return selected_size

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button, size in buttons:
                        if button.collidepoint(mouse_pos):
                            selected_size = size
                            running = False

            # Draw buttons
            for button, size in buttons:
                # Check hover
                hover = button.collidepoint(mouse_pos)

                # Draw button background
                if hover:
                    pygame.draw.rect(menu_window, gc.COLORS['BLUE'], button)
                    text_color = gc.COLORS['WHITE']
                else:
                    pygame.draw.rect(menu_window, gc.COLORS['WHITE'], button)
                    pygame.draw.rect(menu_window, gc.COLORS['BLUE'], button, 2)
                    text_color = gc.COLORS['BLUE']

                # Draw button text
                text = button_font.render(f"{size} x {size} Grid", True, text_color)
                text_rect = text.get_rect(center=button.center)
                menu_window.blit(text, text_rect)

            pygame.display.flip()

        return selected_size

    def draw_game_over_screen(self, window: pygame.Surface, window_width: int, window_height: int) -> None:
        """Draw the game over screen with results and options."""
        # Create semi-transparent overlay for the entire window
        overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        window.blit(overlay, (0, 0))

        # Calculate panel dimensions - increased height
        panel_width = min(300, window_width - gc.PADDING)
        panel_height = min(400, window_height - gc.PADDING)  # Increased from 350 to 400

        # Center the panel
        panel_x = (window_width - panel_width) // 2
        panel_y = (window_height - panel_height) // 2

        # Create and draw the panel
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((*gc.COLORS['WHITE'][:3], 245))

        # Add decorative borders
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        pygame.draw.rect(panel, gc.COLORS['RED'], panel_rect, 2)
        pygame.draw.rect(panel, (*gc.COLORS['BLUE'][:3], 128), panel_rect.inflate(-4, -4), 2)

        # Game Over text - slightly reduced size
        game_over_font = pygame.font.SysFont(gc.FONT_NAME, int(panel_height * 0.10))
        over_text = game_over_font.render('Game Over', True, gc.COLORS['BLACK'])
        over_rect = over_text.get_rect(centerx=panel_width // 2, y=panel_height * 0.08)
        panel.blit(over_text, over_rect)

        # Scores - reduced size and spacing
        score_font = pygame.font.SysFont(gc.FONT_NAME, int(panel_height * 0.07))

        # Player 1 score
        p1_color = gc.COLORS['BLUE']
        p1_score_text = score_font.render(f'Player 1: {self.p1_score}', True, p1_color)
        p1_rect = p1_score_text.get_rect(
            centerx=panel_width // 2,
            y=over_rect.bottom + panel_height * 0.06
        )
        panel.blit(p1_score_text, p1_rect)

        # Player 2 score
        p2_color = gc.COLORS['RED']
        p2_score_text = score_font.render(f'Player 2: {self.p2_score}', True, p2_color)
        p2_rect = p2_score_text.get_rect(
            centerx=panel_width // 2,
            y=p1_rect.bottom + panel_height * 0.04
        )
        panel.blit(p2_score_text, p2_rect)

        # Winner announcement - adjusted position
        winner = '1' if self.p1_score > self.p2_score else '2'
        winner_color = p1_color if winner == '1' else p2_color
        winner_text = score_font.render(f'Player {winner} Wins!', True, winner_color)
        winner_rect = winner_text.get_rect(
            centerx=panel_width // 2,
            y=p2_rect.bottom + panel_height * 0.06
        )
        panel.blit(winner_text, winner_rect)

        # Options - adjusted font size and spacing
        options_font = pygame.font.SysFont(gc.FONT_NAME, int(panel_height * 0.05))

        # Restart option - moved up
        restart_text = options_font.render('Press R: Restart Game', True, gc.COLORS['BLACK'])
        restart_rect = restart_text.get_rect(
            centerx=panel_width // 2,
            y=winner_rect.bottom + panel_height * 0.10
        )
        panel.blit(restart_text, restart_rect)

        # Quit option - increased spacing from restart option
        quit_text = options_font.render('Press Q/ESC: Quit Game', True, gc.COLORS['BLACK'])
        quit_rect = quit_text.get_rect(
            centerx=panel_width // 2,
            y=restart_rect.bottom + panel_height * 0.08
        )
        panel.blit(quit_text, quit_rect)

        # Draw the panel on the window
        window.blit(panel, (panel_x, panel_y))

    def run(self):
        # Show menu and get selected grid size
        selected_size = self.show_menu()
        self.initialize_game(selected_size)

        WIDTH, HEIGHT = self.window_dimension()
        GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dots and Boxes")
        cells = self.get_cells()

        mouse_cord = None
        run = True
        clock = pygame.time.Clock()
        while run:
            clock.tick(60)
            GAME_WINDOW.fill(gc.COLORS['WHITE'])

            # Get current mouse position for hover effects
            current_mouse_pos = pygame.mouse.get_pos()

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
                pygame.draw.circle(GAME_WINDOW, gc.COLORS['RED'], mouse_cord, 2)

            # Update and draw cells, including hover effects
            for cell in cells:
                # Check for hover effects before handling clicks
                cell.check_hover(current_mouse_pos)

                if mouse_cord and cell.rect.collidepoint(mouse_cord):
                    self.is_cell_clicked(cell, mouse_cord)
                cell.update(GAME_WINDOW)

            # Draw the enhanced turn indicator
            self.draw_turn_indicator(GAME_WINDOW, WIDTH)

            if self.gameover:
                self.draw_game_over_screen(GAME_WINDOW, WIDTH, HEIGHT)

            pygame.display.update()

        pygame.quit()
