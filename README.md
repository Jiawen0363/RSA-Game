# Generate the RSA Game Dataset

## SFT Dataset

### Pipeline

* Generate feature pair banks [feature_pairs_bank_01.txt]($HOME/datasets/rsagame/feature_pairs_bank_01.txt) for SFT and [feature_pairs_bank_02.txt]($HOME/datasets/rsagame/feature_pairs_bank_02.txt) for RL.
* Generate rational speech act matrixes: [01_matrixes]($HOME/datasets/rsagame/01_matrixes).
    * matrixes/matrix_generator.py: matrixes_unsorted folder, the shape of matrix can be changed accordingly.
    * matrixes/mapping.py: matrixes_with_dialogs folder
    * matrixes/combine_and_select_matrixes.py: selected_matrixes_with_dialogs/test_selected_dialogs folder
        ```bash
        python dialogs/golden_dialogs/combine_and_select_matrixes.py --target_count 4000 --output_dir /home/jiashuo/datasets/rsagame/01_matrixes/selected_matrixes_with_dialogs
        # there are 4000, 4000, and 26 maxtrixes for 1/2/3-round conversations.
        ```
        The dataset is divided in to three parts: sft (400 * 1, 800 * 5, fister 20 * 64), rl (100 * 2, 400 * 4, latter 20 * 64), and eval (100 * 2, 400 * 4, 20 * 64). Save in the paths: [selected_matrixes_xrounds.json]($HOME/datasets/rsagame/01_matrixes/selected_matrixes_with_dialogs).
        
* Generate a backbone for each conversation, given the feature pairs and the matrixes.
    * Generate referent sets for the conversations with rational speaker and normal listner
        ```bash
        bash matrixes/referent_sets.sh
        ```
    * Generate dialogue chain for conversations with rational speaker and rational listner (about 5500 conversations)
        ```
        bash matrixes/generate_golden_chain.sh
        ```
        The data is saved in [xx_dialog_chains.json]($HOME/datasets/rsagame/02_dialogs/golden_dialog_chain).
* Generate the conversations accoding to the backbones using GPT-4o.
    ```bash
    bash dialogs/golden_dialogs/polish_dialogs.sh
    ```
    The generated dataset is saved in [rsa_dialogs_gpt4.1.json]($HOME/datasets/rsagame/02_dialogs/golden_dialog/rsa_dialogs_gpt4.1.json). Then, we need to check whether the dataset is generated as expected:
    1. the response contians the correct features;
    2. the last reponse is in the format: I know the target object. It is ...
    ```bash 
    python dialogs/golden_dialogs/correct_dialogs.py
    ```
    Save the dataset in [rsa_dialogs_gpt4.1.json]($HOME/datasets/rsagame), and the intermediate data is saved as [xxx_iterx.json](/home/jiashuo/datasets/rsagame/02_dialogs/golden_dialog)
* Generate training dataset.
    ```bash

    ```
    Save the training set in [train_imitation_gpt4.1.json]($HOME/datasets/rsagame)
## Reinforcement Learning Dataset
