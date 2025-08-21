#!/usr/bin/env python3
"""
# Script for randomly selecting matrices and combining them into a new JSON file
# A total of 900 matrices will be selected: 300 with rounds=1, 300 with rounds=2, and 300 with rounds=3
"""

import json
import os
import random
from pathlib import Path
from typing import List, Dict, Any
import argparse
HOME_DIR = os.getenv("HOME")


def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Load JSON file"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(data: List[Dict[str, Any]], file_path: str):
    """Save JSON file"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved {len(data)} matrixes to {file_path}")


def get_all_matrix_files(base_dir: str) -> Dict[int, List[str]]:
    """Get all matrix files, grouped by rounds"""
    rounds_files = {1: [], 2: [], 3: []}

    base_path = Path(base_dir)
    print(f"Searching in directory: {base_path.absolute()}")

    # iterate over all matrix directories
    for matrix_dir in base_path.iterdir():
        if matrix_dir.is_dir() and matrix_dir.name.startswith("matrixes_"):
            print(f"Found matrix directory: {matrix_dir.name}")
            # iterate over all JSON files in the directory
            for json_file in matrix_dir.glob("*.json"):
                if json_file.name.endswith(".json"):
                    print(f"  Found file: {json_file.name}")
                    # extract rounds information from the file name
                    if "1rounds" in json_file.name:
                        rounds_files[1].append(str(json_file))
                        print(f"    -> Added to rounds=1")
                    elif "2rounds" in json_file.name:
                        rounds_files[2].append(str(json_file))
                        print(f"    -> Added to rounds=2")
                    elif "3rounds" in json_file.name:
                        rounds_files[3].append(str(json_file))
                        print(f"    -> Added to rounds=3")

    return rounds_files


def select_random_matrices(
    rounds_files: Dict[int, List[str]], target_count: int = 300
) -> Dict[int, List[Dict[str, Any]]]:
    """Randomly select matrices"""
    selected_matrixes = {1: [], 2: [], 3: []}

    for rounds, file_paths in rounds_files.items():
        print(f"\nProcessing rounds={rounds}...")
        print(f"Found {len(file_paths)} files for rounds={rounds}")

        all_matrixes = []

        # load all matrices from all files
        for file_path in file_paths:
            matrixes = load_json_file(file_path)
            all_matrixes.extend(matrixes)
            print(
                f"  Loaded {len(matrixes)} matrixes from {os.path.basename(file_path)}"
            )

        print(f"Total matrixes available for rounds={rounds}: {len(all_matrixes)}")

        # randomly select the specified number of matrices
        if len(all_matrixes) >= target_count:
            selected = random.sample(all_matrixes, target_count)
            selected_matrixes[rounds] = selected
            print(f"Selected {len(selected)} matrixes for rounds={rounds}")
        else:
            print(
                f"Warning: Only {len(all_matrixes)} matrixes available for rounds={rounds}, "
                f"but {target_count} requested. Using all available."
            )
            selected_matrixes[rounds] = all_matrixes

    return selected_matrixes


def main():
    parser = argparse.ArgumentParser(
        description="Randomly select matrices and combine them into a new JSON file"
    )
    parser.add_argument(
        "--base_dir",
        type=str,
        default=f"{HOME_DIR}/datasets/rsagame/01_matrixes/matrixes_with_dialogs",
        help="Root directory of matrix folders",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="Output directory, default is test_selected_dialogs under base_dir",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--target_count",
        type=int,
        default=300,
        help="Number of matrices to select for each round",
    )
    args = parser.parse_args()

    random.seed(args.seed)

    base_dir = Path(args.base_dir)
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else f"{HOME_DIR}/datasets/rsagame/01_matrixes/test_selected_dialogs"
    )

    print(f"Base directory: {base_dir}")
    print(f"Output directory: {output_dir}")

    # ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print("Start selecting matrices...")

    # get all matrix files
    rounds_files = get_all_matrix_files(str(base_dir))

    # print found file information
    for rounds, files in rounds_files.items():
        print(f"Rounds {rounds}: {len(files)} files")
        for file_path in files:
            print(f"  - {os.path.basename(file_path)}")

    # randomly select matrices
    selected_matrixes = select_random_matrices(
        rounds_files, target_count=args.target_count
    )

    # save to three new JSON files
    for rounds, matrixes in selected_matrixes.items():
        if matrixes:
            output_file = output_dir / f"selected_matrixes_{rounds}rounds.json"
            save_json_file(matrixes, str(output_file))
        else:
            print(f"No matrixes selected for rounds={rounds}")

    # print summary
    print("\n" + "=" * 50)
    print("Selection completed!")
    for rounds, matrixes in selected_matrixes.items():
        print(f"Rounds {rounds}: {len(matrixes)} matrixes")
    print("=" * 50)


if __name__ == "__main__":
    main()
