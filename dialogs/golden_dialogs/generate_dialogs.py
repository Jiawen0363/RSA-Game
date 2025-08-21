from rational_agents import RationalSpeaker, RationalListener
import json

# 这个文件用于生成golden dialogs的链条，并且将链条保存到文件中


class GoldenDialogsGenerator:
    def __init__(self, referent_list, target_index):
        self.referent_list = referent_list
        self.target_index = target_index
        self.dialogue_chain = []
        
    def generate_dialogue(self):
        current_referent_set = self.referent_list.copy()
        dialogue_chain = []
        max_rounds = 10
        round_count = 0

        while round_count < max_rounds:
            round_count += 1
            speaker = RationalSpeaker(current_referent_set, self.target_index)
            best_feature = speaker.first_ranked_target_feature()
            listener = RationalListener(current_referent_set, best_feature)
            possible_referents = listener.give_referent_set(current_referent_set)
            dialogue_chain.append({
                "speaker": best_feature,
                "listener": possible_referents
            })
            
            # 检查possible_referents中是否包含target_referent
            target_referent = self.referent_list[self.target_index]
            if target_referent not in possible_referents:
                print(f"Warning: Target referent {target_referent} not in possible referents {possible_referents}")
                break
            
            if len(possible_referents) == 1:
                break
            current_referent_set = possible_referents

        # 转换为字符串格式的对话
        dialogue_strings = []
        for round_data in dialogue_chain:
            dialogue_strings.append(f"Speaker: {round_data['speaker']}")
            listener_str = ", ".join([f"('{', '.join(ref)}')" for ref in round_data['listener']])
            dialogue_strings.append(f"Listener: {listener_str}")

        return {
            "referent_set": [" ".join(ref) for ref in self.referent_list],
            "target_referent": " ".join(self.referent_list[self.target_index]),
            "dialogue": dialogue_strings,
            "rounds": len(dialogue_chain)
        }    
    

    
    def get_target_object(self):
        return self.referent_list[self.target_index]
    
    @staticmethod
    def load_referent_sets_from_json(json_file_path):
        """
        从JSON文件加载referent sets并转换为referent_list格式
        参数:
        - json_file_path: str, JSON文件路径
        返回:
        - dict, 包含所有referent sets的字典，格式为 {set_name: referent_list}
        """
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        referent_sets = {}
        
        for set_name, referent_strings in data.items():
            # 将字符串格式转换为列表格式
            referent_list = []
            for referent_str in referent_strings:
                # 按空格分割字符串，得到特征列表
                features = referent_str.split()
                referent_list.append(features)
            
            referent_sets[set_name] = referent_list
        
        return referent_sets
    
    @staticmethod
    def process_all_referent_sets(json_file_path, target_index=0, output_filename="dialogue.json"):
        """
        处理JSON文件中的所有referent sets，生成一个合并的对话文件
        
        参数:
        - json_file_path: str, JSON文件路径
        - target_index: int, 目标referent的索引（默认为0）
        - output_filename: str, 输出文件名
        
        返回:
        - dict, 包含所有对话的字典
        """
        # 加载所有referent sets
        referent_sets = GoldenDialogsGenerator.load_referent_sets_from_json(json_file_path)
        
        all_dialogues = {}
        
        for set_name, referent_list in referent_sets.items():
            print(f"\n=== Processing {set_name} ===")
            print(f"Referent Set: {referent_list}")
            
            # 创建生成器并生成对话
            generator = GoldenDialogsGenerator(referent_list, target_index)
            dialogue_chain = generator.generate_dialogue()
            
            # 打印轮数
            print(f"对话轮数: {dialogue_chain['rounds']} 轮")
            
            all_dialogues[set_name] = dialogue_chain

   
        # 保存合并的对话文件
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_dialogues, f, indent=2, ensure_ascii=False)
        
        print(f"\nsuccessfully saved dialogues to {output_filename}")
    




        return all_dialogues


# 测试代码
if __name__ == "__main__":
    print("=== 处理所有referent sets ===")
        # 处理所有referent sets
    basepath = "/Users/duanjiawen/Desktop/RSA_Game/golden_dialogue"
    input_file_path = "/Users/duanjiawen/Desktop/RSA_Game/golden_dialogue/min_referent_set_gold.json" #TODO 修改输入文件的路径
    dialogues = GoldenDialogsGenerator.process_all_referent_sets(
        input_file_path, 
        target_index=0, 
        output_filename=basepath + "/dialogue.json" # TODO 修改输出文件的路径
    )
    print(dialogues)
    print(f"successfully generated {len(dialogues)} dialogues")
    