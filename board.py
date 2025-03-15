# -*- coding: utf-8 -*-
"""
Module defining the Battleship game board and APIs used by other modules
"""
from typing import Callable

import numpy as np

from data_types import BoardConfig, BoardViewConfig, AttackResult


class BattleshipBoard:
    """Game Board with ships placed on board"""

    board_config: BoardConfig
    board: np.array

    CELL_HIT = -2
    CELL_EMPTY = 0

    def __init__(self, board_config: BoardConfig):
        self.board_config = board_config

        self.board = np.zeros(shape=(self.board_config.n, self.board_config.n))

        id = 0
        board_size = self.board_config.n * self.board_config.n
        total_ship_area = 0
        min_l = np.inf
        min_b = np.inf
        min_l_id = 0
        min_b_id = 0

        # make sure number of ships and number of positions in the list match
        for ship in self.board_config.ships:
            if ship.count != len(ship.positions):
                raise ValueError("Ship count does not match with number of ships")
            total_ship_area += ship.length * ship.breadth * ship.count
            if ship.length < min_l:
                min_l = ship.length
                min_l_id = self.board_config.ships.index(ship)
            if ship.breadth < min_b:
                min_b = ship.breadth
                min_b_id = self.board_config.ships.index(ship)

        # make sure there exists a ship type with both smallest length and smallest breath
        if min_l_id != min_b_id:
            raise ValueError(
                "No ship type with both smallest length and smallest breath"
            )

        # make sure area of board is larger than sum of areas of ships
        if total_ship_area > board_size:
            raise ValueError("Ships do not all fit on board")

        # TODO: Place ships on the board. Use CELL_SHIP to indicate ship
        for ship in self.board_config.ships:
            id += 1
            for position in ship.positions:
                x, y = position
                # place the ship on the board
                for i in range(ship.length):
                    for j in range(ship.breadth):
                        if x + i < self.board_config.n and y + j < self.board_config.n:
                            # make sure ships don't overlap
                            if self.board[x + i, y + j] != 0:
                                raise ValueError(
                                    "Ship (id: {id}) overlaps with Ship (id: {self.board[x + i, y + j]})"
                                )
                            self.board[x + i, y + j] = id
                        else:  # make sure ships are all withing bounds of board
                            raise ValueError("Ship (id: {id}) is out of bounds")

        print(self.board)
        # TODO: Put assertiions to ensure our input constraints

    def attack(self, r, c) -> AttackResult:
        """API to hit particular cell on board"""
        if self.board[r, c] == self.CELL_EMPTY:
            # no ship was present, return MISS
            self.board[r, c] = self.CELL_HIT
            return AttackResult.MISS

        elif self.board[r, c] == self.CELL_HIT:
            # cell already hit, return HIT
            return AttackResult.HIT

        elif self.board[r, c] > 0:
            # We hit a ship. Return HIT or SUNK accordingly
            # TODO: Implement logic to return HIT or SUNK
            ship_id = self.board[r, c]
            self.board[r, c] = self.CELL_HIT
            return AttackResult.HIT  # Or AttackResult.SUNK

        # Should not reach here
        return AttackResult.INVALID

    def get_proxy_API_for_attack(self) -> Callable[[int, int], AttackResult]:
        def proxy_attack(r: int, c: int) -> AttackResult:
            return self.attack(r, c)

        return proxy_attack


class BattleshipAgentBoard:
    """View of the board from Agent's perspective"""

    board_config: BoardViewConfig
    attack: Callable[[int, int], AttackResult]

    def __init__(
        self, board_config: BoardConfig, attack_fn: Callable[[int, int], AttackResult]
    ):
        self.board_config = board_config.get_board_view()
        self.attack = attack_fn

    # def attack(self, r: int, c: int) -> AttackResult:
    #     return self.attack(r, c)
