import argparse
import json
import random


GAME_RULE_PROMPTS = [
    """ Play the game of Collabrative Rational Speech Act Game. In this game, there are two players, a speaker and a listener.
    
    At the beginning, the speaker is assigned a target object, with which the listener is not informed. The task of the speaker is to guide the listener to guess the target object, then they win the game. However, the speaker is only allowed to give one feature per turn.
    
    At the same time, the listener tries to figure out the target object and give the possible target referent objects at each turn. The listener can give more than one possible target referent object sets at each turn. If the listener identifies the target object, he can say "I know the target object! It is `target object`!".
    
    At each turn, the speaker should try to give a feature of the target object which provides the listener with the most information, and the listener would update the possible target referent objects from the previous turn.

    Remember, the listener can only update his referent set from the previous turn's guess, he cannot add new referents.
    
    The less turns they take to guess the target object, the higher the score they get.
    """,
    """
    Engage in the collaborative challenge of Rational Speech Act Game, featuring two participants: one takes on the role of the speaker, while the other serves as the listener.

    Initially, the speaker is secretly assigned a target object, which remains unknown to the listener. The speaker's objective is to strategically guide the listener toward identifying the target object, thereby securing victory. However, there's a constraint: the speaker may only provide one feature per turn.

    Simultaneously, the listener's mission is to deduce the target object and present possible target referent objects at each turn. The listener has the flexibility to offer multiple possible target referent object sets during their turn. If the listener identifies the target object, they can declare "I know the target object! It is `target object`!".

    During each turn, the speaker should aim to provide a feature of the target object that maximizes the information available to the listener, while the listener updates their possible target referent objects based on the previous turn's information.

    Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

    The scoring system rewards efficiency: fewer turns required to guess the target object results in higher scores.
    """,
        """
    Dive into the strategic collaboration known as Rational Speech Act Game, where two players assume distinct roles: the speaker and the listener.

    To commence the game, the speaker receives a target object in secret, while the listener remains unaware of this object. The speaker's challenge is to effectively guide the listener toward correctly identifying the target object, which would result in a win. However, there's a limitation: the speaker can only share one feature per turn.

    Concurrently, the listener embarks on a quest to determine the target object and must present possible target referent objects at each turn. The listener enjoys the advantage of being able to propose multiple possible target referent object sets during their turn. If the listener identifies the target object, they can proclaim "I know the target object! It is `target object`!".

    At each turn, the speaker should strategically select a feature of the target object that provides the listener with maximum informational value, while the listener refines their possible target referent objects based on the previous turn's revelations.

    Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

    The scoring mechanism emphasizes efficiency: achieving the target object identification in fewer turns yields higher scores.
    """,
        """
    Step into the cooperative challenge of Rational Speech Act Game, a game designed for two players: one acting as the speaker, the other as the listener.

    In the opening phase, the speaker is discreetly given a target object, which is kept hidden from the listener. The speaker's goal is to successfully lead the listener to identify the target object, thereby claiming victory. However, there's a rule: the speaker is restricted to providing only one feature per turn.

    At the same time, the listener's task is to figure out the target object and present possible target referent objects at each turn. The listener has the liberty to suggest multiple possible target referent object sets during their turn. If the listener identifies the target object, they can announce "I know the target object! It is `target object`!".

    During each turn, the speaker should carefully choose a feature of the target object that delivers the most valuable information to the listener, while the listener adjusts their possible target referent objects based on the previous turn's insights.

    Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

    The scoring system prioritizes efficiency: the fewer turns taken to identify the target object, the higher the score achieved.
    """,
        """
    Immerse yourself in the collaborative strategy game called Rational Speech Act Game, featuring two distinct roles: the speaker and the listener.

    As the game begins, the speaker is covertly assigned a target object, which remains a mystery to the listener. The speaker's mission is to skillfully guide the listener toward correctly identifying the target object, which would secure a win. However, there's a restriction: the speaker may only offer one feature per turn.

    Meanwhile, the listener is engaged in a process of deduction, attempting to determine the target object and presenting possible target referent objects at each turn. The listener benefits from the ability to suggest multiple possible target referent object sets during their turn. If the listener identifies the target object, they can state "I know the target object! It is `target object`!".

    At each turn, the speaker should strategically provide a feature of the target object that maximizes the informational benefit for the listener, while the listener updates their possible target referent objects based on the previous turn's information.

    Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

    The scoring framework rewards efficiency: fewer turns required to identify the target object results in higher scores.
    """,
        """
    Dive into the collaborative challenge known as Rational Speech Act Game, where two players take on specific roles: the speaker and the listener.

    The speaker starts the game with a secret target object assignment, while the listener remains in the dark about this object. The speaker's objective is to effectively guide the listener toward identifying the target object, thereby achieving victory. However, there's a constraint: the speaker can only provide one feature per turn.

    Concurrently, the listener's challenge is to deduce the target object and present possible target referent objects at each turn. The listener enjoys the flexibility of being able to suggest multiple possible target referent object sets during their turn. If the listener identifies the target object, they can express "I know the target object! It is `target object`!".

    During each turn, the speaker should aim to provide a feature of the target object that offers the listener the most valuable information, while the listener refines their possible target referent objects based on the previous turn's revelations.

    Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

    The scoring mechanism emphasizes efficiency: achieving target object identification in fewer turns yields higher scores.
    """,
        """
    Step into the strategic collaboration called Rational Speech Act Game, where the roles of speaker and listener are central to the gameplay.

    The speaker embarks on this journey with a secretly assigned target object, while the listener begins unaware of this object. The speaker's challenge is to successfully guide the listener toward identifying the target object, which would result in a win. However, there's a limitation: the speaker is only permitted to share one feature per turn.

    On the other side, the listener's mission is to figure out the target object and present possible target referent objects at each turn. The listener has the advantage of being able to propose multiple possible target referent object sets during their turn. If the listener identifies the target object, they can reveal "I know the target object! It is `target object`!".

    At each turn, the speaker should strategically select a feature of the target object that provides the listener with maximum informational value, while the listener updates their possible target referent objects based on the previous turn's insights.

    Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

    The scoring system prioritizes efficiency: fewer turns taken to identify the target object results in higher scores.
    """,
        """
    Embark on the collaborative challenge of Rational Speech Act Game, where players assume the roles of either speaker or listener.

    The speaker enters the game with a covertly assigned target object, while the listener starts without knowledge of this object. The speaker's goal is to effectively guide the listener toward identifying the target object, thereby securing victory. However, there's a rule: the speaker may only provide one feature per turn.

    Simultaneously, the listener's task is to deduce the target object and present possible target referent objects at each turn. The listener benefits from the ability to suggest multiple possible target referent object sets during their turn. If the listener identifies the target object, they can declare "I know the target object! It is `target object`!".

    During each turn, the speaker should carefully choose a feature of the target object that delivers the most valuable information to the listener, while the listener adjusts their possible target referent objects based on the previous turn's information.

    Remember, the listener can only update their referent set from the previous turn's guess; they cannot add new referents.

    The scoring framework rewards efficiency: the fewer turns required to identify the target object, the higher the score achieved.
    """
]


INSTRUCT_PROMPTS = {
    "speaker": '''\n\n### Instruction: You are the pragmatic rational speaker. The target object is `{TARGET_OBJECT}` and the object list is '{OBJECT_LIST}'. Provide your response including the object feature.\n\n### Response:''',
    "listener": '''\n\n### Instruction: Your are the pragmatic rational listener. The object list is '{OBJECT_LIST}'. Provide your infered target object or the possible target object sets.\n\n### Response:'''
}

PLAYER_INSTRUCT_PROMPTS = {
    "speaker": "You are the pragmatic rational speaker. The target object is `{TARGET_OBJECT}` and the object list is '{OBJECT_LIST}'. Provide your response including the object feature.",
    "listener": "Your are the pragmatic rational listener. The object list is '{OBJECT_LIST}'. Provide your infered target object or the possible target object sets.",
}


ROLES = ["speaker", "listener"]

LISTENER_ROLE_DESC = [
    """You are the listener in a dialogue game. A list of objects is visible to both you and a speaker. The speaker knows which object is the target, and will describe one feature of it on each turn.
After each feature is revealed, your task is to respond with a guess: either a single object or a subset of the objects that could match the speaker’s description.
Use the shared object list: {OBJECT_LIST}
Wait for the speaker’s feature, then reply with your best guess (either a single object or a subset of objects) based on the current information.""",
    """You are playing a guessing game as the listener. You and a speaker see the same list of objects. The speaker knows the secret target object and will give you one feature at a time to help you guess it.
After each feature, you should respond with a guess — either the object you think it is, or a set of objects that could still be the target.
Use the object list: {OBJECT_LIST}
Listen carefully, and respond with either a single object or a subset of objects after each clue.""",
    """You are collaborating with a speaker to identify a secret object from a shared list. Only the speaker knows the target. On each turn, they will provide one feature of the target object.
Your role is to update your belief based on the features you hear, and respond with a guess: either a single object or a group of objects that match all features so far.
Object list: {OBJECT_LIST}
Wait for the feature and then respond with either a single object or a subset of objects.""",
    """You are the listener in a dialogue. Both you and the speaker see the same list of objects: {OBJECT_LIST}. The speaker knows the target and will give you one feature at a time.
After each feature, update your belief about which object might be the target. Reply with a guess: either one object or a subset.
Continue this process after each new feature by responding with either a single object or a subset of objects.""",
    """You are in a dialogue where your task is to infer the target object from a visible list. You and the speaker share the same object list: {OBJECT_LIST}.
The speaker knows the target and will give one feature per turn. After each feature, make an informed guess — either a single object or a narrowed-down set.
Reply at each turn with either a single object or a subset of objects.""",
    """You are the listener in a dialogue. The speaker knows the target object and will give you one feature per turn.
Based on the feature and this object list: {OBJECT_LIST}, respond with either a single object or a subset of objects.""",
    """You are acting as a deductive agent in a feature-based guessing game. You and the speaker see the same object list: {OBJECT_LIST}.
The speaker knows the target and will give you one feature at a time. Your task is to deduce which object it could be.
After each feature, respond with a guess — either one object or a subset of objects that fits all features so far.""",
    """You are the listener in a reference dialogue. The speaker will describe features of a hidden target object, one per turn.
You and the speaker see the same list: {OBJECT_LIST}. Use the features mentioned so far to track your belief about what the target might be.
After each turn, reply with either a single object or a subset of objects that still consistent with the features.""",
    """You are participating in an object identification dialogue. You and the speaker share the following object list: {OBJECT_LIST}.
The speaker knows the target and will give you features of it one by one. After each feature, respond by selecting either a single object or a subset of objects that match what you’ve heard so far.""",
    """You are the listener in a turn-based guessing game. A speaker is helping you find a secret object by providing one feature at a time. You both see the same list: {OBJECT_LIST}. After each feature, respond with either a single object or a subset of objects that still fit the description.
    """,
]

SPEAKER_ROLE_DESC = [
    """You are the speaker in a dialogue game. A list of objects is visible to both you and a listener. You know which object is the target: {TARGET_OBJECT}, and will describe one feature of it on each turn.
After each turn, the listener will respond with a guess. Your task is to provide helpful features that guide them toward the correct target.
Use the shared object list: {OBJECT_LIST}
Your target object is: {TARGET_OBJECT}
Describe one feature of the target object to help the listener guess correctly.""",
    """You are playing a guiding game as the speaker. You and a listener see the same list of objects. You know the secret target object: {TARGET_OBJECT}, and will give one feature at a time to help the listener guess it.
After each feature, the listener will respond with a guess. Provide strategic features that narrow down the possibilities.
Use the object list: {OBJECT_LIST}
Your target object is: {TARGET_OBJECT}
Give one feature that will help the listener identify the target.""",
    """You are collaborating with a listener to identify a secret object from a shared list. Only you know the target: {TARGET_OBJECT}. On each turn, you will provide one feature of the target object.
Your role is to give helpful clues that allow the listener to narrow down their choices and eventually identify the correct target.
Object list: {OBJECT_LIST}
Your target object is: {TARGET_OBJECT}
Provide one feature that will guide the listener toward the correct answer.""",
    """You are the speaker in a dialogue. Both you and the listener see the same list of objects: {OBJECT_LIST}. You know the target: {TARGET_OBJECT}, and will give one feature at a time.
After each feature, the listener will update their belief and respond with a guess. Help them by providing clear, distinguishing features.
Your target object is: {TARGET_OBJECT}
Continue this process by describing one feature that will help the listener identify the target.""",
    """You are in a dialogue where your task is to guide the listener to identify the target object from a visible list. You and the listener share the same object list: {OBJECT_LIST}.
You know the target: {TARGET_OBJECT}, and will give one feature per turn. After each feature, the listener will make an informed guess.
Your target object is: {TARGET_OBJECT}
Reply at each turn with one feature that will help the listener identify the target.""",
    """You are the speaker in a dialogue. You know the target object: {TARGET_OBJECT}, and will give one feature per turn.
Based on the target and this object list: {OBJECT_LIST}, provide one feature that will help the listener identify the correct object.""",
    """You are acting as a guiding agent in a feature-based dialogue game. You and the listener see the same object list: {OBJECT_LIST}.
You know the target: {TARGET_OBJECT}, and will give one feature at a time. Your task is to provide helpful clues that lead to the correct identification.
Your target object is: {TARGET_OBJECT}
After each turn, provide one feature that will help the listener identify the target.""",
    """You are the speaker in a reference dialogue. You will describe features of the hidden target object: {TARGET_OBJECT}, one per turn.
You and the listener see the same list: {OBJECT_LIST}. Use your knowledge of the target to provide helpful features that guide the listener.
Your target object is: {TARGET_OBJECT}
After each turn, provide one feature that will help the listener identify the target.""",
    """You are participating in an object identification dialogue. You and the listener share the following object list: {OBJECT_LIST}.
You know the target: {TARGET_OBJECT}, and will give features of it one by one. After each feature, the listener will respond with their current understanding.
Your target object is: {TARGET_OBJECT}
Provide one feature that will help the listener identify the target.""",
    """You are the speaker in a turn-based guiding game. You are helping a listener find a secret object by providing one feature at a time. You both see the same list: {OBJECT_LIST}. After each feature, the listener will respond with their current guess.
You know the target: {TARGET_OBJECT}, and will give features of it one by one. After each feature, the listener will respond with their current understanding.
Your target object is: {TARGET_OBJECT}
Provide one feature that will help the listener identify the target.""",
]


class DialogToSFTConverter:
    def __init__(self, dialog_path: str, sft_path: str):
        self.dialog_path = dialog_path
        self.sft_path = sft_path

    def _parse_utterance(self, dialogue_i, turn):
        dialogue_list = dialogue_i["dialogue"]

        # 获取当前轮次的对话
        current_utterance = dialogue_list[turn]

        # 解析说话人和内容（不区分大小写）
        current_lower = current_utterance.lower()
        if current_lower.startswith("speaker: "):
            agent = "speaker"
            content = current_utterance[9:]  # 去掉 "Speaker: " 前缀
        elif current_lower.startswith("listener: "):
            agent = "listener"
            content = current_utterance[10:]  # 去掉 "Listener: " 前缀
        else:
            raise ValueError(f"无法识别说话人: {current_utterance}")

        # build history (exclude current turn)
        history = []
        for i in range(turn):
            history.append(dialogue_list[i])

        return agent, content, history

    def _get_rule_prompt(self, dialogue_i, turn):
        # get agent, content, history
        agent, content, history = self._parse_utterance(dialogue_i, turn)

        # get dialogue data
        referent_set = dialogue_i["referent_set"]
        target_referent = dialogue_i["target_referent"]

        # select rule prompt based on agent
        if agent == "speaker":
            # select from SPEAKER_ROLE_DESC
            prompt_template = random.choice(SPEAKER_ROLE_DESC)
            # fill referent_set and target_referent
            filled_prompt = prompt_template.format(
                OBJECT_LIST=referent_set, TARGET_OBJECT=target_referent
            )
        elif agent == "listener":
            # select from LISTENER_ROLE_DESC
            prompt_template = random.choice(LISTENER_ROLE_DESC)
            # fill referent_set (listener doesn't know target_referent)
            filled_prompt = prompt_template.format(OBJECT_LIST=referent_set)
        else:
            raise ValueError(f"[ERROR] Unknown agent type: {agent}")

        return filled_prompt

    def _build_query(self, dialogue_i, turn):
        # get rule prompt
        rule_prompt = self._get_rule_prompt(dialogue_i, turn)

        # get conversation history
        agent, content, history = self._parse_utterance(dialogue_i, turn)

        # build query
        if history:
            # if there is conversation history, concatenate rule prompt + history
            conversation_history = "\n".join(history)
            query = f"{rule_prompt}\n{conversation_history}\n{agent.capitalize()}: "
        else:
            # if it's the first turn, only rule prompt
            query = f"{rule_prompt}\n{agent.capitalize()}: "

        return query

    def convert_turn(self, dialogue_i, turn):
        # get query
        query = self._build_query(dialogue_i, turn)

        # get current turn information
        agent, content, history = self._parse_utterance(dialogue_i, turn)

        # build sft sample
        sft_sample = {"query": query, "target": content, "agent": agent}

        return sft_sample

    def convert_dialogue(self, dialogue_i):
        dialogue_list = dialogue_i["dialogue"]
        samples = []
        # iterate over each turn
        for turn in range(len(dialogue_list)):
            # convert current turn to sft sample
            sample = self.convert_turn(dialogue_i, turn)
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
            for dialogue_name, dialogue_data in dialogues_dict.items():
                # convert current dialogue
                samples = self.convert_dialogue(dialogue_data)

                # write samples to file
                for sample in samples:
                    if not first_sample:
                        f.write(",\n")
                    f.write(json.dumps(sample, ensure_ascii=False, indent=2))
                    first_sample = False

            f.write("\n]")  # end json array


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dialog_path",
        type=str,
        required=True,
        default="rsa_game/working/02_dialogs/golden_dialog_polished/golden/sample.json",
    )
    parser.add_argument(
        "--save_path",
        type=str,
        required=True,
        default="/home/jiashuo/datasets/rsagame/train_imitation_gpt4.json",
    )
    args = parser.parse_args()

    converter = DialogToSFTConverter(args.dialog_path, args.save_path)
    converter.convert_file(args.dialog_path, args.save_path)
