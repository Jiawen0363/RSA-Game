
import sys
import os
import re
import json
import random
from nltk import pr
from tqdm import tqdm
from collections import defaultdict
from difflib import SequenceMatcher
from typing import List, Dict
HOME_DIR = os.environ.get("HOME")
random.seed(42)


sys.path.append(f"{HOME_DIR}/codes/ForesightOptim")
from environment.word_taboo import *

def is_valid_conv(conversation: List[Dict[str, str]]):
    if len(conversation) % 2 != 0:
        if random.random() < 0.5:
            return False

    if len(conversation) < 4:
        return False

    if len(conversation) > 10:
        return False

    for turn in conversation:
        content = turn["content"]
        if len(content.split()) > 100:
            return False

    return True


def extract_data():
    predict_signal = [
        "the term you're referring to ",
        "the term you are referring to ",
        "the word you're referring to ",
        "the word you are referring to ",
        "guess the word is ",
        "the term you might be referring to is ",
        "the word could be ",
        "the word might be ",
        "are you referring to the term",
        "based on your clues, "
    ]
    winner_times = defaultdict(int)
    dialogue_lens = defaultdict(int)
    data = json.load(
        open(f"{HOME_DIR}/datasets/wordgame/gpt4_game_top30k_results.json", "r"))
    new_data = []
    for idx, instance in tqdm(enumerate(data), total=len(data)):
        target = instance["target_word"]
        history = instance["history"]
        max_turns = instance["max_turns"]
        winner = instance["winner"]

        if not is_valid_conv(history):
            continue

        if len(history) > max_turns * 2:
            continue

        if winner not in ["attacker", "defender"]:
            continue

        is_valid = True
        for idx, turn in enumerate(history):
            if turn["role"] == "attacker":
                # break the rule, discard the conversation
                if has_target_word(turn["content"], target):
                    is_valid = False
                    break
            else:
                for signal in predict_signal:
                    sentences = re.split(r'(?<=[.!?])\s+', turn["content"])
                    for sent in sentences:
                        if signal in sent.lower():
                            signal_idx = sent.lower().find(signal.lower())
                            if signal_idx != -1:
                                prefix = sent[:signal_idx]
                                after_signal = sent[signal_idx + len(signal):]
                                words = [w for w in re.split(
                                    r'\s+', after_signal) if w]
                                if words:
                                    # Remove surrounding punctuation
                                    last_word = re.sub(r'[^\w]', '', words[-1])
                                    word_string = random.choice(
                                        [f"\"{last_word}\"", f"'{last_word}'", f"`{last_word}`", last_word])
                                    history[idx]["content"] = prefix + \
                                        f"I know the word! It is {word_string}."
                                    turn["content"] = history[idx]["content"]
                                    break

                if (not is_prediction(turn["content"], target)) and has_target_word(turn["content"], target) and idx != len(history) - 1:
                    history = history[:idx]
                    target_string = random.choice(
                        [f"\"{target}\"", f"'{target}'", f"`{target}`", target])
                    history.append({
                        "role": "defender",
                        "content": f"I know the word! It is {target_string}.",
                    })
                    winner = "defender"
                    break
                elif is_prediction(turn["content"], target) and (not is_correct_prediction(turn["content"], target)):
                    match = re.search(
                        r'i know the word! it is ([^\.!\?]+)', turn["content"], re.IGNORECASE)
                    guess = ""
                    if match:
                        guess = re.sub(r'[^a-zA-Z]', '', match.group(1))
                    if any([SequenceMatcher(None, gu, target).ratio() >= 0.8 for gu in get_derivative_words(guess)]):
                        history = history[:idx]
                        target_string = random.choice(
                            [f"\"{target}\"", f"'{target}'", f"`{target}`", target])
                        history.append({
                            "role": "defender",
                            "content": f"I know the word! It is {target_string}.",
                        })
                        winner = "defender"

                    elif idx == len(history) - 1:
                        winner == "attacker"
                    
                    elif idx != len(history) - 1:
                        discard = random.random()
                        if discard < 0.5:
                            history = history[:idx+1]
                            winner == "attacker"
                        else:
                            is_valid = False
                        # else:
                        #     history = history[:idx]
                        #     target_string = random.choice(
                        #         [f"\"{target}\"", f"'{target}'", f"`{target}`", target])
                        #     history.append({
                        #         "role": "defender",
                        #         "content": f"I know the word! It is {target_string}.",
                        #     })
                        #     winner = "defender"
                    break
                elif is_prediction(turn["content"], target) and is_correct_prediction(turn["content"], target):
                    history = history[:idx+1]
                    winner = "defender"
                    break

        if not is_valid:
            continue

        if not is_valid_conv(history):
            continue

        if winner == "defender":
            if not is_prediction(history[-1]["content"], target):
                new_history = history[:-1]
                new_history.append({
                    "role": "defender",
                    "content": f"I know the word! It is {target}.",
                })

        else:
            if is_correct_prediction(history[-1]["content"], target):
                winner = "defender"

            elif not is_prediction(history[-1]["content"], target) and not has_target_word(history[-1]["content"], target):
                # print(history[-1]["content"])
                max_turns = len(history)
                if random.random() < 0.7:
                    continue

        new_data.append({
            "target": target,
            "history": history,
            "max_turns": max(max_turns, len(history)),
            "winner": "attacker",
        })

        dialogue_lens[len(history)] += 1
        winner_times[winner] += 1

    print(len(new_data))
    print(winner_times)
    print(dialogue_lens)
    with open(f"{HOME_DIR}/datasets/wordtaboo/gpt4_game_top30k_results_valid.json", "w") as f:
        json.dump(new_data, f, indent=4)


def prepare_training_data():
    data = json.load(
        open(f"{HOME_DIR}/datasets/wordtaboo/gpt4_game_top30k_results_valid.json", "r"))
    training_data = []
    for item in tqdm(data, total=len(data)):
        target = item["target"]
        history = item["history"]
        max_turns = item["max_turns"]
        winner = item["winner"]

        for idx, turn in enumerate(history):
            target = turn["content"]
            training_data.append({
                "query": randomly_convert_game_history_to_query(history[:idx], target, max_turns),
                "target": target,
                "winner": winner,
            })
    with open(f"{HOME_DIR}/datasets/wordtaboo/train_imitation_gpt4.json", "w") as f:
        json.dump(training_data, f, indent=4)


if __name__ == '__main__':
    extract_data()
    prepare_training_data()

    data = json.load(
        open(f"{HOME_DIR}/datasets/wordtaboo/gpt4_game_top30k_results_valid.json", "r"))
    print(len(data))
    print(data[0])

    data = json.load(
        open(f"{HOME_DIR}/datasets/wordtaboo/train_imitation_gpt4.json", "r"))
    print(len(data))
    print(data[0])
