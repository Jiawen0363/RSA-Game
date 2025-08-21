import json
import openai
import time
from typing import List
import argparse
import os
import random
import yaml
from tqdm import tqdm


class DialoguePolisher:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str = "gpt-4.1-mini",
        prompt_dir: str = None,
    ):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        if not prompt_dir:  # rsa_game/
            prompt_dir = "dialogs/prompts"
        self.prompt_dir = prompt_dir
        # Get all available prompt files
        self.prompt_files = [
            os.path.join(prompt_dir, f)
            for f in os.listdir(prompt_dir)
            if f.endswith(".txt")
        ]
        if not self.prompt_files:
            raise ValueError(f"No prompt files found in {prompt_dir}")

    def get_random_prompt_file(self) -> str:
        """Randomly select a prompt file for each dialog"""
        prompt_file = random.choice(self.prompt_files)
        # print(f">>> randomly selected prompt file: {prompt_file}")
        return prompt_file

    def create_polish_prompt(
        self, dialog: List[str], referent_set: List[str], target_referent: str
    ) -> str:
        # Randomly select a prompt file for each dialog
        prompt_file = self.get_random_prompt_file()

        # Read the prompt template file
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        # Replace placeholders
        referent_set = [f"('{', '.join(ref.split(' '))}')" for ref in referent_set]
        prompt = prompt_template.format(
            target_referent=target_referent,
            referent_set=referent_set,
            dialog="\n".join(dialog),
        )

        return prompt

    def polish_single_dialogue(
        self, dialog: List[str], referent_set: List[str], target_referent: str
    ) -> List[str]:
        prompt = self.create_polish_prompt(dialog, referent_set, target_referent)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
            )

            polished_text = response.choices[0].message.content.strip()

            # Parse the polished dialog
            polished_dialogue = []
            for idx, line in enumerate(polished_text.split("\n")):
                line = line.strip()
                if idx % 2 == 0:
                    role = "speaker"
                else:
                    role = "listener"
                polished_dialogue.append(
                    {
                        "role": role,
                        "content": ":".join(line.split(":")[1:]).strip(),
                    }
                )
                if line.split(":")[0].strip().lower() != role:
                    return []

            return polished_dialogue if polished_dialogue else []

        except Exception as e:
            print(f"[Error] error occurred while polishing dialog: {e}")
            return []

    def polish_all_dialogues(
        self, input_file: str, output_file: str, delay: float = 1.0
    ):
        # Read the original data
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        try:
            with open(output_file, "r", encoding="utf-8") as f:
                polished_data = json.load(f)
        except FileNotFoundError:
            polished_data = {}

        for idx, set_data in tqdm(
            enumerate(data), total=len(data), desc="Polishing dialogues"
        ):
            set_name = f"dialog_{idx}"
            # print(f">>> polishing {set_name}...")
            if set_name in polished_data:
                print(f">>> skipping {set_name} because it already exists")
                continue

            # Polish the dialog
            polished_dialogue = self.polish_single_dialogue(
                set_data["dialogue"],
                set_data["referent_set"],
                set_data["target_referent"],
            )

            # Save the polished data
            if len(polished_dialogue) > 0:
                polished_data[set_name] = {
                    "referent_set": set_data["referent_set"],
                    "target_referent": set_data["target_referent"],
                    "dialog": polished_dialogue,
                    "chain": set_data["dialogue"],
                }

                print(
                    f">>> completed {set_name} polishing, {len(polished_dialogue)} turns."
                )
                # save the polished data to a file
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(polished_data, f, indent=2, ensure_ascii=False)

            # Add delay to avoid API rate limits
            time.sleep(delay)

        print(f"[INFO] all dialogues polished, saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Polish dialogues using OpenAI API")
    parser.add_argument(
        "--input_file",
        required=True,
        help="Input JSON file path"
    )
    parser.add_argument(
        "--output_file",
        required=True,
        help="Output JSON file path"
    )
    parser.add_argument(
        "--prompt_dir", required=False, help="Prompt template directory path (optional)"
    )
    args = parser.parse_args()

    # Use args.input_file and args.output_file instead of hardcoded values
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "api_config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    polisher = DialoguePolisher(
        config["api_key"],
        config["base_url"],
        prompt_dir=args.prompt_dir,
    )
    polisher.polish_all_dialogues(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
