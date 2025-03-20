# -*- coding: utf-8 -*-
"""
Module defining different agents that could play the Battleship game.
"""
from abc import ABC, abstractmethod
from typing import Tuple
from collections import deque
import random

import numpy as np

from board import BattleshipAgentBoard
from data_types import AttackResult, BoardViewConfig


class BaseAgent(ABC):
    agent_board: BattleshipAgentBoard
    board_config: BoardViewConfig
    board: np.array

    def __init__(self, agent_board: BattleshipAgentBoard):
        self.agent_board = agent_board
        self.board_config = self.agent_board.board_config
        self.board = np.zeros(shape=(self.board_config.n, self.board_config.n))

    @abstractmethod
    def start_game(self) -> Tuple[int, str]:
        """
        API to start the game for a given board view

        Parameters
        ----------
        None

        Returns
        -------
        int
            The number of moves taken by the agent. Will be -1 in case of error.
        str
            The error message in case the agent runs into an issue. Will be empty
            if the agent successfully finishes the game.
        """
        pass


class BruteForceAgent(BaseAgent):
    """Brute Force Agent"""

    def start_game(self) -> Tuple[int, str]:
        total_ships = sum([ship.count for ship in self.board_config.ships])
        ships_sunk = 0
        moves = 0

        for r in range(self.board_config.n):
            for c in range(self.board_config.n):
                result = self.agent_board.attack(r, c)
                moves += 1

                if result == AttackResult.INVALID:
                    return -1, "INVALID ERROR"

                if result == AttackResult.SUNK:
                    ships_sunk += 1

                if ships_sunk == total_ships:
                    return moves, ""

        return -1, "Unknown Error: Should not have happened"

class OptimalAgent(BaseAgent):
    """Our Optimal Algorithmic Agent"""

    def __init__(self, agent_board: BattleshipAgentBoard):
        super().__init__(agent_board)
        self.total_ships = sum([ship.count for ship in self.board_config.ships])
        self.ships_sunk = 0
        self.moves = 0
        self.step_size = min(ship.length * ship.breadth for ship in self.board_config.ships)

        min_small_side = np.inf
        min_large_side = np.inf
        for ship in self.board_config.ships:
            small_side = min(ship.length, ship.breadth)
            large_side = max(ship.length, ship.breadth)
            if small_side < min_small_side or large_side < min_large_side:
                min_small_side, min_large_side = small_side, large_side

        self.small_side = min_small_side
        self.large_side = min_large_side
        print(f"Min sized ship: {self.large_side}x{self.small_side}")

    def seek(self) -> bool:
        """Seeks ships using a checkerboard-style search based on the smallest ship size."""
        for r in range(0, self.board_config.n, self.large_side):
            for c in range(0, self.board_config.n, self.large_side):
                for x in range(0, self.large_side, self.small_side):
                    ar, ac = r + x, c + x
                    if 0 <= ar < self.board_config.n and 0 <= ac < self.board_config.n and self.board[ar, ac] == 0:
                        result = self.agent_board.attack(ar, ac)
                        self.moves += 1
                        self.board[ar, ac] = 1  # Mark as visited

                        if result == AttackResult.HIT:
                            self.sink(ar, ac)

                        if self.ships_sunk == self.total_ships:
                            return True

        print(f"Could not sink all ships: sunk={self.ships_sunk}, total={self.total_ships}")
        return False

    def sink(self, ar: int, ac: int):
        """Performs a BFS search to completely sink a ship after a hit is found."""
        queue = deque([(ar, ac)])
        while queue:
            i, j = queue.popleft()
            for ni, nj in [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]:
                if 0 <= ni < self.board_config.n and 0 <= nj < self.board_config.n and self.board[ni, nj] == 0:
                    result = self.agent_board.attack(ni, nj)
                    self.moves += 1
                    self.board[ni, nj] = 1  # Mark as visited

                    if result == AttackResult.HIT:
                        queue.append((ni, nj))
                    elif result == AttackResult.SUNK:
                        self.ships_sunk += 1

    def start_game(self) -> Tuple[int, str]:
        """Runs the optimal battleship algorithm."""
        if self.seek():
            return self.moves, ""
        return -1, "Unknown Error: Should not have happened"


class RandomAgent(BaseAgent):
    """Randomized Agent"""
    seed: int

    def __init__(self, agent_board: BattleshipAgentBoard, seed: int = 0):
        super().__init__(agent_board)
        self.seed = seed
        random.seed(self.seed)
        self.available_cells = [(r, c) for r in range(self.board_config.n) for c in range(self.board_config.n)]
        random.shuffle(self.available_cells)  # Shuffle to introduce randomness
        self.moves = 0
        self.ships_sunk = 0
        self.total_ships = sum([ship.count for ship in self.board_config.ships])

    def seek(self):
        """Selects random positions to attack until all ships are found and sunk."""
        while self.available_cells and self.ships_sunk < self.total_ships:
            r, c = self.available_cells.pop()
            if self.board[r, c] == 0:  # If cell is unvisited
                result = self.agent_board.attack(r, c)
                self.board[r, c] = 1  # Mark as visited
                self.moves += 1

                if result == AttackResult.HIT:
                    self.sink(r, c)
                elif result == AttackResult.SUNK:
                    self.ships_sunk += 1

    def sink(self, ar: int, ac: int):
        """Performs a BFS search to completely sink a ship after a hit is found."""
        queue = deque([(ar, ac)])
        while queue:
            i, j = queue.popleft()
            for ni, nj in [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]:
                if 0 <= ni < self.board_config.n and 0 <= nj < self.board_config.n and self.board[ni, nj] == 0:
                    result = self.agent_board.attack(ni, nj)
                    self.board[ni, nj] = 1  # Mark as visited
                    self.moves += 1

                    if result == AttackResult.HIT:
                        queue.append((ni, nj))
                    elif result == AttackResult.SUNK:
                        self.ships_sunk += 1

    def start_game(self) -> Tuple[int, str]:
        """Runs the randomized battleship algorithm."""
        self.seek()
        return self.moves, ""