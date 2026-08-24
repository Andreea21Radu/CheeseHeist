"""Global settings used by the Cheese Heist game."""

# -------------------------------------------------
# window
# -------------------------------------------------

WINDOW_TITLE = "Cheese Heist"

WINDOW_WIDTH = 1050
WINDOW_HEIGHT = 680

FPS = 60

# -------------------------------------------------
# maze
# -------------------------------------------------

GRID_ROWS = 15
GRID_COLUMNS = 21

TILE_SIZE = 28

MINIMUM_GRID_SIZE = 9

DEFAULT_MAZE_SEED = None

TRAP_COUNT = 5

# percentage of removable walls that become new paths
# increase this value for more alternative routes
EXTRA_PASSAGE_RATIO = 0.12

# -------------------------------------------------
# dificultate
# -------------------------------------------------

DIFFICULTY_LEVELS = (
    "easy",
    "medium",
    "hard",
)

DEFAULT_DIFFICULTY = "medium"

EASY_SCORE_LIMIT = 29.0
MEDIUM_SCORE_LIMIT = 32.0

# -------------------------------------------------
# algoritm genetic
# -------------------------------------------------

GA_POPULATION_SIZE = 10
GA_GENERATIONS = 10

# -------------------------------------------------
# Q-learning
# -------------------------------------------------

Q_LEARNING_EPISODES = 2500
Q_LEARNING_RATE = 0.2
Q_DISCOUNT_FACTOR = 0.95
Q_INITIAL_EPSILON = 1.0
Q_MIN_EPSILON = 0.05
Q_EPSILON_DECAY = 0.995

# -------------------------------------------------
# layout
# -------------------------------------------------

MAP_OFFSET_X = 30
MAP_OFFSET_Y = 75

SIDEBAR_WIDTH = 320
SIDEBAR_GAP = 20

# -------------------------------------------------
# movement
# -------------------------------------------------

MOVE_DELAY = 160

MOUSE_ANIMATION_DELAY = 110

# -------------------------------------------------
# temporary interface messages
# -------------------------------------------------

CHEESE_MESSAGE_DURATION = 1500

# -------------------------------------------------
# colors
# -------------------------------------------------

BACKGROUND_COLOR = (
    18,
    16,
    16,
)

PANEL_COLOR = (
    28,
    25,
    24,
)

OVERLAY_COLOR = (
    0,
    0,
    0,
    185,
)

TEXT_COLOR = (
    240,
    240,
    240,
)

SECONDARY_TEXT_COLOR = (
    185,
    180,
    175,
)

ACCENT_COLOR = (
    240,
    190,
    60,
)

SUCCESS_COLOR = (
    120,
    220,
    130,
)

WARNING_COLOR = (
    245,
    150,
    70,
)

GRID_LINE_COLOR = (
    40,
    36,
    34,
)

DEBUG_PATH_COLOR = (
    80,
    180,
    255,
)

# -------------------------------------------------
# debug
# -------------------------------------------------

SHOW_GRID_LINES = True

SHOW_BFS_PATH_BY_DEFAULT = False
