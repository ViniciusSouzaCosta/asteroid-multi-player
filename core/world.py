"""Game systems: World, waves and score."""

import math
from random import uniform
from typing import Dict

import pygame as pg

from core import config as C
from core.collisions import CollisionManager
from core.commands import PlayerCommand
from core.entities import Asteroid, Ship, UFO, BlackHole, PowerUp
from core.utils import Vec, rand_edge_pos

PlayerId = int


class World:
    """World state and game rules."""

    def __init__(self, game_mode: str = C.GAME_MODE_FFA) -> None:
        self.game_mode = game_mode
        self.ships: Dict[PlayerId, Ship] = {}
        self.teams: Dict[PlayerId, int] = {}
        self.bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.black_hole = None

        self.bh_timer = 0
        self.bh_duration = 0

        self.all_sprites = pg.sprite.Group()

        self.scores: Dict[PlayerId, int] = {}
        self.team_scores: Dict[int, int] = {C.TEAM_RED: 0, C.TEAM_BLUE: 0}
        self.lives: Dict[PlayerId, int] = {}
        self.team_lives: Dict[int, int] = {C.TEAM_RED: 0, C.TEAM_BLUE: 0}

        self.wave = 0
        self.wave_cool = float(C.WAVE_DELAY)
        self.ufo_timer = float(C.UFO_SPAWN_EVERY)

        self.events: list[str] = []
        self._collision_mgr = CollisionManager()

        self.game_over = False
        self.winner_id = None

        for player_id in C.PLAYER_IDS:
            self.spawn_player(player_id)

    def begin_frame(self) -> None:
        self.events.clear()

    def reset(self) -> None:
        self.__init__()

    def spawn_player(self, player_id: PlayerId) -> None:
        team_id = 0
        if self.game_mode == C.GAME_MODE_TEAMS:
            team_id = C.TEAM_ASSIGNMENTS.get(player_id, 0)
            self.teams[player_id] = team_id
            # Adiciona a vida inicial do jogador ao contador de vidas do time
            self.team_lives[team_id] = self.team_lives.get(team_id, 0) + C.START_LIVES
        
        x, y = C.PLAYER_SPAWN_POSITIONS.get(
            player_id,
            (C.WIDTH / 2, C.HEIGHT / 2),
        )

        ship = Ship(player_id, Vec(x, y), team_id=team_id)
        ship.invuln = float(C.SAFE_SPAWN_TIME)

        self.ships[player_id] = ship
        self.scores[player_id] = 0
        self.lives[player_id] = C.START_LIVES

        self.all_sprites.add(ship)

    def get_ship(self, player_id: PlayerId) -> Ship | None:
        return self.ships.get(player_id)

    def start_wave(self) -> None:
        self.wave += 1
        count = C.WAVE_BASE_COUNT + self.wave

        ship_positions = [s.pos for s in self.ships.values()]

        for _ in range(count):
            pos = rand_edge_pos()

            while any(
                (pos - sp).length() < C.AST_MIN_SPAWN_DIST
                for sp in ship_positions
            ):
                pos = rand_edge_pos()

            ang = uniform(0, math.tau)
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
            vel = Vec(math.cos(ang), math.sin(ang)) * speed

            self.spawn_asteroid(pos, vel, "L")

    def spawn_asteroid(self, pos: Vec, vel: Vec, size: str) -> None:
        ast = Asteroid(pos, vel, size)
        self.asteroids.add(ast)
        self.all_sprites.add(ast)

    def spawn_ufo(self) -> None:
        small = uniform(0, 1) < 0.5
        pos = rand_edge_pos()
        target = self._get_nearest_ship_pos(pos)

        ufo = UFO(pos, small, target_pos=target)

        self.ufos.add(ufo)
        self.all_sprites.add(ufo)

    def spawn_black_hole(self) -> None:
        pos = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))
        ship_positions = [s.pos for s in self.ships.values()]

        while any((pos - sp).length() < 200 for sp in ship_positions):
            pos = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))

        bh = BlackHole(pos)

        self.black_hole = bh
        self.all_sprites.add(bh)
        self.bh_duration = uniform(C.BH_DURATION_MIN, C.BH_DURATION_MAX)

    def update(
        self,
        dt: float,
        commands_by_player_id: Dict[PlayerId, PlayerCommand],
    ) -> None:
        self.begin_frame()

        if self.game_over:
            return

        self._apply_commands(dt, commands_by_player_id)

        self.all_sprites.update(dt)
        self._update_ufos(dt)
        self._update_timers(dt)
        self._handle_collisions()
        self._maybe_start_next_wave(dt)
        self._update_black_hole(dt)

    def _apply_commands(
        self,
        dt: float,
        commands_by_player_id: Dict[PlayerId, PlayerCommand],
    ) -> None:
        for player_id, cmd in commands_by_player_id.items():
            ship = self.get_ship(player_id)

            if ship is None:
                continue

            if self.lives.get(player_id, 0) <= 0:
                continue

            if cmd.hyperspace:
                ship.hyperspace()
                self.scores[player_id] = max(
                    0,
                    self.scores[player_id] - C.HYPERSPACE_COST,
                )

            if cmd.parry:
                ship.try_parry()

            fired = ship.apply_command(cmd, dt, self.bullets)

            if fired is None:
                continue

            if isinstance(fired, tuple):
                bullets = fired
            else:
                bullets = (fired,)

            for bullet in bullets:
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)

            self.events.append("player_shoot")

    def _update_ufos(self, dt: float) -> None:
        for ufo in list(self.ufos):
            ufo.target_pos = self._get_nearest_ship_pos(ufo.pos)
            ufo.update(dt)

            if not ufo.alive():
                continue

            ufo.target_pos = self._get_nearest_ship_pos(ufo.pos)

            bullet = ufo.try_fire()

            if bullet is not None:
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
                self.events.append("ufo_shoot")

            if not ufo.alive():
                self.ufos.remove(ufo)

    def _get_nearest_ship_pos(self, from_pos: Vec) -> Vec | None:
        nearest = None
        min_dist = float("inf")

        for ship in self.ships.values():
            d = (ship.pos - from_pos).length()

            if d < min_dist:
                min_dist = d
                nearest = ship

        return nearest.pos if nearest else None

    def _update_timers(self, dt: float) -> None:
        self.ufo_timer -= dt

        if self.ufo_timer <= 0.0:
            self.spawn_ufo()
            self.ufo_timer = float(C.UFO_SPAWN_EVERY)

    def _maybe_start_next_wave(self, dt: float) -> None:
        if self.asteroids:
            return

        self.wave_cool -= dt

        if self.wave_cool <= 0.0:
            self.start_wave()
            self.wave_cool = float(C.WAVE_DELAY)

    def _update_black_hole(self, dt: float) -> None:
        if self.black_hole:
            self.bh_duration -= dt

            if self.bh_duration <= 0:
                self.black_hole.kill()
                self.black_hole = None
                self.bh_timer = uniform(10, 20)

        else:
            self.bh_timer -= dt

            if self.bh_timer <= 0:
                self.spawn_black_hole()

        if self.black_hole:
            for ship in self.ships.values():
                dir_vec = self.black_hole.pos - ship.pos
                dist = dir_vec.length()

                if dist > 0:
                    dir_vec = dir_vec.normalize()
                    force = self.black_hole.strength / (dist + 1)
                    ship.vel += dir_vec * force * dt * 50

    def _handle_collisions(self) -> None:
        result = self._collision_mgr.resolve(
            self.ships,
            self.bullets,
            self.asteroids,
            self.ufos,
            self.powerups,
        )

        self.events.extend(result.events)

        for player_id, delta in result.score_deltas.items():
            if player_id in self.scores:
                self.scores[player_id] += delta
                
                # NOVO: Atualiza pontuação da equipe
                if self.game_mode == C.GAME_MODE_TEAMS:
                    team_id = self.teams.get(player_id, 0)
                    if team_id > 0:
                        self.team_scores[team_id] = self.team_scores.get(team_id, 0) + delta

        for pos, vel, size in result.asteroids_to_spawn:
            self.spawn_asteroid(pos, vel, size)

        for pos, powerup_type in result.powerups_to_spawn:
            self.spawn_powerup(pos, powerup_type)

        for player_id in result.extra_life_pickups:
            if player_id in self.lives:
                self.lives[player_id] += 1

        for player_id in result.ship_deaths:
            killer_id = result.death_causes.get(player_id)

            if killer_id is not None and killer_id in self.scores:
                self.scores[killer_id] += C.PLAYER_KILL_SCORE

                # Pontuação de equipe (se aplicável e não for fogo amigo)
                if self.game_mode == C.GAME_MODE_TEAMS:
                    killed_ship = self.get_ship(player_id)
                    killer_ship = self.get_ship(killer_id)
                    if killed_ship and killer_ship and killed_ship.team_id != killer_ship.team_id:
                        self.team_scores[killer_ship.team_id] += C.PLAYER_KILL_SCORE

            ship = self.get_ship(player_id)

            if ship is not None:
                self._ship_die(ship)

        if self.black_hole:
            for _player_id, ship in list(self.ships.items()):
                if ship.invuln > 0.0 or ship.shield_active:
                    continue

                dist = (self.black_hole.pos - ship.pos).length()

                if dist < (self.black_hole.r + ship.r):
                    self._ship_die(ship)

        self._check_pvp_winner()

    def _alive_players(self) -> list[PlayerId]:
        return [
            player_id
            for player_id in C.PLAYER_IDS
            if self.lives.get(player_id, 0) > 0
        ]

    def _check_pvp_winner(self) -> None:
        alive = self._alive_players()

        if len(alive) <= 1:
            self.game_over = True
            self.winner_id = alive[0] if alive else None

    def _ship_die(self, ship: Ship) -> None:
        pid = ship.player_id

        if self.lives.get(pid, 0) <= 0:
            return

        # 1. Diminui a vida do jogador e do time (se aplicável)
        self.lives[pid] = self.lives[pid] - 1
        if self.game_mode == C.GAME_MODE_TEAMS and ship.team_id > 0:
            self.team_lives[ship.team_id] = max(0, self.team_lives.get(ship.team_id, 0) - 1)

        self.events.append("ship_explosion")
        
        # 2. Se o jogador ainda tem vidas, respawn
        if self.lives[pid] > 0:
            x, y = C.PLAYER_SPAWN_POSITIONS.get(pid, (C.WIDTH / 2, C.HEIGHT / 2))
            ship.pos.xy = (x, y)
            ship.vel.xy = (0, 0)
            ship.angle = -90.0
            ship.invuln = float(C.SAFE_SPAWN_TIME)
            return

        # 3. Se o jogador ficou sem vidas, remove a nave
        ship.kill()
        if pid in self.ships:
            del self.ships[pid]

        # 4. Verifica condição de vitória
        self._check_winner()

        if self.lives[pid] <= 0:
            ship.kill()

            if pid in self.ships:
                del self.ships[pid]

            return

    def spawn_powerup(self, pos: Vec, powerup_type: str) -> None:
        powerup = PowerUp(pos, powerup_type)

        self.powerups.add(powerup)
        self.all_sprites.add(powerup)

    def _check_winner(self) -> None:
        """Verifica a condição de vitória baseada no modo de jogo."""
        if self.game_mode == C.GAME_MODE_FFA:
            self._check_pvp_winner()  # Método existente para FFA
        elif self.game_mode == C.GAME_MODE_TEAMS:
            self._check_team_winner()
    
    def _check_team_winner(self) -> None:
        """Verifica se uma equipe inteira foi eliminada."""
        red_alive = self.team_lives.get(C.TEAM_RED, 0) > 0
        blue_alive = self.team_lives.get(C.TEAM_BLUE, 0) > 0

        if not red_alive or not blue_alive:
            self.game_over = True
            if red_alive and not blue_alive:
                self.winner_team = C.TEAM_RED  # Novo atributo
            elif blue_alive and not red_alive:
                self.winner_team = C.TEAM_BLUE
            else:
                self.winner_team = 0  # Empate
