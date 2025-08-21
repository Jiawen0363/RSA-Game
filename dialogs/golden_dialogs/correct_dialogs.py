import os
import re
import json
import openai
import argparse
import random
import yaml
from tqdm import tqdm
from collections import defaultdict

HOME_DIR = os.getenv("HOME")


parser = argparse.ArgumentParser(description="correct the dialogues")
parser.add_argument(
    "--input_file",
    help="input file path",
    default=f"{HOME_DIR}/datasets/rsagame/02_dialogs/golden_dialog/rsa_dialogs_gpt4.1.json",
)

parser.add_argument(
    "--output_file",
    help="output file path",
    default=f"{HOME_DIR}/datasets/rsagame/rsa_dialogs_gpt4.1.json",
)
args = parser.parse_args()
correct_datapath = (
    f"{HOME_DIR}/datasets/rsagame/02_dialogs/golden_dialog/corrected_dialogs.json"
)


def str2object(formatted_str):
    """Reverse the item_string function to extract the original list of items"""
    # If the string is empty, return empty list
    if not formatted_str:
        return []

    # Remove surrounding brackets/parentheses/braces if present
    if formatted_str.startswith("[") and formatted_str.endswith("]"):
        formatted_str = formatted_str[1:-1].strip()
    elif formatted_str.startswith("(") and formatted_str.endswith(")"):
        formatted_str = formatted_str[1:-1].strip()
    elif formatted_str.startswith("{") and formatted_str.endswith("}"):
        formatted_str = formatted_str[1:-1].strip()

    # Handle different formats
    if ", and " in formatted_str:  # Oxford comma format
        parts = formatted_str.split(", and ")
        if len(parts) > 1:
            return [item.strip() for item in parts[0].split(", ")] + [parts[1].strip()]
    elif " and " in formatted_str and ", " in formatted_str:  # No Oxford comma
        parts = formatted_str.split(", ")
        last_part = parts[-1]
        if " and " in last_part:
            last_items = last_part.split(" and ")
            return [item.strip() for item in parts[:-1]] + [
                item.strip() for item in last_items
            ]
    elif " and " in formatted_str:  # "and" separated format
        return [item.strip() for item in formatted_str.split(" and ")]
    elif ", " in formatted_str:  # Comma separated format
        return [item.strip() for item in formatted_str.split(", ")]

    # If none of the above patterns match, return the string as a single-item list
    return [formatted_str.strip()]


def object2str(item, random_choice=True):
    """Format a list of items in various natural ways"""

    # Randomly choose from different formats
    format_choices = {
        "comma": lambda x: ", ".join(x),
        "bracket": lambda x: "[" + ", ".join(x) + "]",
        "parenthesis": lambda x: "(" + ", ".join(x) + ")",
        "curly": lambda x: "{" + ", ".join(x) + "}",
        "oxford_comma": lambda x: ", ".join(x[:-1]) + ", and " + x[-1],
        "no_oxford_comma": lambda x: ", ".join(x[:-1]) + " and " + x[-1],
        "and_separated": lambda x: " and ".join(x),
    }

    if random_choice:
        format = random.choice(list(format_choices.keys()))
        return format_choices[format](item)
    else:
        return {format: func(item) for format, func in format_choices.items()}


def correct_dialogs(data, save_path):
    if os.path.exists(save_path):
        new_dialog_data = json.load(open(save_path, "r"))
    else:
        new_dialog_data = {}
    problems = defaultdict(list)
    for conv_id, conv in tqdm(data.items()):
        if conv_id in new_dialog_data:
            continue

        target_referent = conv["target_referent"]
        chain = conv["chain"]
        dialogue = conv["dialog"]

        if len(dialogue) != len(chain):
            problems[conv_id] = (
                "The lengths of the dialogue and the chain are not the same."
            )
            print(
                f"========== {conv_id} The lengths of the dialogue and the chain are not the same."
            )
            continue

        new_dialog = []
        for turn_id, turn in enumerate(dialogue):
            content = turn["content"].strip()
            if turn_id % 2 == 0:
                chain_content = chain[turn_id][len("Speaker: ") :].strip()
                if chain_content not in content.lower():
                    print(
                        f"========== {conv_id} The feature {chain_content} is not in the content {content}."
                    )
                    problems[conv_id].append(
                        f"The word {chain_content} is not explicitly mentioned in the speaker's response: {content}"
                    )
            else:
                chain_content = chain[turn_id][len("Listener: ") :].strip()
                matches = re.findall(r"'(.*?)'", chain_content)
                chain_content = [match.split(", ") for match in matches]
                for object in chain_content:
                    object_str = object2str(object)
                    if not any(
                        object_str in content.lower() for object_str in object_str
                    ):
                        print(
                            f"========== {conv_id} The objects {', '.join(object)} are not clearly mentioned in the listener's response: {content}."
                        )
                        problems[conv_id].append(
                            f"The objects {', '.join(object)} are not clearly mentioned in the listener's response: {content}"
                        )

            if turn_id == len(dialogue) - 1:
                if "I know the target object. It is" not in content:
                    pattern = r"([\"'\(])([a-z]+(?:, [a-z]+)+)([\"'\)])"
                    match = re.search(pattern, content)
                    if match:
                        # Extract the target words
                        target_object = match.group(2).split(", ")
                        assert target_object == target_referent.split()

                        # Find the last complete sentence before the target words
                        # Look for the last sentence-ending punctuation before the target
                        # Find all sentences before the match, split by sentence-ending punctuation
                        prefix_text = content[: match.start()]
                        # Split into sentences, keeping punctuation
                        sentences = re.findall(r"[^.!?]*[.!?]", prefix_text)
                        # Remove sentences containing 'know' (case-insensitive)
                        sentences = [
                            s
                            for s in sentences
                            if "know" not in s.lower()
                            and "identify" not in s.lower()
                            and "determine" not in s.lower()
                            and "target object" not in s.lower()
                        ]
                        # Reconstruct the prefix text
                        prefix = "".join(sentences).strip()
                        # Find the last sentence-ending punctuation in the new prefix
                        content = f"{prefix} I know the target object. It is {object2str(target_object)}."
                    else:
                        target_object = target_referent.split()
                        content = f"I know the target object. It is {object2str(target_object)}."

            new_dialog.append(
                {
                    "role": "speaker" if turn_id % 2 == 0 else "listener",
                    "content": content.strip(),
                }
            )
        if conv_id in problems:
            continue
        new_dialog_data[conv_id] = {
            "dialog": new_dialog,
            "chain": chain,
            "referent_set": data[conv_id]["referent_set"],
            "target_referent": data[conv_id]["target_referent"],
        }
    for key, value in problems.items():
        problems[key] = {
            "problems": "\n".join(value),
            "dialog": data[key]["dialog"],
            "chain": data[key]["chain"],
            "referent_set": data[key]["referent_set"],
            "target_referent": data[key]["target_referent"],
        }
    print(f"========== The length of the problematic dialogues is: {len(problems)}.")
    json.dump(new_dialog_data, open(save_path, "w"), indent=2, ensure_ascii=False)
    return problems


def process_problems(problems):
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "api_config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    client = openai.OpenAI(api_key=config["api_key"], base_url=config["base_url"])
    model = "gpt-4.1"
    prompt_dir = f"{HOME_DIR}/codes/ForesightOptim/rsa_game/dialogs/prompts"
    prompt_files = [
        os.path.join(prompt_dir, f)
        for f in os.listdir(prompt_dir)
        if f.endswith(".txt")
    ]
    corrected_dialog_data = {}
    for key, value in tqdm(problems.items()):
        prompt_file = random.choice(prompt_files)
        with open(prompt_file, "r") as f:
            prompt_template = f.read()
        prompt = prompt_template.format(
            target_referent=value["target_referent"],
            referent_set=value["referent_set"],
            dialog="\n".join(value["chain"]),
        )
        generated_dialog = "\n".join(
            [f"{line['role']}: {line['content']}" for line in value["dialog"]]
        )
        message = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": generated_dialog},
            {
                "role": "user",
                "content": f"There are some problems in the dialog. Please correct them:\n{value['problems']}\n\nPlease return the just the corrected dialog in the following format:\nSpeaker: [Corrected content]\nListener: [Corrected content]\nSpeaker: [Corrected content]\nListener: [Corrected content]\n...",
            },
        ]
        while True:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=message,
                    temperature=1,
                    max_tokens=500,
                )
                corrected_text = response.choices[0].message.content.strip()
                corrected_dialog = []
                for idx, line in enumerate(corrected_text.split("\n")):
                    line = line.strip()
                    if idx % 2 == 0:
                        role = "speaker"
                    else:
                        role = "listener"
                    corrected_dialog.append(
                        {
                            "role": role,
                            "content": ":".join(line.split(":")[1:]).strip(),
                        }
                    )
                    if line.split(":")[0].strip().lower() != role:
                        corrected_dialog = []
                        break
                if len(corrected_dialog) > 0:
                    break

            except Exception as e:
                print(f"========== Error: {e} ==========")
                corrected_dialog = []

        assert corrected_dialog != [], f"The corrected dialog is empty for {key}"
        corrected_dialog_data[key] = {
            "referent_set": value["referent_set"],
            "target_referent": value["target_referent"],
            "dialog": corrected_dialog,
            "chain": value["chain"],
        }
        if os.path.exists(correct_datapath):
            with open(correct_datapath, "r") as f:
                old_data = json.load(f)
            old_data.update(corrected_dialog_data)
        else:
            old_data = corrected_dialog_data
        json.dump(
            old_data,
            open(correct_datapath, "w"),
            indent=2,
            ensure_ascii=False,
        )
    return corrected_dialog_data


if __name__ == "__main__":
    if os.path.exists(args.output_file):
        overwrite = input(
            "The output file already exists. Do you want to overwrite it, continue or exit? (yes/continue/no)"
        )
        if overwrite == "yes":
            os.remove(args.output_file)
        elif overwrite == "continue":
            pass
        else:
            exit()

    data = json.load(open(args.input_file, "r", encoding="utf-8"))
    while True:
        problems = correct_dialogs(data, args.output_file)
        if len(problems) == 0:
            break
        data = process_problems(problems)
