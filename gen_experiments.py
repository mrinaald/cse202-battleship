# -*- coding: utf-8 -*-
"""
Module to generate random boards for experimentation purposes
"""
import argparse
import json
import os
import random
from typing import Any, Dict, List, Tuple

import numpy as np
from tqdm import tqdm, trange

from data_types import BoardConfig, Ship


DEBUG = False
RNG = np.random.default_rng(seed=13)


def write_boards_to_json(boards_data: Dict[int, Dict[str, List[BoardConfig]]], filepath: str):
    out_data = {
        k1: {
            k2: [board.to_dict() for board in v2]
            for k2, v2 in v1.items()
        }
        for k1, v1 in boards_data.items()
    }

    with open(filepath, "w") as f:
        json.dump(out_data, f, indent=2)


def place_ship_on_board(board: np.ndarray, ship_size: Tuple[int, int], count: int = 1) -> List[List[int]]:
    n = board.shape[0]
    positions: List[List[int]] = []

    tries = 0
    while len(positions) < count and tries < 10:
        # row, col = RNG.integers(0, n, size=2)
        row = RNG.integers(0, n-ship_size[0], endpoint=True, dtype=int)
        col = RNG.integers(0, n-ship_size[1], endpoint=True, dtype=int)
        tries += 1

        if row + ship_size[0] > n or col + ship_size[1] > n:
            continue

        if np.any(board[row:row+ship_size[0], col:col+ship_size[1]]):
            continue

        board[row:row+ship_size[0], col:col+ship_size[1]] = 1
        positions.append([row, col])
        tries = 0

    return positions


def generate_boards(n: int, ship_area_percentage: float, min_ship_size: Tuple[int, int], num_boards: int=1) -> List[BoardConfig]:
    boards: List[BoardConfig] = []
    board_area = float(n*n)

    max_ship_lsize = max(min_ship_size[0], int(n*0.2)) if min_ship_size[0] <= min_ship_size[1] else int(n*0.7)
    max_ship_bsize = max(min_ship_size[1], int(n*0.2)) if min_ship_size[1] < min_ship_size[0] else int(n*0.7)
    # max_ship_lsize = int(n*0.7)
    # max_ship_bsize = int(n*0.7)
    # print(n, max_ship_lsize, max_ship_bsize)

    l_range = list(range(min_ship_size[0], max_ship_lsize+1))
    b_range = list(range(min_ship_size[1], max_ship_bsize+1))
    alpha = 0.4
    if len(l_range) == 1:
        l_probs = [1.0]
    else:
        l_probs = [alpha] + ([(1-alpha)/(len(l_range) - 1)]*(len(l_range) - 1))

    if len(b_range) == 1:
        b_probs = [1.0]
    else:
        b_probs = [alpha] + ([(1-alpha)/(len(b_range) - 1)]*(len(b_range) - 1))

    for _ in range(num_boards):
        ships: List[Ship] = []

        ship_area = 0.0
        total_ships = 0
        game_board = np.zeros((n, n), dtype=np.int32)

        count = 1 if RNG.random() < 0.5 else 2

        positions = place_ship_on_board(game_board, min_ship_size, count=count)
        assert len(positions) == count

        ship_area += (count * min_ship_size[0] * min_ship_size[1])
        total_ships += count

        ships.append(Ship(
            length=min_ship_size[0],
            breadth=min_ship_size[1],
            count=count,
            positions=positions,
        ))

        while (ship_area / board_area) < ship_area_percentage:
            count = 1 if RNG.random() < 0.5 else 2

            # l = int(RNG.integers(min_ship_size[0], max_ship_lsize, endpoint=True))
            # b = int(RNG.integers(min_ship_size[1], max_ship_bsize, endpoint=True))
            l = int(RNG.choice(l_range, p=l_probs))
            b = int(RNG.choice(b_range, p=b_probs))
            ship_size = (l, b)
            if ship_size == min_ship_size and (len(l_range) > 1 or len(b_range) > 1):
                # Gets stuck in infinity loop if following unused statement is removed
                # Maybe some issue with random generator that randomly keeps generating same number.
                _ = int(RNG.choice(l_range, p=l_probs))

                continue

            if (ship_area + (count * ship_size[0] * ship_size[1])) / board_area > (ship_area_percentage + 0.1):
                # if total area crosses ship_area_percentage + 10%, don't place this ship
                continue

            positions = place_ship_on_board(game_board, ship_size, count=count)
            if len(positions) == 0:
                continue
            count = len(positions)

            ship_area += (count * ship_size[0] * ship_size[1])
            total_ships += count

            ships.append(Ship(
                length=ship_size[0],
                breadth=ship_size[1],
                count=count,
                positions=positions,
            ))
            if DEBUG:
                print(ship_size, count)

        boards.append(BoardConfig(n=n, ships=ships))
        if DEBUG:
            # print(json.dumps(boards[-1].to_dict(), indent=2))
            print(total_ships, game_board.sum(), ship_area, ship_area / board_area)
            print(game_board)

    return boards


def get_random_boards(n: int, num_boards: int=1) -> Dict[str, List[BoardConfig]]:
    data: Dict[str, List[BoardConfig]] = {}

    side1 = int(RNG.integers(2, 5, endpoint=True))
    side2 = int(RNG.integers(2, 5, endpoint=True))
    rl = min(side1, side2)
    rb = max(side1, side2)

    for perc in tqdm([0.20, 0.40], leave=False):
        for min_ship_size in tqdm([(1,2), (2,3), (rl, rb)], leave=False):
            boards = generate_boards(n, perc, min_ship_size, num_boards)
            key = f"p{perc:.2f}-s{min_ship_size[0]}x{min_ship_size[1]}"
            data[key] = boards
            if DEBUG:
                return data

    return data

def main(args: argparse.Namespace):
    if args.debug:
        global DEBUG
        DEBUG = True

    board_size = [10, 50, 100, 500, 1000, 5000]
    # board_size = [10, 50, 100]
    # board_size = [1000, 5000]

    os.makedirs(args.output_dir, exist_ok=True)

    for i in trange(1, len(board_size)):
        low = board_size[i-1]
        high = board_size[i]

        num_boards = min(int((high-low)*0.2), 100)

        random_sizes = RNG.choice(range(low, high), replace=False, size=(num_boards,))
        random_sizes = random_sizes.tolist()

        if low not in random_sizes:
            random_sizes.append(low)
        random_sizes.sort()

        filepath = f"experiment_{low}-{high}.json"
        filepath = os.path.join(args.output_dir, filepath)
        data: Dict[int, Dict[str, List[BoardConfig]]] = {}
        for n in random_sizes:
            data[n] = get_random_boards(n, num_boards=args.num_boards_per_config)
            # data[n] = get_random_boards(n)

            if DEBUG:
                write_boards_to_json(data, filepath)
                return

        write_boards_to_json(data, filepath)


    filepath = f"experiment_{board_size[-1]}.json"
    filepath = os.path.join(args.output_dir, filepath)
    data = {
        board_size[-1]: get_random_boards(board_size[-1])
    }
    write_boards_to_json(data, filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--output_dir", type=str, default="./data/experiments",
                        help="Output directory")
    parser.add_argument("--num_boards_per_config", type=int, default=10,
                        help="number of boards per configuration")

    parser.add_argument("-d", "--debug", action="store_true",
                        help="flag to run in debug mode")

    args = parser.parse_args()
    main(args)
