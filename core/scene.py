# core/scene.py

from enum import Enum, auto

class SceneState(Enum):
    MENU = auto()
    MODE_SELECT = auto()  # Novo estado
    PLAY = auto()
    GAME_OVER = auto()