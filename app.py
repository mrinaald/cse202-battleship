# -*- coding: utf-8 -*-
"""
The main app module
"""
import argparse
import json
import os
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from tqdm import tqdm

from agent import BaseAgent, BruteForceAgent, OptimalAgent, RandomAgent
from board import BattleshipBoard, BattleshipAgentBoard
from data_types import BoardConfig, ExperimentConfig


def run_experiments(config_file: str, agent: str, output_dir: str, seed: int, runs: int):
    """
    Method to run multiple experiments

    NOTE: Param {runs} is currently not used
    """
    with open(config_file, "r") as f:
        experiment_config: Dict = json.load(f)

    basename = os.path.basename(config_file)
    result_file = os.path.join(output_dir, f"{agent}_{basename.split('_')[-1]}")

    # Planning to save as json
    # results = {n: {config: {moves: [], error: [(index, message)]}}}
    results = {}


    for n, configs in tqdm(experiment_config.items(), total=len(experiment_config), desc="N"):

    # rng = np.random.default_rng(seed=seed)
    # all_n = list(experiment_config.keys())
    # all_n.sort()
    # random_n = [all_n[0]] + rng.choice(all_n[1:], size=9, replace=False).tolist()
    # random_n.sort()
    # for n in tqdm(random_n, desc="N"):
    #     configs = experiment_config[n]


        results[n] = {}
        for config, boards in tqdm(configs.items(), total=len(configs), desc="Configs", leave=False):
            perc = float(config.split("-")[0][1:])
            min_ship_size = config.split("-")[1][1:]
            min_ship_size = tuple([int(s) for s in min_ship_size.split("x")])

            # print(f"n={n} | p={perc} | s={min_ship_size} | num_boards={len(boards)}")
            game_moves = []
            errors = []

            for i, board_config_dict in tqdm(enumerate(boards), total=len(boards), desc="Board", leave=False):
                board_config = BoardConfig.from_dict(board_config_dict)

                # We need at least N (board size) vs Moves plot for all 3 agents
                #
                # For every N, we have:
                # 1. (a) Total area of ship approx. 20% of total area of board
                #    (b) Total area of ship approx. 40% of total area of board
                # 2. (a) Minimum size ship = 1 x 2
                #    (b) Minimum size ship = 2 x 3
                #    (c) Minimum size ship = Random([2,3,4,5]) x Random([2,3,4,5])
                # In other words, a total of 6 combinations for each N.
                # For each combination, we have 10 different boards, so we can take avg., std., median, etc.

                moves, err = run_game(board_config, agent, seed)
                if moves > 0 and len(err) == 0:
                    game_moves.append(moves)
                else:
                    errors.append((i, err))

            results[n][config] = {
                "moves": game_moves,
                "errors": errors,
            }

    os.makedirs(output_dir, exist_ok=True)
    with open(result_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved in: {result_file}")


def run_game(board_config: BoardConfig, agent: str, seed: int = 0) -> Tuple[int, str]:
    game_board = BattleshipBoard(board_config)
    agent_board = BattleshipAgentBoard(board_config, game_board.get_proxy_API_for_attack())

    if agent == "bruteforce":
        agent: BaseAgent = BruteForceAgent(agent_board=agent_board)
    elif agent == "optimal":
        agent: BaseAgent = OptimalAgent(agent_board=agent_board)
    elif agent == "random":
        agent: BaseAgent = RandomAgent(agent_board=agent_board, seed=seed)
    else:
        raise NotImplementedError(f"Unknown agent [{agent}]")

    moves, err = agent.start_game()
    return moves, err


def main(args: argparse.Namespace):
    if args.experiment_file and os.path.exists(args.experiment_file):
        # Experiment mode
        # TODO: Use run_experiments() method
        run_experiments(args.experiment_file, args.agent, output_dir=args.output_dir, seed=args.seed, runs=args.runs)
        return

    if args.config_file and os.path.exists(args.config_file):
        # Use the input config to generate a random board
        return

    if args.board_file and os.path.exists(args.board_file):
        # Use the input json file to load a board
        board_config = BoardConfig.from_json(args.board_file)
        moves, error_msg = run_game(board_config, args.agent, args.seed)
        if error_msg:
            print(f"Agent Error: {error_msg}")
            return
        print(f"Num moves taken by agent: {moves}")
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--board_file", type=str, default="",
                        help="Input board filepath")
    parser.add_argument("-a", "--agent", default="bruteforce",
                        choices=["bruteforce", "optimal", "random"],
                        help="The agent to use")

    # Below parameters are not implemented yet
    parser.add_argument("-c", "--config_file", type=str, default="",
                        help="Generate a random board from an input CONFIG .json file")
    parser.add_argument("-s", "--seed", type=int, default=0,
                        help="The random seed value. Used when random boards are used.")

    parser.add_argument("-e", "--experiment_file", type=str, default="",
                        help="Run experiments using an input CONFIG .json file."
                        "If provided, all other parameters are ignored.")
    parser.add_argument("-o", "--output_dir", type=str, default="./data/outputs",
    # parser.add_argument("-o", "--output_dir", type=str, default="./data/outputs-large-ships",
                        help="Output directory")
    parser.add_argument("-r", "--runs", type=int, default=10,
                        help="Number of runs for each experiment")

    args = parser.parse_args()
    main(args)
