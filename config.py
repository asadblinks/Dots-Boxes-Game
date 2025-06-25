from dataclasses import dataclass, field
from typing import Dict, Tuple

def _get_default_colors() -> Dict[str, Tuple[int, int, int]]:
    """Return the default color configuration."""
    return {
        'WHITE': (255, 255, 255),
        'RED': (252, 91, 122),
        'BLUE': (78, 193, 246),
        'GREEN': (0, 255, 0),
        'BLACK': (12, 12, 12)
    }

@dataclass
class GameConfig:
    """Game configuration constants."""

    # Color configurations
    COLORS: Dict[str, Tuple[int, int, int]] = field(default_factory=_get_default_colors)

    # Display configurations
    FONT_SIZE: int = 24
    CELL_SIZE: int = 80
    PADDING: int = 100  # Used for all padding calculations
    EDGE_THRESHOLD: int = 10

    # Font configuration
    FONT_NAME: str = "verdana"

    # Game configurations
    DEFAULT_GRID_SIZE: int = 3

# Create a singleton instance
gc = GameConfig()

# Clean up namespace
del dataclass, field, Dict, Tuple, _get_default_colors