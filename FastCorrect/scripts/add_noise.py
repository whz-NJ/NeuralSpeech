# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Usage python add_noise.py <input-raw-text-file> <output-noised-text-file> <random-seed>

import os
import sys
import random
import numpy as np
import trie
import preprocess

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

with open(r'C:\Code\NeuralSpeech\FastCorrect\scripts\sim_prun_word.txt', 'r', encoding='utf-8') as infile:
    for id, line in enumerate(infile.readlines()):
        line = line.strip()
        vocab, sim_vocab = line.split('\t')
        words = preprocess.normalize(vocab)
        sim_words = preprocess.normalize(sim_vocab)
        if len(words) != 1 or len(sim_words) != 1:
            print("skip: " + line)
            continue
        trie_dict.insert(preprocess.tokenize(words[0]), preprocess.tokenize(sim_words[0]))

noise_ratio = 0.15
#noise_ratio = 1.1
beam_size = 1

candidate_logit = [6, 5, 5, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 1]

# infile = sys.argv[1]
# outfile = sys.argv[2]
# random.seed(int(sys.argv[3]))
# np.random.seed(int(sys.argv[3]))
infile = r'C:\Code\NeuralSpeech\FastCorrect\label.txt'
outfile = r'C:\Code\NeuralSpeech\FastCorrect\noised_label_7.txt'
random.seed(7)
np.random.seed(7)

SUB = 0
INS_L = 1
INS_R = 2
DEL = 3
all_op = [SUB, INS_L, INS_R, DEL]
prob_op = [4/5, 1/20, 1/20, 1/10]

def add_char_noise(token, op, candidate, unuse=None):
    if op == SUB:
        if candidate is None:
            random_token = np.random.choice(vocab_1char)
            return random_token, None
        else:
            prob_candidate = [i/sum(candidate_logit[:len(candidate)]) for i in candidate_logit[:len(candidate)]]
            return np.random.choice(candidate, p=prob_candidate), None
    elif op == DEL:
        return "", None
    elif op == INS_L:
        random_token = np.random.choice(vocab_1char)
        return random_token + token, random_token
    elif op == INS_R:
        random_token = np.random.choice(vocab_1char)
        return token + random_token, random_token
    else:
        raise ValueError("impossible op {}!".format(op))

def add_tokens_noise(token, op, candidate, unuse=None):
    if op == SUB:
        if candidate is None:
            random_token = np.random.choice(vocab_1char)
            return 1, 1, random_token, None
        else:
            candidate_len = len(candidate)
            if candidate_len > len(candidate_logit):
                candidate_len = len(candidate_logit)
            prob_candidate = [i/sum(candidate_logit[:candidate_len]) for i in candidate_logit[:candidate_len]]
            matched_info = np.random.choice(candidate, p=prob_candidate)
            return matched_info.matched_tokens_num, matched_info.matched_chars_num, matched_info.sim_words, None

    elif op == DEL:
        return 1, 1, "", None
    elif op == INS_L:
        random_token = np.random.choice(vocab_1char)
        return 1, 1, random_token + token, random_token
    elif op == INS_R:
        random_token = np.random.choice(vocab_1char)
        return 1, 1, token + random_token, random_token
    else:
        raise ValueError("impossible op {}!".format(op))
def noise_meta_beam(token, meta_noise, candidate):
    return add_char_noise(token, meta_noise, candidate, None)


import time
begin_time = time.time()

with open(infile, 'r', encoding='utf-8') as infile:
    with open(outfile, 'w', encoding='utf-8') as outfile:
        for count, line in enumerate(infile.readlines()):
            if count % 5000 == 1:
                print("{} finished in {}s".format(count-1, time.time()-begin_time))
            line = line.strip()
            if not line:
                continue
            new_lines = ["" for _ in range(beam_size)]
            tokens = preprocess.tokenize(line)
            tokens_num = len(tokens)
            i = 0
            while i < tokens_num:
                tok = tokens[i]
                if tok == " ":
                    i += 1
                    for j in range(beam_size):
                        new_lines[j] += tok
                    continue

                if random.random() < noise_ratio:
                    matched_info = trie_dict.get_pairs(tokens[i:])
                    if len(matched_info) > 0:
                        meta_noise = np.random.choice(all_op, p=prob_op)
                        #meta_noise = SUB
                        matched_tokens_num, matched_chars_num, sim_word, meta_ins = add_tokens_noise(tok, meta_noise, matched_info)
                        new_lines[modify_beam] += ''.join(sim_word)
                        i += matched_chars_num
                        continue
                    if tok not in sim_dict.keys():
                        modify_beam = 0
                        meta_noise = np.random.choice(all_op, p=prob_op)
                        meta_new_token, meta_ins = noise_meta_beam(tok, meta_noise, None)
                        new_lines[modify_beam] += meta_new_token
                        continue
                    if tokens_num - i >= 1:
                        if tokens[i] in sim_dict[tok][1].keys():
                            tok = tokens[i]
                            i += 1
                            modify_beam = 0
                            meta_noise = np.random.choice(all_op, p=prob_op)
                            meta_new_token, meta_ins = noise_meta_beam(tok, meta_noise, (sim_dict[tok[0]][1][tok] if random.random() < 0.99 else None))
                            new_lines[modify_beam] += meta_new_token
                            continue
                        else:
                            pass
                    else:
                        raise ValueError("Impossible condition!")
                else:
                    i += 1
                    for j in range(beam_size):
                        new_lines[j] += tok

            need_skip = False
            for iter_line in new_lines:
                if not iter_line.strip():
                    need_skip = True
                    break
            if need_skip:
                continue

            final_line = "\t".join([line] + new_lines)
            outfile.write(final_line + '\n')


