#!/bin/bash

# matrix selection and integration script template
# usage: uncomment the corresponding command as needed

# ============================================================================
# basic command (using default parameters)
# ============================================================================
# cd $HOME/codes/ForesightOptim/rsa_game
# python dialogs/golden_dialogs/combine_and_select_matrixes.py

# ============================================================================
# custom parameters example (uncomment to use)
# ============================================================================

# 1. modify the number of matrices selected for each round
cd $HOME/codes/ForesightOptim/rsa_game
python dialogs/golden_dialogs/combine_and_select_matrixes.py --target_count 26

# 2. custom output directory
# cd $HOME/codes/ForesightOptim/rsa_game
# python dialogs/golden_dialogs/combine_and_select_matrixes.py --output_dir my_custom_output

# 3. modify random seed
# cd $HOME/codes/ForesightOptim/rsa_game
# python dialogs/golden_dialogs/combine_and_select_matrixes.py --seed 123

# 4. combine multiple parameters
# cd $HOME/codes/ForesightOptim/rsa_game
# python dialogs/golden_dialogs/combine_and_select_matrixes.py \
#     --target_count 200 \
#     --output_dir custom_output \
#     --seed 42

# 5. use different input directory (if needed)
# cd $HOME/codes/ForesightOptim/rsa_game
# python dialogs/golden_dialogs/combine_and_select_matrixes.py \
#     --base_dir different_input_dir \
#     --output_dir different_output_dir

# ============================================================================
# parameter explanation
# ============================================================================
# --base_dir: root directory of matrix folders (default: $HOME/datasets/rsagame/01_matrixes/matrixes_with_dialogs)
# --output_dir: output directory (default: $HOME/datasets/rsagame/01_matrixes/test_selected_dialogs)
# --target_count: number of matrices selected for each round (default: 300)
# --seed: random seed (default: 42)

# ============================================================================
# view help information
# ============================================================================
# cd $HOME/codes/ForesightOptim/rsa_game
# python dialogs/golden_dialogs/combine_and_select_matrixes.py --help 