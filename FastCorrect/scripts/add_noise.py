# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Usage python add_noise.py <input-raw-text-file> <output-noised-text-file> <random-seed>

import os
import sys
import random
import numpy as np
import trie
import preprocess

#random_seed = int(sys.argv[1])
random_seed = 5
random.seed(random_seed)
np.random.seed(random_seed)
#input_file_dir = '/root/extracted/AA/'
input_file_dir = '/root/std_wiki'
input_file_names = [r'std_zh_wiki_00', r'std_zh_wiki_01', r'std_zh_wiki_02'] #output of wiki_preprocess.py
dict_file_path = "../dictionary/short.dict.CN_char.txt"
noise_ratio = 0.15


sim_dict = {}
trie_dict = trie.Trie()
vocab_1char = []
#vocab_2char = []

token_count_dict = {}
with open(dict_file_path, 'r', encoding='utf-8') as infile:
    for line in infile.readlines():
        fields = line.split()
        if len(fields) != 2:
            continue
        word = fields[0]
        count = fields[1]
        token_count_dict[word] = count

#with open('./scripts/sim_prun_char.txt', 'r', encoding='utf-8') as infile:
with open(r'C:\Code\NeuralSpeech\FastCorrect\scripts\sim_prun_char.txt', 'r', encoding='utf-8') as infile:
    for line in infile.readlines():
        line = line.strip()
        first_char = line[0]
        if first_char not in sim_dict.keys():
            sim_dict[first_char] = {1: {}, 2: {}, 3: {}, 4: {}, 5:{}, 6:{}, 7: {}, 8: {}}
        vocab, sim_vocab = line.split('\t')
        sim_vocab = sim_vocab.split()

        vocab_length = len(vocab)
        if (vocab_length == 1) and (len(sim_vocab) > 1):
            vocab_1char.append(vocab)
        # if (vocab_length == 2) and (len(sim_vocab) > 1):
        #     vocab_2char.append(vocab)
        if len(sim_vocab) == 1:
            #print("skip ", line)
            continue
        for ch in sim_vocab:
            trie_dict.insert([vocab], [ch])
        # if vocab_length >= 9:
        #     #print("skip ", line)
        #     continue
        #sim_dict[first_char][vocab_length][vocab] = sim_vocab

#with open('./scripts/chinese_char_sim.txt', 'r', encoding='utf-8') as infile:
with open(r'C:\Code\NeuralSpeech\FastCorrect\scripts\chinese_char_sim.txt', 'r', encoding='utf-8') as infile:
    for id, line in enumerate(infile.readlines()):
        line = line.strip()
        first_char = line[0]
        if first_char not in sim_dict.keys():
            sim_dict[first_char] = {1: {}, 2: {}, 3: {}, 4: {}, 5:{}, 6:{}, 7: {}, 8: {}}
        vocab, sim_vocab = line.split('\t')
        sim_vocab = sim_vocab.split()

        vocab_length = len(vocab)
        if (vocab_length == 1) and (vocab not in vocab_1char) and (id < 3000) and (len(sim_vocab) > 1):
            vocab_1char.append(vocab)
        # else:
        #     assert vocab_length == 1, "char length must be 1"
        if len(sim_vocab) == 1:
            #print("skip ", line)
            continue
        #sim_dict[first_char][vocab_length][vocab] = sim_vocab
        matched_info_list = trie_dict.get_pairs([vocab])
        for ch in sim_vocab:
            find = False
            for matched_info in matched_info_list:
                if ch == matched_info.sim_words[0]:
                    find = True
                    break
            if not find:
                trie_dict.insert([vocab], [ch])

force_correction_rule_files = [r'./std_force_correction_rules.txt',
                               r'./hard_force_correction_rules.txt',
                               r'../dictionary/short_noised_English.txt']
# force_correction_rule_files = [r'./scripts/std_force_correction_rules.txt',
#                                r'./scripts/hard_force_correction_rules.txt',
#                                r'../dictionary/short_noised_English.txt']
#force_correction_rule_files = [r'C:\Code\NeuralSpeech\FastCorrect\scripts\std_test_rules.txt']
for rule_file_path in force_correction_rule_files:
    with open(rule_file_path, 'r', encoding='utf-8') as infile:
        for id, line in enumerate(infile.readlines()):
            line = line.strip()
            vocab, sim_vocab = line.split('\t')
            sentences = preprocess.normAndTokenize(vocab, 1)
            sim_sentences = preprocess.normAndTokenize(sim_vocab, 1)
            if len(sentences) == 0 or len(sim_sentences) == 0:
                # print("skip empty src or tgt rule: " + line)
                continue
            tokens = []
            for token in sentences[0].split():
                tokens.append(token)
            sim_tokens = []
            for token in sim_sentences[0].split():
                sim_tokens.append(token)
            same_pairs = True
            if len(tokens) != len(sim_tokens):
                same_pairs = False
            else:
                for token, sim_token in zip(tokens, sim_tokens):
                    if token != sim_token:
                        same_pairs = False
                        break
            if same_pairs:
                #print("skip same src tgt rule: " + line)
                continue
            if len(tokens) > 1 or len(sim_tokens) > 1:
                trie_dict.insert(tokens, sim_tokens)
            else:
                matched_info_list = trie_dict.get_pairs(tokens)
                find = False
                for matched_info in matched_info_list:
                    if tokens[0] == matched_info.sim_words[0]:
                        find = True
                        break
                if not find:
                    trie_dict.insert(tokens, sim_tokens)

beam_size = 1

char_pos_logit = [6, 5, 5, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 1]

SUB = 0
INS_L = 1
INS_R = 2
DEL = 3
all_op1 = [SUB, INS_L, INS_R, DEL]
prob_op1 = [4 / 5, 1 / 20, 1 / 20, 1 / 10] #只有一个token匹配，DEL概率比较大

all_op2 = [SUB, INS_L, INS_R, DEL] #有两个连续token都匹配，DEL操作概率很小
prob_op2 = [4/5, 2/25, 2/25, 1/25]

all_op3 = [SUB, INS_L, INS_R] #有三个连续token都匹配，就不认为应该删除
prob_op3 = [2/3, 1/6, 1/6]

def add_char_noise(token, op, candidate, unuse=None):
    if op == SUB:
        if candidate is None:
            random_token = np.random.choice(vocab_1char)
            return [random_token]
        else:
            prob_candidate = [i / sum(char_pos_logit[:len(candidate)]) for i in char_pos_logit[:len(candidate)]]
            return [np.random.choice(candidate, p=prob_candidate)]
    elif op == DEL:
        return []
    elif op == INS_L:
        random_token = np.random.choice(vocab_1char)
        return [random_token, token]
    elif op == INS_R:
        random_token = np.random.choice(vocab_1char)
        return [token, random_token]
    else:
        raise ValueError("impossible op {}!".format(op))

def add_tokens_noise(token, op, candidates):
    if op == SUB:
        if candidates is None:
            random_token = np.random.choice(vocab_1char)
            return 1, [random_token]
        else:
            matched_tokens_sum = 0
            logit_idx = 0
            prob_candidate = []
            priority_sum = 0
            max_char_pos_logit = char_pos_logit[0]
            # 考虑纠错词长度，如果相同，并且纠错词长度为1，则考虑位置（位置靠前优先考虑），
            # 如果长度相同，并且都大于1，则各个词机会均等
            # 如果长度不同，优先考虑长度长的纠错词
            for c in candidates:
                if c.matched_tokens_num == 1 and len(c.sim_words) == 1:
                    priority = c.matched_tokens_num * max_char_pos_logit + char_pos_logit[logit_idx]
                    priority_sum += priority
                    prob_candidate.append(priority)
                    if logit_idx < len(char_pos_logit) - 1:
                        logit_idx += 1
                else:
                    priority = (c.matched_tokens_num+1)*max_char_pos_logit
                    priority_sum += priority
                    prob_candidate.append(priority)
            prob_candidate = [p/priority_sum for p in prob_candidate]
            matched_info = np.random.choice(candidates, p = prob_candidate)
            return matched_info.matched_tokens_num, matched_info.sim_words
    elif op == DEL:
        return 1, []
    elif op == INS_L:
        random_token = np.random.choice(vocab_1char)
        return 1, [random_token, token]
    elif op == INS_R:
        random_token = np.random.choice(vocab_1char)
        return 1, [token, random_token]
    else:
        raise ValueError("impossible op {}!".format(op))

def noise_meta_beam(token, meta_noise, candidate):
    return add_char_noise(token, meta_noise, candidate, None)


def noise_sentence(sentence):
    new_tokens = []
    tokens = sentence.split()
    tokens_num = len(tokens)
    if tokens_num == 0:
        return new_tokens
    i = 0
    while i < tokens_num:
        tok = tokens[i]
        if not token_count_dict.__contains__(tok):
            i += 1
            continue  # 跳过不在词表中的token
        if random.random() < noise_ratio:
            matched_info = trie_dict.get_pairs(tokens[i:])
            if len(matched_info) > 0:
                if matched_info[-1].matched_tokens_num > 2:
                    all_op = all_op3
                    prob_op = prob_op3
                elif matched_info[-1].matched_tokens_num == 2:
                    all_op = all_op2
                    prob_op = prob_op2
                else:
                    all_op = all_op1
                    prob_op = prob_op1
                meta_noise = np.random.choice(all_op, p=prob_op)
                # meta_noise = SUB
                matched_tokens_num, sim_tokens = add_tokens_noise(tok, meta_noise, matched_info)
                new_tokens.extend(sim_tokens)
                i += matched_tokens_num
                continue
        else:  # 不加噪声
            i += 1
            new_tokens.append(tok)
    return new_tokens

# tokens = noise_sentence(preprocess.normAndTokenize("欢迎来到咪咕体育", 3, True)[0])
# print(noise_sentence(preprocess.normAndTokenize("欢迎参加miguday", 3, True)[0]))

import time
begin_time = time.time()
for input_file_name in input_file_names:
    input_file_path = os.path.join(input_file_dir, input_file_name)
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        output_file_path = input_file_dir + "/noised" + str(random_seed) + "_" + input_file_name
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            final_lines = []
            for count, line in enumerate(infile.readlines()):
                if count % 5000 == 1:
                    print("{} finished in {}s".format(count-1, time.time()-begin_time))
                line = line.strip()
                if not line:
                    continue
                sentences = preprocess.normAndTokenize(line, 2, True)
                for sentence in sentences:
                    new_tokens = noise_sentence(sentence)
                    if len(new_tokens) > 0: # 一句处理完成（一行有多句）
                        final_line = "\t".join([sentence] + [" ".join(new_tokens)]) + '\n'
                        final_lines.append(final_line)
                        if len(final_lines) > 10000:
                            outfile.writelines(final_lines)
                            final_lines = []
            if len(final_lines) > 0: #整个文件处理完成
                outfile.writelines(final_lines)
                final_lines = []

