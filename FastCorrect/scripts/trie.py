from collections import defaultdict
import cal_wer_dur_v1

class TrieNode():
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.word = ''
        self.pairs = []

class MatchInfo:
    def __init__(self, matched_tokens_num, matched_chars_num, werdur, sim_words):
        self.matched_tokens_num = matched_tokens_num
        self.matched_chars_num = matched_chars_num
        self.werdur =  werdur
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
        if len(words) == 1 and len(pair) == 1:
            if words[0] == pair[0]:
                werdur = [1]
            else:
                werdur = [-1]
        else:
            werdur, _ = cal_wer_dur_v1.calculate_wer_dur_v1(pair, words, return_path_only=False)
        node.pairs.append([[int(m) for m in werdur], pair])

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
                    pairs.append(MatchInfo(matched_tokens_num, matched_chars_num, pair[0], pair[1]))
        return pairs

def main():
    trie = Trie()
    trie.insert(['你', '好'], ['累', '好'])
    # trie.insert(['hello', 'world'],['哈','咯','我','的'])
    trie.insert(['hello'], ['哈', '咯'])
    trie.insert(['hello'], ['哈', '啰'])
    # words1 = trie.get_pairs(['hello' , 'world', '啊'])
    words2 = trie.get_pairs(['hello'])
    words3 =trie.get_pairs(['你', '好', '啊'])
    # print(words1)
    print(words2)
    print(words3)

if __name__ == "__main__":
    main()
