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
random_seed = 3
random.seed(random_seed)
np.random.seed(random_seed)
input_file_dir = '../extracted/AA/'
input_file_names = [r'std_zh_wiki_00', r'std_zh_wiki_01', r'std_zh_wiki_02'] #output of wiki_preprocess.py
input_file_dir = r'C:\\Code\\NeuralSpeech\\FastCorrect\\'
input_file_names = [r'std_sports.txt'] #output of wiki_preprocess.py

#noise_ratio = 0.15
noise_ratio = 1.1

sim_dict = {}
trie_dict = trie.Trie()
vocab_1char = []
vocab_2char = []

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
        if (vocab_length == 2) and (len(sim_vocab) > 1):
            vocab_2char.append(vocab)
        if len(sim_vocab) == 1:
            #print("skip ", line)
            continue
        if vocab_length >= 9:
            #print("skip ", line)
            continue
        sim_dict[first_char][vocab_length][vocab] = sim_vocab

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
        else:
            assert vocab_length == 1, "char length must be 1"
        if len(sim_vocab) == 1:
            #print("skip ", line)
            continue
        sim_dict[first_char][vocab_length][vocab] = sim_vocab

force_correction_rule_files = [r'./scripts/std_force_correction_rules.txt',
                               r'./scripts/hard_force_correction_rules.txt',
                               r'./dictionary/short_noised_English.txt']
#force_correction_rule_files = [r'C:\Code\NeuralSpeech\FastCorrect\scripts\std_test_rules.txt']
for rule_file_path in force_correction_rule_files:
    with open(rule_file_path, 'r', encoding='utf-8') as infile:
        for id, line in enumerate(infile.readlines()):
            line = line.strip()
            vocab, sim_vocab = line.split('\t')
            sentences = preprocess.normAndTokenize(vocab, 1)
            sim_sentences = preprocess.normAndTokenize(sim_vocab, 1)
            if len(sentences) == 0 or len(sim_sentences) == 0:
                print("skip empty src or tgt rule: " + line)
                continue
            tokens = []
            for sentence in sentences:
                for token in sentence.split():
                    tokens.append(token.lower())
            sim_tokens = []
            for sentence in sim_sentences:
                for token in sentence.split():
                    sim_tokens.append(token.lower())
            same_pairs = True
            if len(tokens) != len(sim_tokens):
                same_pairs = False
            else:
                for token, sim_token in zip(tokens, sim_tokens):
                    if token != sim_token:
                        same_pairs = False
                        break
            if same_pairs:
                print("skip same src tgt rule: " + line)
                continue
            trie_dict.insert(tokens, sim_tokens)

beam_size = 1

char_candidate_logit = [6, 5, 5, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 1]

SUB = 0
INS_L = 1
INS_R = 2
DEL = 3
all_op1 = [SUB, INS_L, INS_R, DEL]
prob_op1 = [4 / 5, 1 / 20, 1 / 20, 1 / 10]

all_op2 = [SUB, INS_L, INS_R, DEL]
prob_op2 = [4/5, 2/25, 2/25, 1/25]

all_op3 = [SUB, INS_L, INS_R]
prob_op3 = [2/3, 1/6, 1/6]

def add_char_noise(token, op, candidate, unuse=None):
    if op == SUB:
        if candidate is None:
            random_token = np.random.choice(vocab_1char)
            return [random_token]
        else:
            prob_candidate = [i / sum(char_candidate_logit[:len(candidate)]) for i in char_candidate_logit[:len(candidate)]]
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

def add_tokens_noise(token, op, candidate, unuse=None):
    if op == SUB:
        if candidate is None:
            random_token = np.random.choice(vocab_1char)
            return 1, [random_token]
        else:
            matched_info = np.random.choice(candidate)
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


import time
begin_time = time.time()
for input_file_name in input_file_names:
    input_file_path = input_file_dir + input_file_name
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        output_file_path = input_file_dir + "/noised" + str(random_seed) + "_" + input_file_name
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            final_lines = []
            for count, line in enumerate(infile.readlines()):
                if count % 5000 == 1:
                    print("{} finished in {}s".format(count-1, time.time()-begin_time))
                line = line.strip().lower() #不考虑英文大小写
                if not line:
                    continue
                new_tokens = []
                tokens = line.split()
                tokens_num = len(tokens)
                i = 0
                while i < tokens_num:
                    tok = tokens[i]
                    if random.random() < noise_ratio:
                        matched_info = trie_dict.get_pairs(tokens[i:])
                        if tok not in sim_dict.keys(): #对应英文单词（数字、特殊符号或汉字可以在相似字表里找到）
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
                            meta_new_tokens = noise_meta_beam(tok, meta_noise, None)
                            new_tokens.extend(meta_new_tokens)
                            i += 1
                            continue
                        if tokens_num - i >= 1:
                            if tokens[i] in sim_dict[tok][1].keys():
                                tok = tokens[i]
                                matched_tokens_num = sum([item.matched_tokens_num for item in matched_info])
                                token_noise_ratio = matched_tokens_num / (matched_tokens_num + 4) #匹配的字符串越长，纠错项越容易被选到
                                if token_noise_ratio > 0 and np.random.random() < token_noise_ratio:
                                #if matched_tokens_num > 0:
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
                                    matched_tokens_num, sim_tokens = add_tokens_noise(tok, meta_noise, (matched_info if random.random() < 0.99 else None))
                                    new_tokens.extend(sim_tokens)
                                    i += matched_tokens_num
                                    continue
                                i += 1
                                meta_noise = np.random.choice(all_op1, p=prob_op1)
                                #meta_noise = SUB
                                meta_new_tokens = noise_meta_beam(tok, meta_noise, (sim_dict[tok[0]][1][tok] if random.random() < 0.99 else None))
                                new_tokens.extend(meta_new_tokens)
                                continue
                            else:
                                pass
                        else:
                            raise ValueError("Impossible condition!")
                    else: #不加噪声
                        i += 1
                        new_tokens.append(tok)
                if len(new_tokens) > 0: # 一行处理完成
                    final_line = "\t".join([line] + [" ".join(new_tokens)]) + '\n'
                    final_lines.append(final_line)
                    if len(final_lines) > 10000:
                        outfile.writelines(final_lines)
                        final_lines = []
            if len(final_lines) > 0: #整个文件处理完成
                outfile.writelines(final_lines)
                final_lines = []

