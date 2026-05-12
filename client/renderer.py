"""Client-side rendering with pygame."""

from typing import Callable

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

        self._draw_dispatch: dict[type, Callable] = {
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
        world: object,
        state: SceneState,
    ) -> None:
        if state != SceneState.PLAY:
            return

        hud_positions = {
            1: (10, 10),
            2: (self.config.WIDTH - 300, 10),
            3: (10, self.config.HEIGHT - 70),
            4: (self.config.WIDTH - 300, self.config.HEIGHT - 70),
        }
        
        for player_id in self.config.PLAYER_IDS:
            # Verifica se está no modo equipes para escolher a cor correta
            if getattr(world, 'game_mode', None) == self.config.GAME_MODE_TEAMS:
                color = self.config.PLAYER_COLORS_TEAMS.get(player_id, self.config.WHITE)
            else:
                color = self.config.PLAYER_COLORS.get(player_id, self.config.WHITE)
            
            score = world.scores.get(player_id, 0)
            lives = world.lives.get(player_id, 0)
            ship = world.ships.get(player_id)

            x, y = hud_positions[player_id]

            text = f"P{player_id} SCORE {score:06d} LIVES {lives}"
            label = self.font.render(text, True, color)
            self.screen.blit(label, (x, y))

            if ship is not None:
                self._draw_player_powerup_status(ship, x, y + 24, color)

        wave_label = self.font.render(
            f"WAVE {world.wave}",
            True,
            self.config.WHITE,
        )

        self.screen.blit(
            wave_label,
            (self.config.WIDTH // 2 - 45, self.config.HEIGHT - 70),
        )
        
        if getattr(world, 'game_mode', None) == self.config.GAME_MODE_TEAMS:
            self._draw_team_hud(world)

    def _draw_team_hud(self, world: object) -> None:
        """Desenha a pontuação e vidas da equipe no centro superior."""
        center_x = self.config.WIDTH // 2
        y = 10  # Abaixo do indicador de Wave

        for team_id in [self.config.TEAM_RED, self.config.TEAM_BLUE]:
            team_color = self.config.TEAM_COLORS[team_id]
            score = world.team_scores.get(team_id, 0)
            lives = world.team_lives.get(team_id, 0)
            
            text = f"TIME {'VERMELHO' if team_id == 1 else 'AZUL'}: {score:06d} | Vidas: {lives}"
            label = self.font.render(text, True, team_color)
            
            # Posiciona: time vermelho à esquerda do centro, azul à direita
            x = center_x - 420 if team_id == self.config.TEAM_RED else center_x + 50
            self.screen.blit(label, (x, y))

    def _draw_player_powerup_status(
        self,
        ship: Ship,
        x: int,
        y: int,
        color: tuple[int, int, int],
    ) -> None:
        status = []

        if getattr(ship, "triple_shot_active", False):
            status.append(f"TRP {ship.triple_shot_timer:.1f}s")

        if getattr(ship, "shield_active", False):
            status.append(f"SHD {ship.shield_timer:.1f}s")

        if not status:
            return

        label = self.font.render(" | ".join(status), True, color)
        self.screen.blit(label, (x, y))

    def draw_menu(self) -> None:
        center_x = self.config.WIDTH // 2

        self._draw_text(
            self.big,
            "ASTEROIDS PVP",
            center_x - 230,
            120,
        )

        self._draw_text(
            self.font,
            "MULTIPLAYER LOCAL - 4 JOGADORES",
            center_x - 210,
            240,
        )

        self._draw_text(
            self.font,
            "Cada jogador tem 3 vidas",
            center_x - 160,
            295,
        )

        self._draw_text(
            self.font,
            "Vence o ultimo jogador vivo",
            center_x - 170,
            330,
        )

        self._draw_text(
            self.font,
            "Analogico/D-Pad: mover",
            center_x - 160,
            385,
        )

        self._draw_text(
            self.font,
            "Botao 0: atirar | Botao 1: hyperspace",
            center_x - 240,
            420,
        )

        self._draw_text(
            self.font,
            "Pressione qualquer botao para iniciar",
            center_x - 230,
            490,
        )

        self._draw_text(
            self.font,
            "ESC: sair",
            center_x - 55,
            535,
        )

    def draw_game_over(self, world: object | None = None) -> None:
        center_x = self.config.WIDTH // 2

        self._draw_text(
            self.big,
            "FIM DE JOGO",
            center_x - 190,
            100,
        )

        if world is not None:
            game_mode = getattr(world, "game_mode", None)
            
            if game_mode == self.config.GAME_MODE_TEAMS:
                winner_team = getattr(world, "winner_team", None)
                
                if winner_team is not None and winner_team > 0:
                    team_name = "VERMELHO" if winner_team == self.config.TEAM_RED else "AZUL"
                    team_color = self.config.TEAM_COLORS.get(winner_team, self.config.WHITE)
                    
                    winner_label = self.big.render(
                        f"TIME {team_name} VENCEU!",
                        True,
                        team_color,
                    )
                    self.screen.blit(winner_label, (center_x - 250, 200))
                else:
                    self._draw_text(
                        self.big,
                        "EMPATE",
                        center_x - 110,
                        200,
                    )
                
                # Mostra ranking de times
                y = 330
                self._draw_text(
                    self.font,
                    "RANKING DE TIMES",
                    center_x - 90,
                    y - 45,
                )
                
                # Time vermelho
                red_color = self.config.TEAM_COLORS[self.config.TEAM_RED]
                red_score = world.team_scores.get(self.config.TEAM_RED, 0)
                red_lives = world.team_lives.get(self.config.TEAM_RED, 0)
                red_label = self.font.render(
                    f"1. TIME VERMELHO: {red_score:06d} pontos | vidas: {red_lives}",
                    True,
                    red_color,
                )
                self.screen.blit(red_label, (center_x - 190, y))
                y += 34
                
                # Time azul
                blue_color = self.config.TEAM_COLORS[self.config.TEAM_BLUE]
                blue_score = world.team_scores.get(self.config.TEAM_BLUE, 0)
                blue_lives = world.team_lives.get(self.config.TEAM_BLUE, 0)
                blue_label = self.font.render(
                    f"2. TIME AZUL: {blue_score:06d} pontos | vidas: {blue_lives}",
                    True,
                    blue_color,
                )
                self.screen.blit(blue_label, (center_x - 190, y))
                y += 34
                
                # Mostra ranking individual também
                y += 20
                self._draw_text(
                    self.font,
                    "RANKING INDIVIDUAL",
                    center_x - 90,
                    y,
                )
                y += 35  
            
            else:
                winner_id = getattr(world, "winner_id", None)
                if winner_id is not None:
                    winner_color = self.config.PLAYER_COLORS.get(
                        winner_id,
                        self.config.WHITE,
                    )

                    winner_label = self.big.render(
                        f"P{winner_id} VENCEU!",
                        True,
                        winner_color,
                    )

                    self.screen.blit(winner_label, (center_x - 190, 200))
                else:
                    self._draw_text(
                        self.big,
                        "EMPATE",
                        center_x - 110,
                        200,
                    )

                y = 330

                self._draw_text(
                self.font,
                "RANKING FINAL",
                center_x - 90,
                y - 45,
            )
            
            ranking = sorted(
                world.scores.items(),
                key=lambda item: item[1],
                reverse=True,
            )

            for index, item in enumerate(ranking, start=1):
                player_id, score = item
                lives = world.lives.get(player_id, 0)

                if game_mode == self.config.GAME_MODE_TEAMS:
                    color = self.config.PLAYER_COLORS_TEAMS.get(player_id, self.config.WHITE)
                else:
                    color = self.config.PLAYER_COLORS.get(player_id, self.config.WHITE)

                label = self.font.render(
                    f"{index}. P{player_id}: {score:06d} pontos | vidas: {lives}",
                    True,
                    color,
                )

                self.screen.blit(label, (center_x - 190, y))
                y += 34

        self._draw_text(
            self.font,
            "Pressione qualquer botao para escolher o modo",
            center_x - 270,
            self.config.HEIGHT - 80,
        )

        self._draw_text(
            self.font,
            "ESC: sair",
            center_x - 55,
            self.config.HEIGHT - 40,
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

        color = self.config.PLAYER_COLORS.get(
            getattr(bullet, "owner_id", 0),
            self.config.WHITE,
        )

        pg.draw.circle(
            self.screen,
            color,
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

        if ship.team_id > 0:
            # Modo times: usa a cor do time (ajustada por jogador)
            color = self._get_player_team_color(ship.player_id, ship.team_id)
        else:
            # Modo FFA ou sem time definido
            color = self.config.PLAYER_COLORS.get(ship.player_id, self.config.WHITE)

        pg.draw.polygon(self.screen, color, points, width=2)

        if ship.shield_active:
            center = (int(ship.pos.x), int(ship.pos.y))

            pg.draw.circle(
                self.screen,
                (135, 206, 250),
                center,
                ship.r + 8,
                width=2,
            )

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

        if ship.parry_on():
            center = (int(ship.pos.x), int(ship.pos.y))
            parry_radius = int(ship.r * 1.3)
            
            pg.draw.circle(
                self.screen,
                self.config.WHITE,
                center,
                parry_radius,
                width=3
            )

    def _get_player_team_color(self, player_id: int, team_id: int) -> tuple[int, int, int]:
        """Retorna a cor de um jogador no modo times."""
        # Usa PLAYER_COLORS_TEAMS do config para diferenciar dentro do time
        return self.config.PLAYER_COLORS_TEAMS.get(player_id, self.config.WHITE)

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

        pg.draw.circle(
            self.screen,
            self.config.PURPLE,
            center,
            black_hole.visual_r,
        )

        pg.draw.circle(
            self.screen,
            self.config.VIOLET,
            center,
            black_hole.visual_r - 4,
            width=2,
        )

        pg.draw.circle(
            self.screen,
            self.config.BLACK,
            center,
            black_hole.r,
        )

    def _draw_powerup(self, powerup: PowerUp) -> None:
        if not powerup.visible:
            return

        center = (int(powerup.pos.x), int(powerup.pos.y))
        color = powerup.get_color()

        pg.draw.circle(self.screen, color, center, powerup.r)
        pg.draw.circle(self.screen, self.config.WHITE, center, powerup.r, width=2)
        pg.draw.circle(self.screen, self.config.WHITE, center, 3)

    def draw_mode_select(self) -> None:
        """Desenha a tela de seleção de modo de jogo."""
        center_x = self.config.WIDTH // 2
        self._draw_text(self.big, "SELECIONE O MODO DE JOGO", center_x - 350, 200)

        self._draw_text(self.font, "1 - TODOS CONTRA TODOS (Free for All)", center_x - 260, 350)
        self._draw_text(self.font, "2 - EQUIPES (Vermelho vs Azul)", center_x - 240, 450)
        
        self._draw_text(self.font, "ESC: Voltar ao Menu", center_x - 130, 550)