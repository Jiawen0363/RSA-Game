"""
This file is used to generate the dialogue between the rational speaker and a literal listener.
"""

# 调试版本
import os
import sys
import yaml

# Add the correct paths to find the chatarena module and local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
chatarena_parent_path = os.path.join(current_dir, "..")  # Parent directory of chatarena
sys.path.append(os.path.abspath(chatarena_parent_path))
sys.path.append(current_dir)  # Add current directory to find speaker.py

# 调试模式检测
DEBUG_MODE = True  # 调试完改为 False

if DEBUG_MODE:
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "api_config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    os.environ["OPENAI_API_KEY"] = config["api_key"]
    os.environ["OPENAI_API_BASE"] = config["base_url"]

# ===========================================================
# # 使用vLLM
# DEBUG_MODE = True
# if DEBUG_MODE:
#     # 新的本地API设置
#     os.environ["OPENAI_API_KEY"] = "sk-local-dummy-key"
#     os.environ["OPENAI_API_BASE"] = "http://localhost:8000/v1"

# ===========================================================


import json
import random
from typing import List, Optional

from chatarena.agent import Player
from chatarena.backends import OpenAIChat
from chatarena.backends.openai_vllm import VLLMChat
from chatarena.environments import Environment, TimeStep, register_env
from chatarena.message import Message, MessagePool
from speaker import RationalSpeaker
from tqdm import tqdm

sampler = random.Random(42)

SPEAKER_ROLE_DESC = [
    """You are a speaker in a dialogue game. A list of objects is shared between you and a listener. Only you know the target object. 

Each turn, you will provide one feature of the target object to help the listener identify it. The listener will respond with a guess: either one object or a subset of objects that could be the target.

You should act rationally and aim to choose features that best help the listener distinguish the target from the other objects. You must remain rational regardless of how the listener behaves.

One example with the objects [red square, blue ball, blue square] and the target object red square, you say: "It's red."

Use the following object list: {OBJECT_LIST}, and the target object: {TARGET_OBJECT}.

Begin the dialogue by giving one feature of the target object.""",
    """You are the speaker in a reference game. You and a listener are presented with the same list of objects. Only you know which object is the target.

On each turn, your task is to provide one feature of the target to help the listener identify it. The listener will respond with a guess — either a specific object or a subset of possible candidates.

Think carefully about how your message will be interpreted by the listener. Choose a feature that a rational listener would find most helpful. Your goal is to guide the listener’s inferences so they correctly identify the target object.

One example with the objects [red square, blue ball, blue square] and the target object red square, you say: "It's red."

Here is the shared object list: {OBJECT_LIST} and the target object: {TARGET_OBJECT}.

Start the dialogue by stating one feature of the target.""",
    """You are in a cooperative dialogue where your role is to help a listener figure out which object is the target. You both see the same set of objects, but only you know the target.

In each turn, you’ll give one feature of the target to help the listener narrow down the options. The listener replies with a guess — either a single object or a group of potential targets.

Speak with the goal of maximizing clarity in each step. That means it rules out the most potential distractor objects and avoid vague or redundant features.

One example with the objects [red square, blue ball, blue square] and the target object red square, you say: "It's red."

Object list: {OBJECT_LIST}

Target object: {TARGET_OBJECT}

Begin the conversation by giving one feature.""",
    """You are the speaker in a stepwise dialogue game. A list of objects is shown to both you and a listener, but only you know which one is the target.

Each round, share one informative feature of the target. Then, the listener will respond with a guess — either a specific object or a subset.

Choose features that are rationally optimal for distinguishing the target. Your strategy should remain rational, even if the listener is uncertain or inconsistent.

One example with the objects [red square, blue ball, blue square] and the target object red square, you say: "It's red."

Here are the objects: {OBJECT_LIST} and the target object: {TARGET_OBJECT}.

Let’s begin. Provide one feature of the target object.""",
    """You are participating in a dialogue game as the speaker. Both you and the listener are shown the same list of objects. You know the target object.

On each turn, give one feature of the target object. The listener will respond with either a guess or a narrowed-down set of possible objects.

Select your features carefully. Always choose the most informative feature that helps distinguish the target. Your behavior should remain rational throughout, regardless of the listener's responses.

One example with the objects [red square, blue ball, blue square] and the target object red square, you say: "It's red."

The shared object list is: {OBJECT_LIST} and the target object: {TARGET_OBJECT}.

Begin by stating one feature of the target.""",
    """You're in a reference game where your job is to help the listener guess the target object. You both see the same objects: {OBJECT_LIST}, but only you know that the target is {TARGET_OBJECT}.

Every turn, say one feature of the target to help the listener narrow it down. The listener will guess — either one item or a group.

Your goal is to choose the feature that a rational listener would find most helpful in identifying the target — that is, the one that increases the listener's posterior belief in the target object.

Example with [red square, blue ball, blue square] and target red square: you might say "It's red."

Start by giving one feature of the target.""",
    """You're in a guessing dialogue where you are the speaker. Both you and the listener can see a set of objects, but only you know the target object.

In each round, say one feature of the target. The listener will respond with a guess — a specific object or a subset.

Your task is to choose a single, informative feature that helps the listener get closer to the target. You should always act in a rational and efficient way by imagining how a rational listener would interpret your message.

One example with the objects [red square, blue ball, blue square] and the target object red square, you say: "It's red."

The object list is: {OBJECT_LIST} and the target object: {TARGET_OBJECT}.

Begin by giving one feature of the target.""",
    """You are taking part in a turn-based dialogue. A list of visible objects is shared between you and a listener. You know which object is the target.

Each turn, describe one feature of the target. The listener will then guess either the object or a subset of objects they think could be correct.

Be rational in your communication. Choose your features based on what will help the listener narrow down the target most effectively. Your behavior should stay rational in every step.

One example with the objects [red square, blue ball, blue square] and the target object red square, you say: "It's red."

Shared object list: {OBJECT_LIST} and the target object: {TARGET_OBJECT}.

Start now by stating one feature.""",
    """You are playing a dialogue game where your task is to help the listener guess the target object. Both of you see the same list of options, but only you know the target: {TARGET_OBJECT}.

Each turn, say one feature of the target that best helps the listener rule out incorrect options. Pick a feature that is true of the target and false for as many distractors as possible. This helps the listener efficiently narrow down the possibilities. Then, the listener replies with a guess — either one object or a set of candidates.

One example with the objects [red square, blue ball, blue square] and the target object red square, you say: "It's red."

Object list: {OBJECT_LIST}

Target object: {TARGET_OBJECT}

Begin the interaction by giving one useful feature.""",
    """You're a pragmatic and rational speaker in a reference dialogue. You and the listener share a list of objects. Only you know the target.

Each turn, say one feature of the target. The listener will respond with a guess — either an object or a subset.

Pick features that help the listener rule out incorrect options. Always behave rationally as the listener is a rational listener.

One example with the objects [red square, blue ball, blue square] and the target object red square, you say: "It's red."

Object list: {OBJECT_LIST} and the target object: {TARGET_OBJECT}.

Start by providing one feature of the target.""",
]


LISTENER_ROLE_DESC = [
    """You are the listener in a reference dialogue game. You and the speaker share the same list of objects: {OBJECT_LIST}. The speaker knows the target object and will give you one feature per turn to help you identify it.

After each feature, you must respond with a guess — either a single object or a subset of objects.

Importantly, you are a **rational, pragmatic listener**. This means you don’t just consider which objects match the feature literally — you reason about **why a rational speaker would have chosen that particular feature**. Use this inference to update your beliefs about the target.

Example:
- Objects: [red square, blue ball, blue square]
- You respond: "It's red square."

Wait for the speaker’s feature and respond with your best pragmatic guess.""",
    """You are a pragmatic listener in a cooperative dialogue game. The speaker knows the target object and will describe it one feature at a time. You and the speaker see the same set of objects: {OBJECT_LIST}.

After each clue, guess which object is the target — either a single object or a group of likely candidates.

As a **rational listener**, you reason not only about which objects match the feature, but also about **why the speaker chose that feature**. Consider what a helpful speaker would say to distinguish the target, and update your beliefs accordingly.

Example:
- Feature: "It's red"
- You say: "It's red square"

Use this pragmatic reasoning to guide your guesses and respond with either a single object or a subset of objects.""",
    """You are the listener in a reference game. The speaker will give you one feature of the target object per turn. You and the speaker share the same list: {OBJECT_LIST}, but only the speaker knows the target.

After each feature, respond with a rational guess: either one object or a subset.

You are a **Bayesian listener** in a Rational Speech Act framework. Infer what object the speaker likely intended to indicate, given their choice of feature. Ask yourself: *Among the possible targets, which would make the speaker choose this feature?*

Example:
- Feature: "It's red"
- So you guess: "It's red square"

Respond pragmatically, based on what the speaker likely intended and respond with either a single object or a subset of objects.""",
    """You are the pragmatic listener in a reference dialogue task. You and the speaker share the object list: {OBJECT_LIST}. The speaker knows the target and will describe it one feature at a time.

After each feature, you must guess the target — either a single object or a subset of plausible options.

You are expected to reason **pragmatically**, not just literally. That is, you should consider **why** the speaker chose a particular feature, and what that implies about the target. A helpful speaker chooses features to distinguish the target — so reverse-engineer their choice.

Example:
- Objects: [red square, blue ball, blue square]
- You respond: "It's red square"

Base your response on this type of rational inference and respond with either a single object or a subset of objects.""",
    """You are a Rational Speech Act (RSA) listener in a reference game. You and the speaker both see the same list of objects: {OBJECT_LIST}, but only the speaker knows the target.

Each turn, the speaker gives one feature of the target. You must guess which object it is — either a single object or a set of likely candidates.

As a pragmatic listener, you reason about the speaker's **intent**: what feature would a rational speaker choose to help you identify the target? Use this to update your beliefs about the most likely object.

Example:
- Feature: "It's red"
- You reply: "It's red square"

Respond as a pragmatic listener at every turn and respond with either a single object or a subset of objects.""",
    """You are the pragmatic listener in a reference dialogue task. A list of objects is visible to both you and a speaker. The speaker knows which object is the target, and will describe one feature of it on each turn.

After each feature is revealed, your task is to respond with a guess: either a single object or a subset of the objects that could match the speaker’s description.

One example with the objects [red square, blue ball, blue square], the spekaer says "It's red" you say: "It's red square."

Use the shared object list: {OBJECT_LIST}

Wait for the speaker’s feature, then reply with your best guess (either a single object or a subset of objects) based on the current information.""",
    """You are playing a guessing game as a pragmatic listener. You and a speaker see the same list of objects. The speaker knows the secret target object and will give you one feature at a time to help you guess it.

After each feature, you should respond with a guess — either the object you think it is, or a set of objects that could still be the target.

One example with the objects [red square, blue ball, blue square], the spekaer says "It's red" you say: "It's red square."

Use the object list: {OBJECT_LIST}

Listen carefully, and respond with either a single object or a subset of objects after each clue.""",
    """You are collaborating with a speaker to identify a secret object from a shared list as a pragmatic listener. Only the speaker knows the target. On each turn, they will provide one feature of the target object.

Your role is to update your belief based on the features you hear, and respond with a guess: either a single object or a group of objects that match all features so far.

One example with the objects [red square, blue ball, blue square], the spekaer says "It's red" you say: "It's red square."

Object list: {OBJECT_LIST}

Wait for the feature and then respond with either a single object or a subset of objects.""",
    """You are a pragmatic listener in a dialogue. Both you and the speaker see the same list of objects: {OBJECT_LIST}. The speaker knows the target and will give you one feature at a time.

After each feature, update your belief about which object might be the target. Reply with a guess: either one object or a subset.

One example with the objects [red square, blue ball, blue square], the spekaer says "It's red" you say: "It's red square."

Continue this process after each new feature by responding with either a single object or a subset of objects.""",
    """You are in a dialogue where your task is to infer the target object from a visible list as a pragmatic listener. You and the speaker share the same object list: {OBJECT_LIST}.

The speaker knows the target and will give one feature per turn. After each feature, make an informed guess — either a single object or a narrowed-down set.

One example with the objects [red square, blue ball, blue square], the spekaer says "It's red" you say: "It's red square."

Reply at each turn with either a single object or a subset of objects.""",
]


@register_env
class RSAGame(Environment):
    def __init__(
        self,
        player_names: List[str],
        object_list: List[str],
        target_object: str,
        **kwargs,
    ):
        super().__init__(
            player_names=player_names,
            object_list=object_list,
            target_object=target_object,
            **kwargs,
        )
        self.object_list = object_list
        self.target_object = target_object

        self.message_pool = MessagePool()

        # Game states
        self._current_turn = 0
        self._next_player_idx = 0
        self._initialized = False

        self.reset()

    def get_next_player(self) -> str:
        """Get the next player."""
        return self.player_names[self._next_player_idx]

    def reset(self):
        """The current objects are set in the constructor."""
        self.available_objects = list(self.object_list)

        self._current_turn = 0
        self._next_player_idx = 0

        self.message_pool.reset()
        self._initialized = True

        init_timestep = TimeStep(
            observation=self.get_observation(),
            reward=self.get_zero_rewards(),
            terminal=False,
        )
        return init_timestep

    def print(self):
        self.message_pool.print()

    def get_observation(self, player_name=None) -> List[Message]:
        """Get observation for the player."""
        if player_name is None:
            return self.message_pool.get_all_messages()
        else:
            return self.message_pool.get_visible_messages(
                player_name, turn=self._current_turn
            )

    def step(self, player_name: str, action: str) -> TimeStep:
        """
        Step function that is called by the arena.

        Args:
            player_name: the name of the player that takes the action
            action: the action that the agents wants to take
        """
        if not self._initialized:
            self.reset(self.object_list, self.target_object)

        assert (
            player_name == self.get_next_player()
        ), f"Wrong player! It is {self.get_next_player()} turn."
        message = Message(
            agent_name=player_name, content=action, turn=self._current_turn
        )
        self.message_pool.append_message(message)

        # update the counters
        self._current_turn += 1
        self._next_player_idx = (self._next_player_idx + 1) % len(self.player_names)

        if player_name == "listener":
            self.update_available_objects()

        timestep = TimeStep(
            observation=self.get_observation(),
            reward=self.get_zero_rewards(),
            terminal=False,
        )

        if self.is_terminal():
            timestep.terminal = True

        return timestep

    def update_available_objects(self):
        """Update the available objects."""
        answer = self.message_pool.last_message.content
        guess_objs = []
        for obj in self.object_list:
            if obj in answer:
                guess_objs.append(obj)
        if self.target_object in guess_objs:
            self.available_objects = guess_objs

    def is_terminal(self) -> bool:
        """Check if the conversation is over: the listener has guessed the target object."""
        if self.message_pool.last_message is None:
            return False
        answer = self.message_pool.last_message.content
        guess_objs = []
        for obj in self.object_list:
            if obj in answer:
                guess_objs.append(obj)
        if len(guess_objs) == 1 and guess_objs[0] == self.target_object:
            return True
        return False

    def sily_listener(self) -> bool:
        """A simple listener that guesses the target object based on the last message."""
        answer = self.message_pool.last_message.content
        if answer is None or self.target_object.lower() not in answer.lower():
            return True
        return False


def main():
    # read the referent sets generated in the first step
    referents_path = f"{os.getenv('HOME')}/datasets/rsagame/02_referent_sets/sample_referent_sets.json"
    with open(referents_path, "r") as f:
        referents = json.load(f)

    for idx in tqdm(
        range(len(referents)), desc="Generating dialogues", total=len(referents)
    ):
        key = f"referent_set_{idx+1}"
        item = referents[idx]  # Each item is a dictionary
        value = item["referent_set"]  # Get the referent_set list
        object_list = random.sample(value, len(value))
        target_object = item["target_referent"]  # Get the target_referent
        # =================================================================================
        speaker = RationalSpeaker(
            backend=OpenAIChat(model="gpt-4o-mini"),
            role_desc=random.choice(SPEAKER_ROLE_DESC).format(
                OBJECT_LIST=object_list, TARGET_OBJECT=target_object
            ),
            global_prompt="You are a speaker.",
            target_object=target_object,
        )
        listener = Player(
            name="listener",
            role_desc=random.choice(LISTENER_ROLE_DESC).format(OBJECT_LIST=object_list),
            backend=OpenAIChat(model="gpt-4o-mini"),
            global_prompt="You are a listener.",
        )
        # =================================================================================
        # speaker = RationalSpeaker(
        #     backend=VLLMChat(
        #         vllm_api_key="dummy-key",
        #         vllm_endpoint="http://localhost:8000/v1",
        #         model_name_or_path="gpt-4o-mini",
        #         temperature=0.7,
        #         top_p=0.95,
        #         max_tokens=256,
        #         max_latest_messages=-1
        #     ),
        #     role_desc=random.choice(SPEAKER_ROLE_DESC).format(
        #         OBJECT_LIST=object_list, TARGET_OBJECT=target_object
        #     ),
        #     global_prompt="You are a speaker.",
        #     target_object=target_object,
        # )
        # listener = Player(
        #     name="listener",
        #     role_desc=random.choice(LISTENER_ROLE_DESC).format(OBJECT_LIST=object_list),
        #     backend=VLLMChat(
        #         vllm_api_key="dummy-key",
        #         vllm_endpoint="http://localhost:8000/v1",
        #         model_name_or_path="gpt-4o-mini",
        #         temperature=0.7,
        #         top_p=0.95,
        #         max_tokens=256,
        #         max_latest_messages=-1
        #     ),
        #     global_prompt="You are a listener.",
        # )
        # =================================================================================
        dialogue = RSAGame(
            player_names=[speaker.name, listener.name],
            object_list=object_list,
            target_object=target_object,
        )

        sily_listener = False
        sily_times = 0
        print(f"Target object: {target_object}")
        print(f"Object list: {value}")
        while not dialogue.is_terminal():
            speaker_act = speaker.act(dialogue.available_objects, sily_listener)
            print(f"****** [Speaker]: {speaker_act}")
            dialogue.step(speaker.name, speaker_act)
            valid_act = False
            while True:
                listener_act = listener.act(dialogue.get_observation(listener.name))
                for obj in object_list:
                    if obj.lower() in listener_act.lower():
                        valid_act = True
                        break
                if valid_act:
                    break
                else:
                    print(
                        f">>> [Warning]: For {listener.name}, {listener_act} is not valid, please try again."
                    )
            print(f"****** [Listener]: {listener_act}")
            dialogue.step(listener.name, listener_act)
            sily_listener = dialogue.sily_listener()
            if sily_listener:
                sily_times += 1
            if sily_times > 2:
                break

        if sily_times > 2:
            print(f">>> [Error] Sily listener times: {sily_times}")
            print(f">>> [Error] Dialogue: {dialogue.message_pool.get_all_messages()}")
            print(f">>> [Skip] Dialogue {key} skipped due to silly listener.")
            continue  # 跳过当前对话，继续下一个

        # the dialogue format should be like this:
        # {"index": key, "dialogue": [{"role": "speaker", "content": "..."}, {"role": "listener", "content": "..."}, ...]}
        # thus the dialogue_list is List[Dict[str, Any]], and each dialogue is a List[Dict[str, str]]
        try:
            with open(f"dialogue.json", "r") as f:
                dialogue_list = json.load(f)
        except FileNotFoundError:
            dialogue_list = []
        conversation = []
        for message in dialogue.message_pool.get_all_messages():
            if message.agent_name == "RationalSpeaker":
                conversation.append("Speaker: " + message.content)
            else:
                conversation.append("Listener: " + message.content)

        # Add metadata about the dialogue
        dialogue_data = {
            "referent_set": object_list,
            "dialogue": conversation,
            "target_referent": target_object,
            "sily_times": sily_times,
        }

        dialogue_list.append(dialogue_data)
        with open(f"dialogue3.json", "w") as f:
            json.dump(dialogue_list, f, indent=4)

        print(f">>> [Save] Dialogue {key} saved.")


if __name__ == "__main__":
    main()
