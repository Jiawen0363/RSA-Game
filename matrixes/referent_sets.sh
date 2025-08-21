#!/bin/bash

cd $HOME/codes/ForesightOptim/rsa_game
python matrixes/normal_referent_sets.py \
    --feature_pairs_file "$HOME/datasets/rsagame/feature_pairs_bank_01.txt" \
    --selected_matrixes_dir "$HOME/datasets/rsagame/01_matrixes/selected_matrixes_with_dialogs" \
    --output_dir "$HOME/datasets/rsagame/02_referent_sets" \
    --repeat 5500