import random
import json
import os
import glob
from mapping import MatrixMapping, load_feature_pairs
import argparse

parser = argparse.ArgumentParser(description='随机选择一个矩阵，并生成对话链条')
parser.add_argument('--feature_pairs_file', required=True, help='特征对文件路径')
parser.add_argument('--selected_matrixes_dir', required=True, help='已选择矩阵目录')
parser.add_argument('--output_dir', required=True, help='输出目录')
parser.add_argument('--repeat', type=int, default=10, help='重复次数')


args = parser.parse_args()

# 重新加载 feature_pairs
with open(args.feature_pairs_file, 'r') as file:
    feature_pairs = [line.strip() for line in file.readlines()]

# 设置全局 feature_pairs 供 mapping.py 使用
import mapping
mapping.feature_pairs = feature_pairs

# 从目录中读取矩阵文件列表
import glob
matrix_files = glob.glob(os.path.join(args.selected_matrixes_dir, "*.json"))
if not matrix_files:
    raise ValueError(f"在目录 {args.selected_matrixes_dir} 中没有找到JSON文件")

print(f"找到 {len(matrix_files)} 个矩阵文件")
# 全局变量
feature_pairs = []


def generate_referent_set(matrix_files):
    # 随机选择一个矩阵文件
    selected_file = random.choice(matrix_files)
    
    # 读取矩阵文件
    with open(selected_file, 'r') as file:
        matrixes_data = json.load(file)
    
    # 确认数据格式：JSON数组，每个元素是矩阵对象
    if not isinstance(matrixes_data, list):
        raise ValueError(f"期望JSON数组格式，但得到 {type(matrixes_data)}")
    
    # 随机选择一个矩阵对象
    selected_matrix_obj = random.choice(matrixes_data)
    
    # 提取矩阵数据
    matrix_data = selected_matrix_obj['matrix']
    
    # 调用mapping.py中的函数，生成referent set
    referent_set = MatrixMapping(matrix_data).mapping_to_referent_set()
    
    # 将特征列表转换为字符串格式
    referent_set_strings = []
    for referent in referent_set:
        # 将特征列表用空格连接成字符串
        referent_string = " ".join(referent)
        referent_set_strings.append(referent_string)
    
    # 返回包含referent_set和target_referent的字典
    result = {
        "referent_set": referent_set_strings,
        "target_referent": referent_set_strings[0]  # 第0位作为target_referent
    }
    
    return result

def save_referent_sets(all_referent_sets, output_dir):
    # 保存所有referent set到一个文件
    with open(os.path.join(output_dir, 'referent_sets.json'), 'w') as file:
        json.dump(all_referent_sets, file, indent=2, ensure_ascii=False)

def main():
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 收集所有对话链条
    all_referent_sets = []
    
    # 重复生成对话链条
    for i in range(args.repeat):
        print(f"\n=== 第 {i+1} 次生成 ===")
        
        # 生成对话链条
        referent_set = generate_referent_set(matrix_files)
        
        # 添加到列表中
        all_referent_sets.append(referent_set)
        
        print(f"Generated {i+1} referent sets")
    
    # 保存所有对话链条到一个文件
    save_referent_sets(all_referent_sets, args.output_dir)
    
    print(f"\nDone! Generated {args.repeat} referent sets, saved to {args.output_dir}/referent_sets.json")

if __name__ == "__main__":
    main()

