"""Game configuration constants."""

import os

WIDTH = 1280
HEIGHT = 720
FPS = 60

MAX_PLAYERS = 4
PLAYER_IDS = (1, 2, 3, 4)
LOCAL_PLAYER_ID = 1

# --- Modos de Jogo ---
GAME_MODE_FFA = "free_for_all"  
GAME_MODE_TEAMS = "teams"       

# --- Configurações de Times (para o modo TEAMS) ---
TEAM_RED = 1
TEAM_BLUE = 2

# Mapeamento de time padrão: jogadores 1 e 2 no time vermelho, 3 e 4 no azul
TEAM_ASSIGNMENTS = {
    1: TEAM_RED,
    2: TEAM_RED,
    3: TEAM_BLUE,
    4: TEAM_BLUE,
}

# Cores para os times (usadas no HUD e talvez nas naves)
TEAM_COLORS = {
    TEAM_RED: (255, 80, 80),    # Vermelho
    TEAM_BLUE: (80, 80, 255),   # Azul
}

# Cores individuais DENTRO do time (para diferenciar jogadores do mesmo time)
PLAYER_COLORS_TEAMS = {
    # Time Vermelho
    1: (220, 50, 50),   # Vermelho mais escuro
    2: (255, 150, 150), # Vermelho claro

    # Time Azul
    3: (50, 50, 220),   # Azul escuro
    4: (150, 150, 255), # Azul claro
}

PLAYER_COLORS = {
    1: (80, 200, 255),
    2: (255, 100, 100),
    3: (120, 255, 120),
    4: (255, 220, 80),
}

PLAYER_SPAWN_POSITIONS = {
    1: (WIDTH * 0.20, HEIGHT * 0.25),
    2: (WIDTH * 0.80, HEIGHT * 0.25),
    3: (WIDTH * 0.20, HEIGHT * 0.75),
    4: (WIDTH * 0.80, HEIGHT * 0.75),
}

CONTROLLER_DEADZONE = 0.35
CONTROLLER_SHOOT_BUTTON = 0
CONTROLLER_HYPERSPACE_BUTTON = 1
CONTROLLER_THRUST_BUTTON = 7
CONTROLLER_THRUST_AXIS = 5

START_LIVES = 3
PLAYER_KILL_SCORE = 1000

SAFE_SPAWN_TIME = 2.0
WAVE_DELAY = 2.0
WAVE_BASE_COUNT = 3

SHIP_RADIUS = 15
SHIP_TURN_SPEED = 220.0
SHIP_THRUST = 220.0
SHIP_FRICTION = 0.995
SHIP_FIRE_RATE = 0.2
SHIP_BULLET_SPEED = 420.0
HYPERSPACE_COST = 250
SHIP_NOSE_ANGLE = 140.0
SHIP_NOSE_SCALE = 0.9
BULLET_SPAWN_OFFSET = 6

TRIPLE_SHOOT_DURATION = 5.0
TRIPLE_SHOOT_SPREAD = 15

TIME_STOP_DURATION = 4.0
SHIELD_DURATION = 3.0

POWERUP_CHANCE = 0.3
POWERUP_RADIUS = 12
POWERUP_SPEED = 40.0
POWERUP_TTL = 8.0

POWERUP_TYPES = {
    "triple_shot": {"color": (0, 255, 0)},
    "time_stop": {"color": (0, 255, 255)},
    "extra_life": {"color": (255, 215, 0)},
    "shield": {"color": (0, 0, 255)},
}

AST_VEL_MIN = 30.0
AST_VEL_MAX = 90.0
AST_POLY_STEPS = {"L": 12, "M": 10, "S": 8}
AST_POLY_JITTER_MIN = 0.75
AST_POLY_JITTER_MAX = 1.2
AST_MIN_SPAWN_DIST = 150
AST_SPLIT_SPEED_MULT = 1.2

AST_SIZES = {
    "L": {"r": 46, "score": 20, "split": ["M", "M"]},
    "M": {"r": 24, "score": 50, "split": ["S", "S"]},
    "S": {"r": 12, "score": 100, "split": []},
}

BULLET_RADIUS = 2
BULLET_TTL = 1.0
MAX_BULLETS_PER_PLAYER = 4

UFO_SPAWN_EVERY = 12.0
UFO_SPEED_BIG = 95.0
UFO_SPEED_SMALL = 120.0
UFO_BIG = {"r": 18, "score": 200}
UFO_SMALL = {"r": 12, "score": 1000}
UFO_FIRE_RATE_BIG = 0.8
UFO_FIRE_RATE_SMALL = 0.55
UFO_BULLET_SPEED = 360.0
UFO_BULLET_TTL = 1.3

UFO_AIM_JITTER_DEG_BIG = 28.0
UFO_AIM_JITTER_DEG_SMALL = 6.0
UFO_BIG_MISS_CHANCE = 0.35

BLACK_HOLE_RADIUS = 18
BLACK_HOLE_VISUAL_RADIUS = 28
BLACK_HOLE_STRENGTH = 450
BH_TIMER_MIN = 40
BH_TIMER_MAX = 100
BH_DURATION_MIN = 5
BH_DURATION_MAX = 10

WHITE = (240, 240, 240)
GRAY = (120, 120, 120)
BLACK = (0, 0, 0)
PURPLE = (40, 0, 80)
VIOLET = (120, 120, 255)

AUDIO_FREQUENCY = 44100
AUDIO_SIZE = -16
AUDIO_CHANNELS = 2
AUDIO_BUFFER = 512

FONT_SIZE_SMALL = 22
FONT_SIZE_LARGE = 64
FONT_NAME = "consolas"

RANDOM_SEED = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUND_PATH = os.path.join(BASE_DIR, "assets", "sounds")

PLAYER_SHOOT = "player_shoot.wav"
UFO_SHOOT = "ufo_shoot.wav"
ASTEROID_EXPLOSION = "asteroid_explosion.wav"
SHIP_EXPLOSION = "ship_explosion.wav"
THRUST_LOOP = "thrust_loop.wav"
UFO_SIREN_BIG = "ufo_siren_big.wav"
UFO_SIREN_SMALL = "ufo_siren_small.wav"