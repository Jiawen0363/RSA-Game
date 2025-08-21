import random
import json
import sys
import os
import glob
import argparse
import sys
import os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "dialogs", "golden_dialogs")
)
from generate_dialogs import GoldenDialogsGenerator


# global variable
feature_pairs = []


def load_feature_pairs(file_path):
    """load feature pairs file"""
    global feature_pairs
    with open(file_path, "r") as file:
        feature_pairs = [line.strip() for line in file.readlines()]


# default load feature pairs file
default_feature_pairs_file = f"{os.environ.get('HOME')}/datasets/rsagame/feature_pairs_bank_01.txt"
load_feature_pairs(default_feature_pairs_file)


class MatrixMapping:
    def __init__(self, matrix):
        self.matrix = matrix

    def mapping_to_referent_set(self):
        """
        map feature pairs to matrix, generate referent set
        each column corresponds to a feature pair, the 0/1 in the matrix decides which feature to use
        """
        # randomly select feature pairs with the same number of columns as the matrix
        selected_pairs = random.sample(feature_pairs, len(self.matrix[0]))
        referent_set = []

        for row in self.matrix:  # iterate over each row of the matrix
            referent = []
            for col_idx, value in enumerate(row):  # iterate over each column
                feature_pair = selected_pairs[
                    col_idx
                ]  # get the corresponding feature pair
                features = feature_pair.split(" / ")  # split feature pair

                if value == 0:
                    referent.append(features[0])  # use the first feature
                elif value == 1:
                    referent.append(features[1])  # use the second feature
                else:
                    print(f"Warning: Unexpected value {value} in matrix")
                    referent.append(features[0])  # use the first feature by default

            # directly add the feature list, without converting to a string
            referent_set.append(referent)

        return referent_set

    def mapping_to_dialogue(self):
        referent_set = self.mapping_to_referent_set()
        dialogue_data = GoldenDialogsGenerator(referent_set, 0).generate_dialogue()
        return dialogue_data

    def save_dialogue(self, dialogue_data, output_dir=None):
        # create a complete data structure with matrix and dialogue information
        complete_data = {
            "matrix": self.matrix,
            "referent_set": dialogue_data["referent_set"],
            "target_referent": dialogue_data["target_referent"],
            "dialogue": dialogue_data["dialogue"],
            "rounds": dialogue_data["rounds"],
        }

        assert output_dir is not None, "output_dir is required"

        # get the shape of the matrix
        rows = len(self.matrix)
        cols = len(self.matrix[0]) if self.matrix else 0
        matrix_shape = f"{rows}x{cols}"

        # choose filename by rounds
        rounds = dialogue_data["rounds"]
        filename = f"{output_dir}/{matrix_shape}_dialogue_{rounds}rounds.json"

        with open(filename, "w") as file:
            json.dump(complete_data, file, indent=2, ensure_ascii=False)

        print(f"dialogue saved to {filename}")

    @staticmethod
    def process_all_matrices(json_file_path, output_dir=None):
        """
        process all matrices in the JSON file, generate dialogue for each matrix and save

        parameters:
        - json_file_path: str, JSON file path
        - output_dir: str, output directory path
        """
        assert output_dir is not None, "output_dir is required"

        # 读取所有矩阵
        with open(json_file_path, "r") as file:
            matrixes_data = json.load(file)

        print(f"processing {len(matrixes_data)} matrices...")

        # collect data by rounds
        dialogues_by_rounds = {1: [], 2: [], 3: [], 4: [], "other": []}

        for matrix_name, matrix in matrixes_data.items():
            print(f"\n=== processing matrix {matrix_name} ===")

            # create MatrixMapping instance
            mapping = MatrixMapping(matrix)

            # generate dialogue
            dialogue_data = mapping.mapping_to_dialogue()

            # create complete data structure
            complete_data = {
                "matrix_name": matrix_name,
                "matrix": matrix,
                "referent_set": dialogue_data["referent_set"],
                "target_referent": dialogue_data["target_referent"],
                "dialogue": dialogue_data["dialogue"],
                "rounds": dialogue_data["rounds"],
            }

            # collect by rounds
            rounds = dialogue_data["rounds"]
            if rounds in [1, 2, 3, 4]:
                dialogues_by_rounds[rounds].append(complete_data)
            else:
                dialogues_by_rounds["other"].append(complete_data)

            print(f"matrix {matrix_name} processed, rounds: {rounds}")

        # get the shape of the matrix (from the first matrix)
        if matrixes_data:
            first_matrix = next(iter(matrixes_data.values()))
            rows = len(first_matrix)
            cols = len(first_matrix[0]) if first_matrix else 0
            matrix_shape = f"{rows}x{cols}"
        else:
            matrix_shape = "0x0"

        # save by rounds
        for rounds, dialogues in dialogues_by_rounds.items():
            if dialogues:  # only save files with data
                if rounds == "other":
                    filename = f"{output_dir}/{matrix_shape}_dialogue_other.json"
                else:
                    filename = (
                        f"{output_dir}/{matrix_shape}_dialogue_{rounds}rounds.json"
                    )

                with open(filename, "w") as file:
                    json.dump(dialogues, file, indent=2, ensure_ascii=False)

                print(f"saved {len(dialogues)} {rounds} rounds dialogues to {filename}")

        print(f"\nall matrices processed!")


# # test code
# if __name__ == "__main__":
#     # create output directory
#     os.makedirs(args.output_dir, exist_ok=True)

#     # get all JSON files in the input directory
#     input_files = glob.glob(os.path.join(args.input_dir, "*.json"))

#     if not input_files:
#         print(f"no JSON files found in the directory {args.input_dir}")
#         exit(1)

#     print(f"found {len(input_files)} JSON files")


#     # process each input file
#     for input_file in input_files:
#         print(f"\n=== processing file: {os.path.basename(input_file)} ===")

#         # create output directory for each file
#         file_name = os.path.splitext(os.path.basename(input_file))[0]
#         file_output_dir = os.path.join(args.output_dir, file_name)
#         os.makedirs(file_output_dir, exist_ok=True)

#         # process all matrices in the current file
#         MatrixMapping.process_all_matrices(input_file, file_output_dir)

#         print(f"file {os.path.basename(input_file)} processed")

#     print(f"\nall files processed! output saved in: {args.output_dir}")
