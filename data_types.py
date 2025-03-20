# -*- coding: utf-8 -*-
"""
Module describing different data types
"""
import json

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ShipView():
    """View of Ship for Agent in Battleship game"""
    length: int
    breadth: int
    count: int


@dataclass
class BoardViewConfig():
    """Battleship Game Board view for Agent"""
    n: int
    ships: List[ShipView]


@dataclass
class Ship():
    """Ship in Battleship game"""
    length: int
    breadth: int
    count: int
    positions: List[List[int]]

    @classmethod
    def from_dict(cls, ship: Dict[str, Any]) -> "Ship":
        return cls(ship["length"], ship["breadth"], ship["count"], ship["positions"])

    def to_dict(self) -> Dict[str, int]:
        return {
            "length": self.length,
            "breadth": self.breadth,
            "count": self.count,
            "positions": self.positions,
        }

    def get_ship_view(self) -> ShipView:
        return ShipView(self.length, self.breadth, self.count)


@dataclass
class BoardConfig():
    """Game Board for a Battleship game"""
    n: int
    ships: List[Ship]

    @classmethod
    def from_json(cls, json_file: str) -> "BoardConfig":
        with open(json_file, "r") as f:
            config = json.load(f)
        return cls.from_dict(config)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "BoardConfig":
        n = config["n"]

        ships: List[Ship] = [None] * len(config["ships"])

        for i, ship in enumerate(config["ships"]):
            ships[i] = Ship.from_dict(ship)

        return cls(n, ships)

    def to_json(self, output_file: str):
        with open(output_file, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n": self.n,
            "ships": [ship.to_dict() for ship in self.ships]
        }

    def get_board_view(self):
        return BoardViewConfig(self.n, [ship.get_ship_view() for ship in self.ships])


class AttackResult(Enum):
    HIT = auto()
    MISS = auto()
    SUNK = auto()
    INVALID = auto()

@dataclass
class ExperimentConfig():
    boards: List[BoardConfig]
    runs_per_board: int


if __name__ == "__main__":
    with open("./data/boards/example_board.json", "r") as f:
        config = json.load(f)

    print(json.dumps(config, indent=2))
    BoardConfig.from_json("./data/boards/example_board.json")
