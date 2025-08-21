# dialogue_pipeline.py
import random
import json
import os
import argparse
from mapping import MatrixMapping
from tqdm import tqdm

parser = argparse.ArgumentParser(
    description="randomly select a matrix and generate dialogue chain"
)
parser.add_argument(
    "--feature_pairs_file", required=True, help="feature pairs file path"
)
parser.add_argument(
    "--selected_matrixes_dir", required=True, help="selected matrixes directory"
)
parser.add_argument("--output_dir", required=True, help="output directory")
parser.add_argument("--repeat", type=int, default=10, help="repeat times")


args = parser.parse_args()

# reload feature_pairs
with open(args.feature_pairs_file, "r") as file:
    feature_pairs = [line.strip() for line in file.readlines()]

# set global feature_pairs for mapping.py
import mapping

mapping.feature_pairs = feature_pairs

# read matrix files from the directory
import glob

matrix_files = glob.glob(os.path.join(args.selected_matrixes_dir, "*.json"))
if not matrix_files:
    raise ValueError(
        f"no JSON files found in the directory {args.selected_matrixes_dir}"
    )

print(f"found {len(matrix_files)} matrix files")


def generate_dialogue_chain(matrix_files):
    # randomly select a matrix file
    selected_file = random.choice(matrix_files)

    # read the matrix file
    with open(selected_file, "r") as file:
        matrixes_data = json.load(file)

    # confirm the data format: JSON array, each element is a matrix object
    if not isinstance(matrixes_data, list):
        raise ValueError(f"expected JSON array format, but got {type(matrixes_data)}")

    # randomly select a matrix object
    selected_matrix_obj = random.choice(matrixes_data)

    # extract the matrix data
    matrix_data = selected_matrix_obj["matrix"]

    # call the function in mapping.py to generate dialogue chain
    dialogue_data = MatrixMapping(matrix_data).mapping_to_dialogue()
    return dialogue_data


def save_dialogue_chains(all_dialogue_data, output_path):
    # save all dialogue chains to a file
    with open(output_path, "w") as file:
        json.dump(all_dialogue_data, file, indent=2, ensure_ascii=False)


def main():
    # create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # collect all dialogue chains
    all_dialogue_chains = []

    # repeat generate dialogue chains
    for i in range(args.repeat):
        print(f"\n=== generate {i+1}th dialogue chain ===")

        # generate dialogue chain
        dialogue_data = generate_dialogue_chain(matrix_files)

        # add to the list
        all_dialogue_chains.append(dialogue_data)

        print(f"generated {i+1}th dialogue chain")

    # save all dialogue chains to a file
    output_path = os.path.join(args.output_dir, "dialogue_chains.json")
    save_dialogue_chains(all_dialogue_chains, output_path)

    print(
        f"\ncompleted! generated {args.repeat} dialogue chains, saved to dialogue_chains.json"
    )


def generate_dataset():
    os.makedirs(args.output_dir, exist_ok=True)
    all_dialogue_chains = []

    for file in tqdm(matrix_files, total=len(matrix_files), desc="Generating dataset"):
        with open(file, "r") as file:
            matrixes_data = json.load(file)
        if "1round" in str(file):
            count = 1
            # matrixes_data = matrixes_data[:400] + matrixes_data[600:1200] + matrixes_data[1400:1800]
            # matrixes_data = matrixes_data[400:500] + matrixes_data[1200:1300] + matrixes_data[1700:1800]
            # matrixes_data = matrixes_data[500:600] + matrixes_data[1300:1400] + matrixes_data[1800:1900]
            
            matrixes_data = matrixes_data[1800:1900]
            
        elif "2round" in str(file):
            count = 5
            # matrixes_data = matrixes_data[:800] + matrixes_data[1400:2200] + matrixes_data[3000:3400]
            # matrixes_data = matrixes_data[600:1000] + matrixes_data[2200:2600] + matrixes_data[3200:3600]
            # matrixes_data = matrixes_data[1000:1400] + matrixes_data[2600:3000] + matrixes_data[3400:3800]
            
            matrixes_data = matrixes_data[3600:3800]

        else:
            assert "3round" in str(file), f"unknown round number in {file}"
            count = 128
            # matrixes_data = matrixes_data[:20]
            # matrixes_data = matrixes_data[6:26]
            matrixes_data = random.sample(matrixes_data, 20)
        
        for matrix in matrixes_data:
            data = matrix["matrix"]
            for _ in range(count):
                dialogue_data = MatrixMapping(data).mapping_to_dialogue()
                all_dialogue_chains.append(dialogue_data)

    # output_path = os.path.join(args.output_dir, "imitation_dialog_chains.json")
    # output_path = os.path.join(args.output_dir, "reasoning_dialog_chains.json")
    output_path = os.path.join(args.output_dir, "eval_dialog_chains.json")
    
    save_dialogue_chains(all_dialogue_chains, output_path)

if __name__ == "__main__":
    # main()
    generate_dataset()
