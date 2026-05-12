"""Local controller input reading and conversion to PlayerCommand."""

from __future__ import annotations

import pygame as pg

from core import config as C
from core.commands import PlayerCommand


class InputMapper:
    """Converts up to 4 local controllers into PlayerCommand objects."""

    def __init__(self) -> None:
        pg.joystick.init()

        self.joysticks: dict[int, object] = {}
        self.player_by_instance: dict[int, int] = {}

        self._shoot_pressed = {pid: False for pid in C.PLAYER_IDS}
        self._hyper_pressed = {pid: False for pid in C.PLAYER_IDS}

        self.refresh_joysticks()

    def refresh_joysticks(self) -> None:
        self.joysticks.clear()
        self.player_by_instance.clear()

        count = min(pg.joystick.get_count(), C.MAX_PLAYERS)

        for index in range(count):
            joy = pg.joystick.Joystick(index)
            joy.init()

            instance_id = joy.get_instance_id()
            player_id = index + 1

            self.joysticks[instance_id] = joy
            self.player_by_instance[instance_id] = player_id

    def handle_event(self, event: pg.event.Event) -> None:
        if event.type == pg.JOYDEVICEADDED:
            self.refresh_joysticks()
            return

        if event.type == pg.JOYDEVICEREMOVED:
            instance_id = event.instance_id

            if instance_id in self.joysticks:
                del self.joysticks[instance_id]

            if instance_id in self.player_by_instance:
                del self.player_by_instance[instance_id]

            self.refresh_joysticks()
            return

        if event.type != pg.JOYBUTTONDOWN:
            return

        instance_id = event.instance_id
        player_id = self.player_by_instance.get(instance_id)

        if player_id is None:
            return

        if event.button == C.CONTROLLER_SHOOT_BUTTON:
            self._shoot_pressed[player_id] = True

        elif event.button == C.CONTROLLER_HYPERSPACE_BUTTON:
            self._hyper_pressed[player_id] = True

    def build_commands(self) -> dict[int, PlayerCommand]:
        commands: dict[int, PlayerCommand] = {}

        for player_id in C.PLAYER_IDS:
            joy = self._get_joystick_by_player(player_id)

            if joy is None:
                commands[player_id] = PlayerCommand()
                continue

            commands[player_id] = self._build_command_for_joystick(player_id, joy)

        return commands

    def has_any_controller(self) -> bool:
        return len(self.joysticks) > 0

    def _get_joystick_by_player(self, player_id: int):
        for instance_id, mapped_player_id in self.player_by_instance.items():
            if mapped_player_id == player_id:
                return self.joysticks.get(instance_id)

        return None

    def _build_command_for_joystick(
        self,
        player_id: int,
        joy,
    ) -> PlayerCommand:
        x_axis = self._safe_axis(joy, 0)
        y_axis = self._safe_axis(joy, 1)
        thrust_axis = self._safe_axis(joy, C.CONTROLLER_THRUST_AXIS)

        hat_x, hat_y = self._safe_hat(joy, 0)

        rotate_left = x_axis < -C.CONTROLLER_DEADZONE or hat_x < 0
        rotate_right = x_axis > C.CONTROLLER_DEADZONE or hat_x > 0

        thrust = (
            y_axis < -C.CONTROLLER_DEADZONE
            or hat_y > 0
            or thrust_axis > C.CONTROLLER_DEADZONE
            or self._safe_button(joy, C.CONTROLLER_THRUST_BUTTON)
        )

        shoot = (
            self._shoot_pressed[player_id]
            or self._safe_button(joy, C.CONTROLLER_SHOOT_BUTTON)
        )

        hyperspace = self._hyper_pressed[player_id]

        self._shoot_pressed[player_id] = False
        self._hyper_pressed[player_id] = False

        return PlayerCommand(
            rotate_left=rotate_left,
            rotate_right=rotate_right,
            thrust=thrust,
            shoot=shoot,
            hyperspace=hyperspace,
        )

    def _safe_axis(self, joy, axis: int) -> float:
        if joy.get_numaxes() <= axis:
            return 0.0

        return joy.get_axis(axis)

    def _safe_button(self, joy, button: int) -> bool:
        if joy.get_numbuttons() <= button:
            return False

        return bool(joy.get_button(button))

    def _safe_hat(self, joy, hat: int) -> tuple[int, int]:
        if joy.get_numhats() <= hat:
            return 0, 0

        return joy.get_hat(hat)
    
    def get_mode_selection(self, event: pg.event.Event) -> int | None:
        """Retorna 1 para FFA, 2 para TEAMS, ou None se não for evento relevante."""
        if event.type == pg.JOYBUTTONDOWN:
            if event.button == 0:  # Botão 0 = FFA
                return 1
            elif event.button == 1:  # Botão 1 = TEAMS
                return 2
        return None