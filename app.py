# -*- coding: utf-8 -*-
"""
The main app module
"""
import argparse
import os

from agent import BruteForceAgent, OptimalAgent, RandomAgent
from board import BattleshipBoard, BattleshipAgentBoard
from data_types import BoardConfig, ExperimentConfig


def run_experiments(config: ExperimentConfig, output_dir: str):
    """Method to run multiple experiments"""
    pass


def run_game(board_config: BoardConfig, agent: str, seed: int = 0):
    game_board = BattleshipBoard(board_config)
    agent_board = BattleshipAgentBoard(board_config, game_board.get_proxy_API_for_attack())

    if agent == "bruteforce":
        agent = BruteForceAgent(agent_board=agent_board)
    elif agent == "optimal":
        agent = OptimalAgent(agent_board=agent_board)
    elif agent == "random":
        agent = RandomAgent(agent_board=agent_board, seed=seed)
    else:
        raise NotImplementedError(f"Unknown agent [{agent}]")

    moves, err = agent.start_game()
    if err:
        print(f"Agent Error: {err}")
        return
    print(f"Num moves taken by agent: {moves}")


def main(args: argparse.Namespace):
    if args.experiment_file and os.path.exists(args.experiment_file):
        # Experiment mode
        # TODO: Use run_experiments() method
        return

    if args.config_file and os.path.exists(args.config_file):
        # Use the input config to generate a random board
        return

    if args.board_file and os.path.exists(args.board_file):
        # Use the input json file to load a board
        board_config = BoardConfig.from_json(args.board_file)
        run_game(board_config, args.agent, args.seed)
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

    args = parser.parse_args()
    main(args)
