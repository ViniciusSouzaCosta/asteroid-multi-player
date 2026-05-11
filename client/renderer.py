"""Client-side rendering (pygame)."""

import pygame as pg

from core import config as C
from core.scene import SceneState
from core.entities import Asteroid, Bullet, Ship, UFO, BlackHole, PowerUp


class Renderer:
    """Draws scenes and entities without coupling game rules to Game."""

    def __init__(
        self,
        screen: pg.Surface,
        config: object = C,
        fonts: dict[str, pg.font.Font] | None = None,
    ) -> None:
        self.screen = screen
        self.config = config
        safe_fonts = fonts or {}
        self.font = safe_fonts["font"]
        self.big = safe_fonts["big"]

        self._draw_dispatch: dict[type, callable] = {
            Bullet: self._draw_bullet,
            Asteroid: self._draw_asteroid,
            Ship: self._draw_ship,
            UFO: self._draw_ufo,
            BlackHole: self._draw_black_hole,
            PowerUp: self._draw_powerup,
        }

    def clear(self) -> None:
        self.screen.fill(self.config.BLACK)

    def draw_world(self, world: object) -> None:
        sprites = getattr(world, "all_sprites", [])
        for sprite in sprites:
            drawer = self._draw_dispatch.get(type(sprite))
            if drawer is not None:
                drawer(sprite)

    def draw_hud(
        self,
        score: int,
        lives: int,
        wave: int,
        state: SceneState,
        triple_shot_timer: float = 0.0,
        time_stop_timer: float = 0.0,
        shield_timer: float = 0.0,
    ) -> None:
        if state != SceneState.PLAY:
            return

        text = f"SCORE {score:06d}   LIVES {lives}   WAVE {wave}"
        label = self.font.render(text, True, self.config.WHITE)
        self.screen.blit(label, (10, 10))

        # Powerup Time Bars
        y_offset = 40 
        bar_w = 150
        bar_h = 12

        if triple_shot_timer > 0:
            pct = max(0.0, triple_shot_timer / self.config.TRIPLE_SHOOT_DURATION)
            
            pg.draw.rect(self.screen, self.config.GRAY, (10, y_offset, bar_w, bar_h))
            pg.draw.rect(self.screen, (0, 255, 0), (10, y_offset, int(bar_w * pct), bar_h))
            
            lbl = self.font.render(f"TRIPLE SHOT {triple_shot_timer:.1f}s", True, self.config.WHITE)
            self.screen.blit(lbl, (bar_w + 20, y_offset - 4))
            y_offset += 25

        if time_stop_timer > 0:
            max_time = getattr(self.config, 'TIME_STOP_DURATION', 4.0)
            pct = max(0.0, time_stop_timer / max_time)
            
            pg.draw.rect(self.screen, self.config.GRAY, (10, y_offset, bar_w, bar_h))
            pg.draw.rect(self.screen, (0, 255, 255), (10, y_offset, int(bar_w * pct), bar_h))
            
            lbl = self.font.render(f"TIME STOP {time_stop_timer:.1f}s", True, self.config.WHITE)
            self.screen.blit(lbl, (bar_w + 20, y_offset - 4))

        if shield_timer > 0:
            max_time = getattr(self.config, 'SHIELD_DURATION', 3.0)
            pct = max(0.0, shield_timer / max_time)
            
            pg.draw.rect(self.screen, self.config.GRAY, (10, y_offset, bar_w, bar_h))
            pg.draw.rect(self.screen, (135, 206, 250), (10, y_offset, int(bar_w * pct), bar_h))
            
            lbl = self.font.render(f"SHIELD {shield_timer:.1f}s", True, self.config.WHITE)
            self.screen.blit(lbl, (bar_w + 20, y_offset - 4))

    def draw_menu(self) -> None:
        self._draw_text(
            self.big,
            "ASTEROIDS",
            self.config.WIDTH // 2 - 170,
            200,
        )
        self._draw_text(
            self.font,
            "Press any key",
            self.config.WIDTH // 2 - 170,
            350,
        )

    def draw_game_over(self) -> None:
        self._draw_text(
            self.big,
            "GAME OVER",
            self.config.WIDTH // 2 - 170,
            260,
        )
        self._draw_text(
            self.font,
            "Press any key",
            self.config.WIDTH // 2 - 170,
            340,
        )

    def _draw_text(
        self,
        font: pg.font.Font,
        text: str,
        x: int,
        y: int,
    ) -> None:
        label = font.render(text, True, self.config.WHITE)
        self.screen.blit(label, (x, y))

    def _draw_bullet(self, bullet: Bullet) -> None:
        center = (int(bullet.pos.x), int(bullet.pos.y))
        pg.draw.circle(
            self.screen,
            self.config.WHITE,
            center,
            bullet.r,
            width=1,
        )

    def _draw_asteroid(self, asteroid: Asteroid) -> None:
        points = []
        for point in asteroid.poly:
            px = int(asteroid.pos.x + point.x)
            py = int(asteroid.pos.y + point.y)
            points.append((px, py))
        pg.draw.polygon(self.screen, self.config.WHITE, points, width=1)

    def _draw_ship(self, ship: Ship) -> None:
        p1, p2, p3 = ship.ship_points()
        points = [
            (int(p1.x), int(p1.y)),
            (int(p2.x), int(p2.y)),
            (int(p3.x), int(p3.y)),
        ]
        pg.draw.polygon(self.screen, self.config.WHITE, points, width=1)

        if ship.shield_active:
            center = (int(ship.pos.x), int(ship.pos.y))
            # Círculo do escudo (semi-transparente seria ideal, mas pygame básico não suporta bem)
            pg.draw.circle(
                self.screen,
                (135, 206, 250),  # Azul claro
                center,
                ship.r + 8,
                width=2,
            )
            # Efeito de pulsação baseado no timer
            if int(ship.shield_timer * 5) % 2 == 0:
                pg.draw.circle(
                    self.screen,
                    (0, 0, 255),
                    center,
                    ship.r + 12,
                    width=1,
                )

        if ship.invuln > 0.0 and int(ship.invuln * 10) % 2 == 0:
            center = (int(ship.pos.x), int(ship.pos.y))
            pg.draw.circle(
                self.screen,
                self.config.WHITE,
                center,
                ship.r + 6,
                width=1,
            )

    def _draw_ufo(self, ufo: UFO) -> None:
        width = ufo.r * 2
        height = ufo.r

        body = pg.Rect(0, 0, width, height)
        body.center = (int(ufo.pos.x), int(ufo.pos.y))
        pg.draw.ellipse(self.screen, self.config.WHITE, body, width=1)

        cup = pg.Rect(0, 0, int(width * 0.5), int(height * 0.7))
        cup.center = (int(ufo.pos.x), int(ufo.pos.y - height * 0.3))
        pg.draw.ellipse(self.screen, self.config.WHITE, cup, width=1)

    def _draw_black_hole(self, black_hole: BlackHole) -> None:
        center = (int(black_hole.pos.x), int(black_hole.pos.y))

        # Aura visual
        pg.draw.circle(self.screen, self.config.PURPLE, center, black_hole.visual_r)
        # Anel interno
        pg.draw.circle(
            self.screen, self.config.VIOLET, center, black_hole.visual_r - 4, width=2
        )
         # O buraco negro em si (centro)
        pg.draw.circle(self.screen, self.config.BLACK, center, black_hole.r)

    def _draw_powerup(self, powerup) -> None:
        """Desenha um power-up com efeito de piscar."""
        if not powerup.visible:
            return
            
        center = (int(powerup.pos.x), int(powerup.pos.y))
        color = powerup.get_color()
        
        # Desenha o power-up principal
        pg.draw.circle(self.screen, color, center, powerup.r)
        
        # Adiciona um brilho/borda branca
        pg.draw.circle(self.screen, self.config.WHITE, center, powerup.r, width=2)
        
        # Efeito visual extra: um ponto brilhante no centro
        pg.draw.circle(self.screen, self.config.WHITE, center, 3)