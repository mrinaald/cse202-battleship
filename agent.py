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
    # # Specific constructor required if more paramters are required to initialize agent
    # def __init__(self):
    #     pass

    def seek(self):
        # for r in range(self.board_config.n, step_size):
        #     for c in range(self.board_config.n, step_size):
        pass

    def sink(self):
        pass

    def start_game(self) -> Tuple[int, str]:
        # TODO: Complete this
        pass


class RandomAgent(BaseAgent):
    """Randomized Agent"""
    seed: int

    def __init__(self, agent_view: BattleshipAgentBoard, seed: int = 0):
        super().__init__(agent_view)
        self.seed = seed
    
    def seek(self):
        pass

    def sink(self):
        pass

    def start_game(self) -> Tuple[int, str]:
        # TODO:
        pass
