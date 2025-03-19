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

    CELL_HIT = -1
    CELL_EMPTY = 0
    SHIP_CELLS = {}

    def __init__(self, board_config: BoardConfig):
        self.board_config = board_config

        self.board = np.zeros(shape=(self.board_config.n, self.board_config.n))

        id = 0
        board_size = self.board_config.n * self.board_config.n
        total_ship_area = 0
        min_l = np.inf
        min_b = np.inf
        min_l_id = []
        min_b_id = []

        for ship_index, ship in enumerate(self.board_config.ships):
            # make sure number of ships and number of positions in the list match
            if ship.count != len(ship.positions):
                raise ValueError("Ship count does not match with number of ships")
            
            total_ship_area += ship.length * ship.breadth * ship.count

            l = min(ship.length, ship.breadth)
            b = max(ship.length, ship.breadth)
            
            if l < min_l:
                min_l = l
                min_l_id = [ship_index]
            elif l == min_l:
                min_l_id.append(ship_index)

            if b < min_b:
                min_b = b
                min_b_id = [ship_index]
            elif b == min_b:
                min_b_id.append(ship_index)

        # make sure there exists a ship type with both smallest length and smallest breath
        is_valid = False
        for l in min_l_id:
            if l in min_b_id:
                is_valid = True
                break
        
        if not is_valid:
            raise ValueError(
                "No ship type with both smallest length and smallest breath"
            )

        # make sure area of board is larger than sum of areas of ships
        if total_ship_area > board_size:
            raise ValueError("Ships do not all fit on board")

        # Place ships on the board. Use id number to indicate ship
        for ship in self.board_config.ships:
            for position in ship.positions:
                id += 1
                self.SHIP_CELLS[id] = ship.length * ship.breadth
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
                            raise ValueError(f"Ship (id: {id}, pos: {position}) is out of bounds")

        print(self.board)
        print(self.SHIP_CELLS)

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
            self.SHIP_CELLS[ship_id] -= 1
            if self.SHIP_CELLS[ship_id] == 0:
                return AttackResult.SUNK
            else:
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
