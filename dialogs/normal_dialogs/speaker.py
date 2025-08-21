"""
This file is used to build a rational speaker.
"""

import random
from typing import List, Union
# from golden_dialogue.RSA_speaker import ranked_position_of_target
from chatarena.agent import Player
from chatarena.message import Message
from speaker_utils import SpeakerUtils
import openai


class RationalSpeaker(Player):
    def __init__(self, backend, role_desc, global_prompt, target_object, **kwargs):
        name = "RationalSpeaker"
        super().__init__(name, role_desc, backend, global_prompt, **kwargs)
        self.target_object = target_object
        self.target_features = self.target_object.split(" ")
        self.random = random.Random(42)

    def act(self, objects: List[str], sily_listener: bool) -> str:
        target_idx = objects.index(self.target_object)

        # ranks = []
        # for feature in self.target_features:
        #     rank = ranked_position_of_target(objects, feature, target_idx)
        #     assert rank is not None, "Rank is None"
        #     ranks.append(rank)
        # feature = self.target_features[ranks.index(min(ranks))]
        feature = SpeakerUtils(objects, target_idx).first_ranked_target_feature()

        if sily_listener:
            contents = [
                f"The listener's guess did not include the target object. Please repeat the feature you mentioned earlier — {feature} — and naturally ask the listener to guess again.",
                f"The listener excluded the target from their guess. Just repeat the previous feature — {feature} — and kindly ask them to try guessing again.",
                f"The listener's guess did not include the target object. Please repeat the feature you mentioned earlier — {feature} — and naturally ask the listener to guess agai from {objects}.",
                f"The listener excluded the target from their guess. Just repeat the previous feature — {feature} — and kindly ask them to try guessing again from {objects}."
                f"Hmm, the listener didn’t include the target. Just repeat your last feature — {feature} — and ask them to try guessing again.",
                f"The listener missed the target. Say {feature} again and gently ask them to take another guess.",
                f"It looks like the listener didn’t choose the target. Repeat the feature — {feature} — and invite them to guess again from this group: {objects}.",
                f"The listener’s guess was off. Please say {feature} again and ask them to try once more using this list: {objects}.",
            ]

        else:
            contents = [
                f"Based on your reasoning, the next feature to provide is: {feature}. Tell the listener this informatuon naturally in a single sentence.",
                f"You’ve determined that the next helpful feature is: {feature}. Tell it to the listener in a single, natural-sounding sentence.",
                f"Your next feature should be: {feature}. Tell it to the listener naturally as part of the dialogue.",
                f"The most informative feature to say now is: {feature}. Tell it to the listener clearly in one natural sentence.",
            ]

        content = self.random.choice(contents)
        observation = [Message(agent_name="User Prompt", content=content, turn=1)]

        response = super().act(observation)

        return response

    async def async_act(self, objects: List[str], sily_listener: bool) -> str:
        target_idx = objects.index(self.target_object)
        referent_features = [o.split(" ") for o in objects]

        # ranks = []
        # for feature in self.target_features:
        #     rank = ranked_position_of_target(referent_features, feature, target_idx)
        #     assert rank is not None, "Rank is None"
        #     ranks.append(rank)
        # feature = self.target_features[ranks.index(min(ranks))]
        feature = SpeakerUtils(objects, target_idx).first_ranked_target_feature()

        if sily_listener:
            contents = [
                f"The listener's guess did not include the target object. Please repeat the feature you mentioned earlier — {feature} — and naturally ask the listener to guess again.",
                f"The listener excluded the target from their guess. Just repeat the previous feature — {feature} — and kindly ask them to try guessing again.",
                f"The listener's guess did not include the target object. Please repeat the feature you mentioned earlier — {feature} — and naturally ask the listener to guess agai from {objects}.",
                f"The listener excluded the target from their guess. Just repeat the previous feature — {feature} — and kindly ask them to try guessing again from {objects}."
                f"Hmm, the listener didn’t include the target. Just repeat your last feature — {feature} — and ask them to try guessing again.",
                f"The listener missed the target. Say {feature} again and gently ask them to take another guess.",
                f"It looks like the listener didn’t choose the target. Repeat the feature — {feature} — and invite them to guess again from this group: {objects}.",
                f"The listener’s guess was off. Please say {feature} again and ask them to try once more using this list: {objects}.",
            ]

        else:
            contents = [
                f"Based on your reasoning, the next feature to provide is: {feature}. Please express it naturally in a single sentence.",
                f"You’ve determined that the next helpful feature is: {feature}. Present it in a single, natural-sounding sentence.",
                f"Your next feature should be: {feature}. Say it naturally as part of the dialogue.",
                f"The most informative feature to say now is: {feature}. Express it clearly in one natural sentence.",
            ]

        content = self.random.choice(contents)
        observation = [Message(agent_name="User Prompt", content=content, turn=1)]

        response = await super().async_act(observation)

        return response


if __name__ == "__main__":
    # 导入必要的模块
    from chatarena.backends import OpenAIChat
    
    # 创建测试数据
    referent_set = ["red square", "blue ball", "blue square"]
    target_idx = 0  # 目标是 "red square"
    
    # 创建有效的后端
    backend = OpenAIChat(model="gpt-4o-mini")
    
    # 创建 speaker 实例
    speaker = RationalSpeaker(
        backend=backend,
        role_desc="You are a speaker in a dialogue game.",
        global_prompt="You are a speaker.",
        target_object="red square"
    )
    
    # 测试
    result = speaker.act(referent_set, False)
    print(f"Speaker response: {result}")
