from collections import Counter

def split_referent_object(referent_set):
    referent_list = [r.split() for r in referent_set]
    return referent_list

class SpeakerUtils:
    def __init__(self, referent_set, target_index):
        self.referent_list = split_referent_object(referent_set)
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
        referent_object = self.referent_list[index]
        if feature not in referent_object:
            return 0.0
        freq = self.get_freq()
        numerator = 1 / freq[feature]
        denominator = sum(1 / freq[f] for f in referent_object)
        likelihood = numerator / denominator
        return likelihood

    def feature_posterior_given_referent(self, feature, index)->float:
        """
        在referent_list中已知，并且想要指代某个referent_object，
        那么说出某个feature词的posterior概率 
        P(referent_object | feature, referent_list)
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
        print("[DEBUG] the first ranked feature: ", target_object[feature_rank_list.index(min(feature_rank_list))])
        print("[DEBUG] the present referent set: ", self.referent_list)
        return target_object[feature_rank_list.index(min(feature_rank_list))]

# 测试
# print(SpeakerUtils(["old flat porous", "old flat dense", "old three-dimensional porous", "old three-dimensional dense", "new flat dense", "new three-dimensional porous", "new three-dimensional dense"], 0).first_ranked_target_feature())

# referent_set = ["red circle small", "red circle large", "red square large"]
# target_index = 0
# print(SpeakerUtils(referent_set, target_index).first_ranked_target_feature())