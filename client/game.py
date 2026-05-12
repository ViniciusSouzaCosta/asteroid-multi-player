"""Game loop and scenes."""

import sys

import pygame as pg

from core import config as C
from core.scene import SceneState
from client.audio import load_sounds
from client.audio_manager import AudioManager
from client.controls import InputMapper
from client.renderer import Renderer
from core.world import World


class Game:
    """Orchestrates input -> update -> draw."""

    def __init__(self) -> None:
        pg.mixer.pre_init(
            C.AUDIO_FREQUENCY,
            C.AUDIO_SIZE,
            C.AUDIO_CHANNELS,
            C.AUDIO_BUFFER,
        )

        pg.init()
        pg.mixer.init()
        pg.joystick.init()

        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("Asteroids PvP Local")

        self.clock = pg.time.Clock()
        self.running = True

        self.font = pg.font.SysFont(C.FONT_NAME, C.FONT_SIZE_SMALL)
        self.big = pg.font.SysFont(C.FONT_NAME, C.FONT_SIZE_LARGE)

        self.renderer = Renderer(
            self.screen,
            config=C,
            fonts={"font": self.font, "big": self.big},
        )

        self.scene = SceneState.MENU
        self.world = World()
        self.input_mapper = InputMapper()

        self.sounds = load_sounds(C.SOUND_PATH)
        self.audio = AudioManager(self.sounds)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(C.FPS) / 1000.0

            self._handle_events()
            self._update(dt)
            self._draw()

        pg.quit()

    def _handle_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._quit()

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self._quit()

            self.input_mapper.handle_event(event)

            if self.scene == SceneState.MENU:
                if event.type in (pg.KEYDOWN, pg.JOYBUTTONDOWN):
                    self.world.reset()
                    self.scene = SceneState.PLAY
                    continue

            if self.scene == SceneState.GAME_OVER:
                if event.type in (pg.KEYDOWN, pg.JOYBUTTONDOWN):
                    self.world.reset()
                    self.scene = SceneState.PLAY
                    continue

    def _update(self, dt: float) -> None:
        if self.scene != SceneState.PLAY:
            return

        commands = self.input_mapper.build_commands()

        self.world.update(dt, commands)

        if self.world.game_over:
            self.audio.stop_all()
            self.scene = SceneState.GAME_OVER
            return

        any_thrust = any(cmd.thrust for cmd in commands.values())

        self.audio.update_thrust(any_thrust)
        self.audio.update_ufo_siren(list(self.world.ufos))
        self.audio.play_events(self.world.events)

    def _draw(self) -> None:
        self.renderer.clear()

        if self.scene == SceneState.MENU:
            self.renderer.draw_menu()
            pg.display.flip()
            return

        if self.scene == SceneState.GAME_OVER:
            self.renderer.draw_game_over(self.world)
            pg.display.flip()
            return

        self.renderer.draw_world(self.world)
        self.renderer.draw_hud(self.world, self.scene)

        pg.display.flip()

    def _quit(self) -> None:
        self.running = False
        pg.quit()
        sys.exit(0)