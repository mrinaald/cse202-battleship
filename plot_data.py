# -*- coding: utf-8 -*-
"""
Module to plot results
"""
import json
import os
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm


plt.rcParams.update({'font.size': 16})


def plot_for_board_size(brute_force_data_files: List[str], optimal_data_files: List[str], random_data_files: List[str]):
    """Only use p0.20-s1x2 config"""
    CONFIG_NAMES = ["p0.20-s1x2"]

    def extract_results(data_files: Dict) -> Dict[int, List[int]]:
        results = {}
        for result_file in data_files:
            with open(result_file, "r") as f:
                data: Dict = json.load(f)

            for n, configs in data.items():
                for config, result in configs.items():
                    if config not in CONFIG_NAMES:
                        continue
                    results[int(n)] = result["moves"]
        return results

    # {N -> [Moves]}
    bruteforce = extract_results(brute_force_data_files)
    optimal = extract_results(optimal_data_files)
    randomized = extract_results(random_data_files)

    datasets = [bruteforce, optimal, randomized]
    names = ["BruteForce", "Our Algo", "Randomized"]

    for name, dataset in zip(names, datasets):
        n = list(dataset.keys())
        n.sort()
        avg_moves = [np.mean(dataset[i]) for i in n]
        median_moves = [np.median(dataset[i]) for i in n]
        plt.plot(n, avg_moves, label=name)

    # plt.xscale("log", base=2)
    # plt.yscale("log", base=2)
    plt.xlabel("Board Size $N$")
    plt.ylabel("Num moves to finish the game")
    plt.subplots_adjust(left=0.06, bottom=0.08, right=0.97, top=0.95)
    plt.title("Board Size $N$ vs Num moves")
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_for_area(brute_force_data_files: List[str], optimal_data_files: List[str], random_data_files: List[str]):
    """Only use 1x2 ship size config"""
    SHIP_SIZE = "-s1x2"

    def extract_results(data_files: Dict) -> Dict[int, Dict[int, List[int]]]:
        results = {}
        for result_file in data_files:
            with open(result_file, "r") as f:
                data: Dict = json.load(f)

            for n, configs in data.items():
                for config, result in configs.items():
                    if SHIP_SIZE not in config:
                        continue
                    perc = float(config.split("-")[0][1:])
                    area = round(perc*100)
                    if area not in results:
                        results[area] = {}
                    results[area][int(n)] = result["moves"]
        return results

    # {Area -> {N -> [Moves]}}
    bruteforce = extract_results(brute_force_data_files)
    optimal = extract_results(optimal_data_files)
    randomized = extract_results(random_data_files)

    datasets = [bruteforce, optimal, randomized]
    names = ["BruteForce", "Our Algo", "Randomized"]

    # fig, axes = plt.subplots(3, 1)
    for algo_id, (name, dataset) in enumerate(zip(names, datasets)):
        areas = list(dataset.keys())
        areas.sort()

        for area in areas:
            n = list(dataset[area].keys())
            n.sort()

            avg_moves = [np.mean(dataset[area][i]) for i in n]
            median_moves = [np.median(dataset[area][i]) for i in n]
            plt.plot(n, avg_moves, label=f"{name}; $A_S$ = {area}%")

        # plt.xscale("log", base=2)
        # plt.yscale("log", base=2)
        plt.xlabel("Board Size $N$")
        plt.ylabel("Num moves to finish the game")
        plt.subplots_adjust(left=0.07, bottom=0.08, right=0.97, top=0.95)
        plt.title("Area covered by Ships $A_S$ vs Num moves")
        plt.legend()
        plt.grid(True)
        plt.show()


def plot_for_ship_size(brute_force_data_files: List[str], optimal_data_files: List[str], random_data_files: List[str]):
    """Only use 1x2 ship size config"""
    AREA_PERCENTAGE = "p0.20-"
    SHIP_SIZES = [(1, 2), (2, 3), (3, 5)]

    def extract_results(data_files: Dict) -> Dict[int, Dict[int, List[int]]]:
        results = {}
        for result_file in data_files:
            with open(result_file, "r") as f:
                data: Dict = json.load(f)

            for n, configs in data.items():
                for config, result in configs.items():
                    if AREA_PERCENTAGE not in config:
                        continue
                    min_ship_size = config.split("-")[1][1:]
                    min_ship_size = tuple([int(s) for s in min_ship_size.split("x")])
                    if min_ship_size not in SHIP_SIZES:
                        continue
                    if min_ship_size not in results:
                        results[min_ship_size] = {}
                    results[min_ship_size][int(n)] = result["moves"]
        return results

    # {(l_a, b_a) -> {N -> [Moves]}}
    bruteforce = extract_results(brute_force_data_files)
    optimal = extract_results(optimal_data_files)
    randomized = extract_results(random_data_files)

    datasets = [bruteforce, optimal, randomized]
    names = ["BruteForce", "Our Algo", "Randomized"]

    # fig, axes = plt.subplots(3, 1)
    for algo_id, (name, dataset) in enumerate(zip(names, datasets)):
        ship_sizes = list(dataset.keys())
        ship_sizes.sort()

        for size in ship_sizes:
            n = list(dataset[size].keys())
            n.sort()

            avg_moves = [np.mean(dataset[size][i]) for i in n]
            median_moves = [np.median(dataset[size][i]) for i in n]
            plt.plot(n, avg_moves, label=f"{name}; $S_a$ = {size}")

        # plt.xscale("log", base=2)
        # plt.yscale("log", base=2)
        plt.xlabel("Board Size $N$")
        plt.ylabel("Num moves to finish the game")
        plt.subplots_adjust(left=0.07, bottom=0.08, right=0.97, top=0.95)
        plt.title("Min Ship Size $S_a = (l_a, b_a)$ vs Num moves")
        plt.legend()
        plt.grid(True)
        plt.show()


def main():
    data_dirs = ["./data/outputs", "./data/outputs-fixed"]
    brute_force_data_files = [
        f.path for data_dir in data_dirs
        for f in os.scandir(data_dir) if "bruteforce" in f.name
    ]
    optimal_data_files = [
        f.path for data_dir in data_dirs
        for f in os.scandir(data_dir) if "optimal" in f.name
    ]
    random_data_files = [
        f.path for data_dir in data_dirs
        for f in os.scandir(data_dir) if "random" in f.name
    ]

    # plot_for_board_size(brute_force_data_files, optimal_data_files, random_data_files)
    plot_for_area(brute_force_data_files, optimal_data_files, random_data_files)
    plot_for_ship_size(brute_force_data_files, optimal_data_files, random_data_files)


if __name__ == "__main__":
    main()
