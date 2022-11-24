from collections import defaultdict

class TrieNode():
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.word = ''
        self.pairs = []

class MatchInfo:
    def __init__(self, matched_tokens_num, matched_chars_num, sim_words):
        self.matched_tokens_num = matched_tokens_num
        self.matched_chars_num = matched_chars_num
        self.sim_words = sim_words

class Trie():
    '''
    实现如下功能：
    4. 迭代器返回插入trie的所有单词：get_all_words
    '''

    def __init__(self):
        self.root = TrieNode()
        self.total_count = 0


    def insert(self, words, pair):
        node = self.root
        for word in words:
            node = node.children[word]
            node.word = word
        node.pairs.append(pair)

    def delete(self, words):
        def delete_inner(root, words):
            if words and len(words) >= 1:
                parent = root
                node = parent.children[words[0]]
                if node and len(node.word) > 0: #node是有效节点（node匹配words[0])
                    if len(words) > 1:
                        if delete_inner(node, words[1:]): #node的子节点被删除
                            if not node.pairs or len(node.pairs) == 0: #待删除的node节点不是叶子节点
                                parent.children.pop(words[0])
                                return True
                            #待删除的node是叶子节点，同时还是当前待删除words的一部分
                            return False
                        else: #parent节点的子节点未被删除（但可能是匹配的）
                            return False
                    else: #匹配到最后一个字了
                        child = node.children
                        if not child or len(child) == 0: #匹配的node节点没有后代
                            parent.children.pop(words[0]) #不管node节点是否是叶子节点都要删除了
                            return True
                        else: #node节点有后代
                            node.pairs = [] #node节点不再是叶子节点了
                            return False
                else: #node节点不匹配 words[0]
                    return False
            else:
                return False
        delete_inner(self.root, words)

    def keys(self):
        def keys_inner(root):
            parent = root
            sub_keys = []
            if parent.pairs and len(parent.pairs) > 0:  # parent节点是叶子节点
                sub_keys.append(parent.word)
            if parent.children and len(parent.children) > 0: #parent节点有后代
                for child in parent.children:
                    inner_keys = keys_inner(parent.children[child])
                    for inner_key in inner_keys:
                        sub_keys.append(parent.word + inner_key)
            return sub_keys
        return keys_inner(self.root)

    # 返回所有相似词组
    def get_pairs(self, words):
        pairs = []
        node = self.root
        matched_tokens_num = 0
        matched_chars_num = 0
        for word in words:
            if word not in node.children:
                return pairs
            matched_tokens_num = matched_tokens_num + 1
            matched_chars_num += len(word)
            node = node.children[word]
            if len(node.pairs) > 0:
                for pair in node.pairs: #遍历读音类似词组
                    pairs.append(MatchInfo(matched_tokens_num, matched_chars_num, pair))
        return pairs

def main():
    trie = Trie()
    trie.insert(['你', '好'], ['累', '好'])
    trie.insert(['你', '好', '吗'], ['累', '好', '咩'])
    trie.insert(['你', '好', '吗', '啊'], ['累', '好', '咩', '呃'])
    trie.insert(['你', '好', '么'], ['累', '好', '麽'])
    # trie.insert(['hello', 'world'],['哈','咯','我','的'])
    # trie.insert(['hello'], ['哈', '咯'])
    trie.insert(['hello'], ['哈', '啰'])
    # trie.delete(['你', '好'])
    trie.delete(['你', '好', '吗'])
    print(trie.keys())
    #words1 = trie.get_pairs(['hello' , 'world', '啊'])
    words2 = trie.get_pairs(['hello'])
    words3 =trie.get_pairs(['你', '好', '啊'])
    words4 = trie.get_pairs(['你', '好', '吗', '啊'])
    #print(words1)
    print(words2)
    print(words3)
    print(words4)

if __name__ == "__main__":
    main()
