import argparse
import json
import os
import random
from copy import deepcopy
HOME_DIR = os.getenv("HOME")

GAME_RULE_PROMPTS = [
    """Play the game of Collabrative Rational Speech Act Game. In this game, there are two players, a speaker and a listener.

At the beginning, the speaker is assigned a target object, with which the listener is not informed. The task of the speaker is to guide the listener to guess the target object, then they win the game. However, the speaker is only allowed to give one feature per turn.

At the same time, the listener tries to figure out the target object and give the possible target referent objects at each turn. The listener can give more than one possible target referent object sets at each turn. If the listener identifies the target object, he can say "I know the target object! It is `target object`!".

At each turn, the speaker should try to give a feature of the target object which provides the listener with the most information, and the listener would update the possible target referent objects from the previous turn.

Remember, the listener can only update his referent set from the previous turn's guess, he cannot add new referents.

The less turns they take to guess the target object, the higher the score they get.
""",
    """Engage in the collaborative challenge of Rational Speech Act Game, featuring two participants: one takes on the role of the speaker, while the other serves as the listener.

Initially, the speaker is secretly assigned a target object, which remains unknown to the listener. The speaker's objective is to strategically guide the listener toward identifying the target object, thereby securing victory. However, there's a constraint: the speaker may only provide one feature per turn.

Simultaneously, the listener's mission is to deduce the target object and present possible target referent objects at each turn. The listener has the flexibility to offer multiple possible target referent object sets during their turn. If the listener identifies the target object, they can declare "I know the target object! It is `target object`!".

During each turn, the speaker should aim to provide a feature of the target object that maximizes the information available to the listener, while the listener updates their possible target referent objects based on the previous turn's information.

Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

The scoring system rewards efficiency: fewer turns required to guess the target object results in higher scores.
""",
    """Dive into the strategic collaboration known as Rational Speech Act Game, where two players assume distinct roles: the speaker and the listener.

To commence the game, the speaker receives a target object in secret, while the listener remains unaware of this object. The speaker's challenge is to effectively guide the listener toward correctly identifying the target object, which would result in a win. However, there's a limitation: the speaker can only share one feature per turn.

Concurrently, the listener embarks on a quest to determine the target object and must present possible target referent objects at each turn. The listener enjoys the advantage of being able to propose multiple possible target referent object sets during their turn. If the listener identifies the target object, they can proclaim "I know the target object! It is `target object`!".

At each turn, the speaker should strategically select a feature of the target object that provides the listener with maximum informational value, while the listener refines their possible target referent objects based on the previous turn's revelations.

Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

The scoring mechanism emphasizes efficiency: achieving the target object identification in fewer turns yields higher scores.
""",
    """Step into the cooperative challenge of Rational Speech Act Game, a game designed for two players: one acting as the speaker, the other as the listener.

In the opening phase, the speaker is discreetly given a target object, which is kept hidden from the listener. The speaker's goal is to successfully lead the listener to identify the target object, thereby claiming victory. However, there's a rule: the speaker is restricted to providing only one feature per turn.

At the same time, the listener's task is to figure out the target object and present possible target referent objects at each turn. The listener has the liberty to suggest multiple possible target referent object sets during their turn. If the listener identifies the target object, they can announce "I know the target object! It is `target object`!".

During each turn, the speaker should carefully choose a feature of the target object that delivers the most valuable information to the listener, while the listener adjusts their possible target referent objects based on the previous turn's insights.

Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

The scoring system prioritizes efficiency: the fewer turns taken to identify the target object, the higher the score achieved.
""",
    """Immerse yourself in the collaborative strategy game called Rational Speech Act Game, featuring two distinct roles: the speaker and the listener.

As the game begins, the speaker is covertly assigned a target object, which remains a mystery to the listener. The speaker's mission is to skillfully guide the listener toward correctly identifying the target object, which would secure a win. However, there's a restriction: the speaker may only offer one feature per turn.

Meanwhile, the listener is engaged in a process of deduction, attempting to determine the target object and presenting possible target referent objects at each turn. The listener benefits from the ability to suggest multiple possible target referent object sets during their turn. If the listener identifies the target object, they can state "I know the target object! It is `target object`!".

At each turn, the speaker should strategically provide a feature of the target object that maximizes the informational benefit for the listener, while the listener updates their possible target referent objects based on the previous turn's information.

Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

The scoring framework rewards efficiency: fewer turns required to identify the target object results in higher scores.
""",
    """Dive into the collaborative challenge known as Rational Speech Act Game, where two players take on specific roles: the speaker and the listener.

The speaker starts the game with a secret target object assignment, while the listener remains in the dark about this object. The speaker's objective is to effectively guide the listener toward identifying the target object, thereby achieving victory. However, there's a constraint: the speaker can only provide one feature per turn.

Concurrently, the listener's challenge is to deduce the target object and present possible target referent objects at each turn. The listener enjoys the flexibility of being able to suggest multiple possible target referent object sets during their turn. If the listener identifies the target object, they can express "I know the target object! It is `target object`!".

During each turn, the speaker should aim to provide a feature of the target object that offers the listener the most valuable information, while the listener refines their possible target referent objects based on the previous turn's revelations.

Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

The scoring mechanism emphasizes efficiency: achieving target object identification in fewer turns yields higher scores.
""",
    """Step into the strategic collaboration called Rational Speech Act Game, where the roles of speaker and listener are central to the gameplay.

The speaker embarks on this journey with a secretly assigned target object, while the listener begins unaware of this object. The speaker's challenge is to successfully guide the listener toward identifying the target object, which would result in a win. However, there's a limitation: the speaker is only permitted to share one feature per turn.

On the other side, the listener's mission is to figure out the target object and present possible target referent objects at each turn. The listener has the advantage of being able to propose multiple possible target referent object sets during their turn. If the listener identifies the target object, they can reveal "I know the target object! It is `target object`!".

At each turn, the speaker should strategically select a feature of the target object that provides the listener with maximum informational value, while the listener updates their possible target referent objects based on the previous turn's insights.

Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

The scoring system prioritizes efficiency: fewer turns taken to identify the target object results in higher scores.
""",
    """Embark on the collaborative challenge of Rational Speech Act Game, where players assume the roles of either speaker or listener.

The speaker enters the game with a covertly assigned target object, while the listener starts without knowledge of this object. The speaker's goal is to effectively guide the listener toward identifying the target object, thereby securing victory. However, there's a rule: the speaker may only provide one feature per turn.

Simultaneously, the listener's task is to deduce the target object and present possible target referent objects at each turn. The listener benefits from the ability to suggest multiple possible target referent object sets during their turn. If the listener identifies the target object, they can declare "I know the target object! It is `target object`!".

During each turn, the speaker should carefully choose a feature of the target object that delivers the most valuable information to the listener, while the listener adjusts their possible target referent objects based on the previous turn's information.

Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

The scoring framework rewards efficiency: the fewer turns required to identify the target object, the higher the score achieved.
""",
]


INSTRUCT_PROMPTS = {
    "speaker": """\n\n### Instruction: You are the pragmatic rational speaker. The target object is `{target}` and the object list is '{object_list}'. Provide your response including the object feature.\n\n### Response:""",
    "listener": """\n\n### Instruction: Your are the pragmatic rational listener. The object list is '{object_list}'. Provide your infered target object or the possible target object sets.\n\n### Response:""",
}

PLAYER_INSTRUCT_PROMPTS = {
    "speaker": "You are the pragmatic rational speaker. The target object is `{target}` and the object list is '{object_list}'. Provide your response including the object feature.",
    "listener": "Your are the pragmatic rational listener. The object list is '{object_list}'. Provide your infered target object or the possible target object sets.",
}


ROLES = ["speaker", "listener"]


def object2str(object_list, random_choice=True):
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
        return format_choices[format](object_list)
    else:
        return {format: func(object_list) for format, func in format_choices.items()}


class DialogToSFTConverter:
    def __init__(self):
        pass

    def _parse_utterance(self, instance, turn):
        dialogue_list = instance["dialog"]
        turn_num = len(dialogue_list)
        # get current utterance
        current_utterance = dialogue_list[turn]

        # parse agent and content (JSON format)
        if isinstance(current_utterance, dict):
            agent = current_utterance["role"]
            current_content = current_utterance["content"]
        else:
            # compatible with old format (string format)
            current_lower = current_utterance.lower()
            if current_lower.startswith("speaker: "):
                agent = "speaker"
                current_content = current_utterance[len("Speaker: "):]  # 去掉 "Speaker: " 前缀   
            elif current_lower.startswith("listener: "):
                agent = "listener"
                current_content = current_utterance[len("Listener: "):]  # 去掉 "Listener: " 前缀
            else:
                raise ValueError(f"Unknown agent role: {current_utterance}")

        # build history (exclude current turn)
        history = []
        for i in range(turn):
            history.append(dialogue_list[i])

        return agent, current_content, turn_num

    def _build_structured_history(self, instance, turn):
        history = []
        for i in range(turn):
            utt = instance["dialog"][i]
            if isinstance(utt, dict):
                # JSON format
                history.append({"role": utt["role"], "content": utt["content"]})
            else:
                # compatible with old format (string format)
                low = utt.lower()
                if low.startswith("speaker: "):
                    history.append({"role": "speaker", "content": utt[9:]})
                elif low.startswith("listener: "):
                    history.append({"role": "listener", "content": utt[10:]})
                else:
                    raise ValueError(f"Unknown agent role: {utt}")
        return history

    def _get_rule_prompt(self, instance, turn):
        # get agent, content, history
        agent, content, turn_num = self._parse_utterance(instance, turn)

        # get dialogue data
        referent_set = instance["referent_set"]
        target_referent = instance["target_referent"]

        # select rule prompt based on agent
        if agent == "speaker":
            return PLAYER_INSTRUCT_PROMPTS["speaker"].format(
                object_list=", ".join(referent_set), target=target_referent
            )
        elif agent == "listener":
            return PLAYER_INSTRUCT_PROMPTS["listener"].format(
                object_list=", ".join(referent_set), target=target_referent  # 多传无碍
            )
        else:
            raise ValueError(f"[ERROR] Unknown agent type: {agent}")

    def convert_turn(self, instance, turn):
        # get query
        query = self.randomly_convert_game_history_to_query(instance, turn)

        # get current turn information
        agent, current_content, turn_num = self._parse_utterance(instance, turn)

        # build sft sample
        sft_sample = {"query": query, "target": current_content, "min_turns": turn_num}

        return sft_sample

    def convert_dialogue(self, instance):
        dialogue_list = instance["dialog"]
        samples = []
        # iterate over each turn
        for turn in range(len(dialogue_list)):
            # convert current turn to sft sample
            sample = self.convert_turn(instance, turn)
            samples.append(sample)
        return samples

    def convert_file(self, input_file, output_file):
        # read input file
        with open(input_file, "r", encoding="utf-8") as f:
            dialogues_dict = json.load(f)

        # open output file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("[\n")  # start json array

            first_sample = True  # for comma control

            # iterate over all dialogues
            for dialog_id, dialog in dialogues_dict.items():
                # convert current dialogue
                samples = self.convert_dialogue(dialog)

                # write samples to file
                for sample in samples:
                    if not first_sample:
                        f.write(",\n")
                    f.write(json.dumps(sample, ensure_ascii=False, indent=2))
                    first_sample = False

            f.write("\n]")  # end json array

    def randomly_convert_game_history_to_query(self, instance, turn):
        history = self._build_structured_history(instance, turn)
        target = instance["target_referent"]
        object_list = object2str(instance["referent_set"])

        if len(history) == 0:
            next_player = ROLES[0]
        else:
            if history[-1]["role"] == ROLES[0]:
                next_player = ROLES[1]
            else:
                next_player = ROLES[0]

        dialog_prefix = "\n" + random.choice(
            ["\n - ", "\n### ", "\n## ", "\n# ", "\n *** ", "\n **", "\n\n"]
        )
        answer_str, question_str = random.choice(
            [
                (next_player, ROLES[1] if next_player == ROLES[0] else ROLES[0]),
                ("Assistant", "Human"),
                ("Answer", "Question"),
                ("Response", "Query"),
                ("A", "Q"),
            ]
        )

        player_prefix = {
            ROLES[0]: answer_str if next_player == ROLES[0] else question_str,
            ROLES[1]: answer_str if next_player == ROLES[1] else question_str,
        }

        history_str = ""
        for i, message in enumerate(history):
            history_str += "{}{}: {}".format(
                dialog_prefix, player_prefix[message["role"]], message["content"]
            )

        prompt_type = random.choice(["chat", "chat_inverse", "alpaca"])
        system_prefix = random.choice(["Rules", "Game Rule", "System"])

        system_prompt = random.choice(GAME_RULE_PROMPTS)
        
        if "chat" in prompt_type:
            system_prompt += "\n\n" + PLAYER_INSTRUCT_PROMPTS[next_player].format(
                target=target,
                object_list=object_list,
            )

            if len(history) == 0:
                history_str = ""
                system_prompt += "The game is just initialized. "

            system_str = f"{dialog_prefix}{system_prefix}: {system_prompt}"
            if "inverse" in prompt_type:
                query = (
                    history_str
                    + system_str
                    + dialog_prefix
                    + player_prefix[next_player]
                    + ": "
                )
            else:
                query = (
                    system_str
                    + history_str
                    + dialog_prefix
                    + player_prefix[next_player]
                    + ": "
                )

        elif prompt_type == "alpaca":
            if random.uniform(0, 1) < 0.2:
                system_prompt = system_prefix + ": " + system_prompt

            if len(history) == 0:
                query = system_prompt + "The game is just initialized. "
            else:
                query = (
                    system_prompt
                    + dialog_prefix
                    + "Game History:"
                    + history_str
                    + "\n\n"
                )

            if random.uniform(0, 1) < 0.2:
                query += (
                    PLAYER_INSTRUCT_PROMPTS[next_player].format(
                        target=target,
                        object_list=object_list,
                    )[:-1]
                    + ": "
                )
            else:
                query += (
                    PLAYER_INSTRUCT_PROMPTS[next_player].format(
                        target=target,
                        object_list=object_list,
                    )
                    + dialog_prefix
                    + player_prefix[next_player]
                    + ": "
                )

        return query


if __name__ == "__main__":
    dialog_path = f"{HOME_DIR}/datasets/rsagame/rsa_dialogs_gpt4.1.json"
    # save_path = f"{HOME_DIR}/codes/ForesightOptim/rsa_game/working/02_dialogs/dialog_to_sft/rsagame_gpt4.1_sft.json"
    save_path = f"{HOME_DIR}/datasets/rsagame/train_imitation_gpt4.1.json"
    converter = DialogToSFTConverter()
    converter.convert_file(dialog_path, save_path)


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "--dialog_path",
#         type=str,
#         default="rsa_game/working/02_dialogs/golden_dialog_polished/golden/sample.json",
#     )
#     parser.add_argument(
#         "--save_path",
#         type=str,
#         default="/home/jiashuo/datasets/rsagame/train_imitation_gpt4.json",
#     )
#     args = parser.parse_args()

#     converter = DialogToSFTConverter(args.dialog_path, args.save_path)

#     # 读入样例数据，取出一个对话对象
#     with open(args.dialog_path, "r", encoding="utf-8") as f:
#         dialogues = json.load(f)

#     dialogue = dialogues["dialogue_2"]  # 或 "dialogue_2"

#     # 可复现实验（可选）
#     random.seed(43)

#     # 测试第 0 轮与第 1 轮
#     print("turn=0:")
#     print(converter._get_rule_prompt(dialogue, 0))
#     print(converter._build_structured_history(dialogue, 0))
#     print("\nturn=2:")
#     print(converter._get_rule_prompt(dialogue, 1))
#     print("---------")
#     print(converter._build_structured_history(dialogue, 1))
#     print("---------")
#     print(converter.randomly_convert_game_history_to_query(dialogue, 1))
#     print("---------")
#     print(converter.convert_turn(dialogue, 1))
