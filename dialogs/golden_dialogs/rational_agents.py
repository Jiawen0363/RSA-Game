from collections import Counter
from typing import Any



target_index = 0


class RationalSpeaker:
    def __init__(self, referent_list, target_index):
        self.referent_list = referent_list
        self.target_index = target_index

    def get_freq(self):
        all_features = [f for r in self.referent_list for f in r]
        freq = Counter(all_features)
        return freq
    
    def feature_likelihood_given_referent(self, feature, index)->float:
        """
        在题目是referent_list的情况下，speaker为了指代referent_object
        说出某个特征的likelihood的概率
        P(feature | referent_object, referent_list)
        """
        # 1. 如果这个referent object不包含feature，则likelihood为0
        referent_object = self.referent_list[index]
        if feature not in referent_object:
            return 0.0
        # 2. 统计所有词在 referent set 中的出现频率
        freq = self.get_freq()
        # 3. 分子: 1 / freq(feature)
        numerator = 1 / freq[feature]
        # 4. 分母: sum over 1 / freq(f_i) for f_i in target's features
        denominator = sum(1 / freq[f] for f in referent_object)
        # likelihood
        likelihood = numerator / denominator
        return likelihood

    def feature_posterior_given_referent(self, feature, index)->float:
        """
        在referent_list中已知，并且想要指代某个referent_object，那么说出某个feature词的posterior概率 P(referent_object | feature, referent_list)
        """
        likelihood1 = self.feature_likelihood_given_referent(feature, index)
        # 计算所有referent的likelihood
        all_likelihood = [self.feature_likelihood_given_referent(feature, j) for j in range(len(self.referent_list))]
        # # 计算所有referent的posterior只和,注意，这里要乘以object的数量的倒数！
        prior = 1 / len(self.referent_list)
        evidence = sum(all_likelihood)*prior
        posterior = likelihood1 * prior / evidence
        return posterior

    def posterior_list_given_feature(self, feature):
        posterior_list = []
        for i in range(len(self.referent_list)):
            # 为每个referent计算posterior
            posterior = self.feature_posterior_given_referent(feature, i)
            posterior_list.append(posterior)
        return posterior_list
    
    # def ranked_object_list(self, feature):
    #     # TODO 这里需要修改一下，因为需要处理posterior值相同的时候，如何排序
    #     posterior_list = self.posterior_list_given_feature(feature)
    #     # 获取所有referent的索引
    #     indices = list(range(len(self.referent_list)))
    #     # 按posterior_list排序索引
    #     sorted_indices = sorted(indices, key=lambda i: posterior_list[i], reverse=True)
    #     # 用排序后的索引获取对象
    #     ranked_object_list = [self.referent_list[i] for i in sorted_indices]
    #     return ranked_object_list
    
    def target_object_rank_given_feature(self, feature):
        posterior_list = self.posterior_list_given_feature(feature)
        target_posterior = self.feature_posterior_given_referent(feature, self.target_index)
        # 降序排序所有唯一posterior
        sorted_unique = sorted(set(posterior_list), reverse=True)
        # 找到target_posterior的排名（从1开始）
        rank = sorted_unique.index(target_posterior) + 1
        # 统计有多少个和target_posterior一样的
        same_count = posterior_list.count(target_posterior)
        if same_count > 1:
            # 返回如2.2、2.3等格式
            return float(f"{rank}.{same_count}")
        else:
            return float(rank)
    
    def first_ranked_target_feature(self):
        # 对于target object，遍历它所有的feature，并且分别调用target_object_rank_given_feature函数
        # 然后把所有的rank依次放到一个list里
        # 然后返回rank值最小的feature词语，而不是rank值
        target_object = self.referent_list[self.target_index]
        feature_rank_list = []
        for feature in target_object:
            rank = self.target_object_rank_given_feature(feature)
            feature_rank_list.append(rank)
        # print(feature_rank_list)
        return target_object[feature_rank_list.index(min(feature_rank_list))]



# print(RationalSpeaker(referent_list, target_index).first_ranked_target_feature())


class RationalListener:
    def __init__(self, referent_list, heard_feature):
        self.referent_list = referent_list
        self.heard_feature = heard_feature

    def give_referent_set(self, referent_list=None):
        """
        听到一个feature之后，遍历referent_list, 并在遍历过程中调用speaker的first_ranked_target_feature函数。
        如果speaker的first_ranked_target_feature函数返回的feature与heard_feature相同，则将这个object添加到possible_referents列表中。
        最后返回possible_referents。
        """
        if referent_list is None:
            referent_list = self.referent_list
            
        possible_referents = []
        for referent in referent_list:
            if RationalSpeaker(referent_list, referent_list.index(referent)).first_ranked_target_feature() == self.heard_feature:
                possible_referents.append(referent)
        return possible_referents

# 测试代码
# print(RationalListener(referent_list, "small").give_referent_set())
