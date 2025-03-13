# -*- coding: utf-8 -*-
"""
Module defining the Battleship game board and APIs used by other modules
"""
from typing import Callable

import numpy as np

from data_types import BoardConfig, BoardViewConfig, AttackResult


class BattleshipBoard():
    """Game Board with ships placed on board"""
    board_config: BoardConfig
    board: np.array

    CELL_HIT = -1
    CELL_EMPTY = 0
    CELL_SHIP = 1

    def __init__(self, board_config: BoardConfig):
        self.board_config = board_config

        self.board = np.zeros(shape=(self.board_config.n, self.board_config.n))
        # TODO: Place ships on the board. Use CELL_SHIP to indicate ship
        for ship in self.board_config.ships:
            pass

    def attack(self, r, c) -> AttackResult:
        """API to hit particular cell on board"""
        if self.board[r, c] == self.CELL_EMPTY:
            # no ship was present, return MISS
            self.board[r, c] = self.CELL_HIT
            return AttackResult.MISS

        elif self.board[r, c] == self.CELL_HIT:
            # cell already hit, return HIT
            return AttackResult.HIT

        elif self.board[r, c] == self.CELL_SHIP:
            # We hit a ship. Return HIT or SUNK accordingly
            # TODO: Implement logic to return HIT or SUNK
            self.board[r, c] = self.CELL_HIT
            return AttackResult.HIT

        # Should not reach here
        return AttackResult.INVALID

    def get_proxy_API_for_attack(self) -> Callable[[int, int], AttackResult]:
        def proxy_attack(r: int, c: int) -> AttackResult:
            return self.attack(r, c)
        return proxy_attack


class BattleshipAgentBoard():
    """View of the board from Agent's perspective"""
    board_config: BoardViewConfig
    attack: Callable[[int, int], AttackResult]

    def __init__(self, board_config: BoardConfig, attack_fn: Callable[[int, int], AttackResult]):
        self.board_config = board_config.get_board_view()
        self.attack = attack_fn

    # def attack(self, r: int, c: int) -> AttackResult:
    #     return self.attack(r, c)
