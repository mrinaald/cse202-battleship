# -*- coding: utf-8 -*-
"""
Module defining different agents that could play the Battleship game.
"""
from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np

from board import BattleshipAgentBoard
from data_types import AttackResult


class BaseAgent(ABC):
    agent_board: BattleshipAgentBoard
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

    def seek(self) -> bool:
        """Seeks ships using a checkerboard-style search based on the smallest ship size."""
        large_side = max(self.step_size, self.step_size)
        small_side = min(self.step_size, self.step_size)

        for r in range(0, self.board_config.n, large_side):
            for c in range(0, self.board_config.n, large_side):
                for x in range(0, large_side, small_side):
                    ar, ac = r + x, c + x
                    if 0 <= ar < self.board_config.n and 0 <= ac < self.board_config.n and self.board[ar, ac] == 0:
                        result = self.agent_board.attack(ar, ac)
                        self.moves += 1
                        self.board[ar, ac] = 1  # Mark as visited
                        
                        if result == AttackResult.HIT:
                            self.sink(ar, ac)
                        
                        if self.ships_sunk == self.total_ships:
                            return True
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


# class OptimalAgent(BaseAgent):
#     """Our Optimal Algorithmic Agent"""
#     # # Specific constructor required if more paramters are required to initialize agent
#     # def __init__(self):
#     #     pass

#     def seek(self):
#         # for r in range(self.board_config.n, step_size):
#         #     for c in range(self.board_config.n, step_size):
#         pass

#     def sink(self):
#         pass

#     def start_game(self) -> Tuple[int, str]:
#         # TODO: Complete this
#         pass


# class RandomAgent(BaseAgent):
#     """Randomized Agent"""
#     seed: int

#     def __init__(self, agent_view: BattleshipAgentBoard, seed: int = 0):
#         super().__init__(agent_view)
#         self.seed = seed
    
#     def seek(self):
#         pass

#     def sink(self):
#         pass

#     def start_game(self) -> Tuple[int, str]:
#         # TODO:
#         pass



class RandomAgent(BaseAgent):
    """Randomized Agent"""
    
    def __init__(self, agent_board: BattleshipAgentBoard, seed: int = 0):
        super().__init__(agent_board)
        self.seed = seed
        random.seed(self.seed)
        self.available_cells = [(r, c) for r in range(self.board_config.n) for c in range(self.board_config.n)]
        random.shuffle(self.available_cells)  # Shuffle to introduce randomness

    def seek(self):
        """Selects random positions to attack until all ships are found and sunk."""
        while self.available_cells:
            r, c = self.available_cells.pop()
            if self.board[r, c] == 0:  # If cell is unvisited
                result = self.agent_board.attack(r, c)
                self.board[r, c] = 1  # Mark as visited

                if result == AttackResult.HIT:
                    self.sink(r, c)
                elif result == AttackResult.SUNK:
                    pass

    def sink(self, ar: int, ac: int):
        """Performs a BFS search to completely sink a ship after a hit is found."""
        queue = deque([(ar, ac)])
        while queue:
            i, j = queue.popleft()
            for ni, nj in [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]:
                if 0 <= ni < self.board_config.n and 0 <= nj < self.board_config.n and self.board[ni, nj] == 0:
                    result = self.agent_board.attack(ni, nj)
                    self.board[ni, nj] = 1  # Mark as visited
                    
                    if result == AttackResult.HIT:
                        queue.append((ni, nj))
                    elif result == AttackResult.SUNK:
                        pass

    def start_game(self) -> Tuple[int, str]:
        """Runs the randomized battleship algorithm."""
        self.seek()
        return sum(self.board.flatten() == 1), ""