#!/bin/bash
# to generate 5500 conversations
cd $HOME/codes/ForesightOptim/rsa_game
python matrixes/golden_dialog_pipeline.py \
    --feature_pairs_file "$HOME/datasets/rsagame/feature_pairs_bank_01.txt" \
    --selected_matrixes_dir "$HOME/datasets/rsagame/01_matrixes/selected_matrixes_with_dialogs" \
    --output_dir "$HOME/datasets/rsagame/02_dialogs/golden_dialog_chain" \
    --repeat 200