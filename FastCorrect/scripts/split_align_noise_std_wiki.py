# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Usage python add_noise.py <input-raw-text-file> <output-noised-text-file> <random-seed>

import os
import sys
import random
import numpy as np
import trie
import preprocess
import codecs
import cal_wer_dur_v1
import signal


split_rate = [0.9, 0.05, 0.05]
#random_seed = int(sys.argv[1])
random_seed = 3
random.seed(random_seed)
np.random.seed(random_seed)
# input_file_dir = '/root/extracted/AA/'
input_file_dir = '/root/std_wiki'
# input_file_names = [r'std_zh_wiki_00', r'std_zh_wiki_01', r'std_zh_wiki_02'] #output of wiki_preprocess.py
input_file_names = ['std_zh_wiki_00_sp000', 'std_zh_wiki_00_sp001', 'std_zh_wiki_00_sp002', 'std_zh_wiki_00_sp003', 'std_zh_wiki_00_sp004', 'std_zh_wiki_00_sp005', 'std_zh_wiki_00_sp006', 'std_zh_wiki_00_sp007', 'std_zh_wiki_00_sp008', 'std_zh_wiki_00_sp009', 'std_zh_wiki_00_sp010', 'std_zh_wiki_00_sp011', 'std_zh_wiki_00_sp012', 'std_zh_wiki_00_sp013', 'std_zh_wiki_00_sp014', 'std_zh_wiki_00_sp015', 'std_zh_wiki_00_sp016', 'std_zh_wiki_00_sp017', 'std_zh_wiki_00_sp018', 'std_zh_wiki_00_sp019', 'std_zh_wiki_00_sp020', 'std_zh_wiki_00_sp021', 'std_zh_wiki_00_sp022', 'std_zh_wiki_00_sp023', 'std_zh_wiki_00_sp024', 'std_zh_wiki_00_sp025', 'std_zh_wiki_00_sp026', 'std_zh_wiki_00_sp027', 'std_zh_wiki_00_sp028', 'std_zh_wiki_00_sp029', 'std_zh_wiki_00_sp030', 'std_zh_wiki_00_sp031', 'std_zh_wiki_00_sp032', 'std_zh_wiki_00_sp033', 'std_zh_wiki_00_sp034', 'std_zh_wiki_00_sp035', 'std_zh_wiki_00_sp036', 'std_zh_wiki_00_sp037', 'std_zh_wiki_00_sp038', 'std_zh_wiki_00_sp039', 'std_zh_wiki_00_sp040', 'std_zh_wiki_00_sp041', 'std_zh_wiki_00_sp042', 'std_zh_wiki_00_sp043', 'std_zh_wiki_00_sp044', 'std_zh_wiki_00_sp045', 'std_zh_wiki_00_sp046', 'std_zh_wiki_00_sp047', 'std_zh_wiki_00_sp048', 'std_zh_wiki_00_sp049', 'std_zh_wiki_00_sp050', 'std_zh_wiki_00_sp051', 'std_zh_wiki_00_sp052', 'std_zh_wiki_00_sp053', 'std_zh_wiki_00_sp054', 'std_zh_wiki_00_sp055', 'std_zh_wiki_00_sp056', 'std_zh_wiki_00_sp057', 'std_zh_wiki_00_sp058', 'std_zh_wiki_00_sp059', 'std_zh_wiki_00_sp060', 'std_zh_wiki_00_sp061', 'std_zh_wiki_00_sp062', 'std_zh_wiki_00_sp063', 'std_zh_wiki_00_sp064', 'std_zh_wiki_01_sp000', 'std_zh_wiki_01_sp001', 'std_zh_wiki_01_sp002', 'std_zh_wiki_01_sp003', 'std_zh_wiki_01_sp004', 'std_zh_wiki_01_sp005', 'std_zh_wiki_01_sp006', 'std_zh_wiki_01_sp007', 'std_zh_wiki_01_sp008', 'std_zh_wiki_01_sp009', 'std_zh_wiki_01_sp010', 'std_zh_wiki_01_sp011', 'std_zh_wiki_01_sp012', 'std_zh_wiki_01_sp013', 'std_zh_wiki_01_sp014', 'std_zh_wiki_01_sp015', 'std_zh_wiki_01_sp016', 'std_zh_wiki_01_sp017', 'std_zh_wiki_01_sp018', 'std_zh_wiki_01_sp019', 'std_zh_wiki_01_sp020', 'std_zh_wiki_01_sp021', 'std_zh_wiki_01_sp022', 'std_zh_wiki_01_sp023', 'std_zh_wiki_01_sp024', 'std_zh_wiki_01_sp025', 'std_zh_wiki_01_sp026', 'std_zh_wiki_01_sp027', 'std_zh_wiki_01_sp028', 'std_zh_wiki_01_sp029', 'std_zh_wiki_01_sp030', 'std_zh_wiki_01_sp031', 'std_zh_wiki_01_sp032', 'std_zh_wiki_01_sp033', 'std_zh_wiki_01_sp034', 'std_zh_wiki_01_sp035', 'std_zh_wiki_01_sp036', 'std_zh_wiki_01_sp037', 'std_zh_wiki_01_sp038', 'std_zh_wiki_01_sp039', 'std_zh_wiki_01_sp040', 'std_zh_wiki_01_sp041', 'std_zh_wiki_01_sp042', 'std_zh_wiki_01_sp043', 'std_zh_wiki_01_sp044', 'std_zh_wiki_01_sp045', 'std_zh_wiki_01_sp046', 'std_zh_wiki_01_sp047', 'std_zh_wiki_01_sp048', 'std_zh_wiki_01_sp049', 'std_zh_wiki_01_sp050', 'std_zh_wiki_01_sp051', 'std_zh_wiki_01_sp052', 'std_zh_wiki_01_sp053', 'std_zh_wiki_01_sp054', 'std_zh_wiki_01_sp055', 'std_zh_wiki_01_sp056', 'std_zh_wiki_01_sp057', 'std_zh_wiki_01_sp058', 'std_zh_wiki_01_sp059', 'std_zh_wiki_01_sp060', 'std_zh_wiki_01_sp061', 'std_zh_wiki_02_sp000', 'std_zh_wiki_02_sp001', 'std_zh_wiki_02_sp002', 'std_zh_wiki_02_sp003', 'std_zh_wiki_02_sp004', 'std_zh_wiki_02_sp005', 'std_zh_wiki_02_sp006', 'std_zh_wiki_02_sp007', 'std_zh_wiki_02_sp008', 'std_zh_wiki_02_sp009', 'std_zh_wiki_02_sp010', 'std_zh_wiki_02_sp011', 'std_zh_wiki_02_sp012', 'std_zh_wiki_02_sp013', 'std_zh_wiki_02_sp014', 'std_zh_wiki_02_sp015', 'std_zh_wiki_02_sp016', 'std_zh_wiki_02_sp017', 'std_zh_wiki_02_sp018', 'std_zh_wiki_02_sp019', 'std_zh_wiki_02_sp020', 'std_zh_wiki_02_sp021', 'std_zh_wiki_02_sp022', 'std_zh_wiki_02_sp023', 'std_zh_wiki_02_sp024', 'std_zh_wiki_02_sp025', 'std_zh_wiki_02_sp026', 'std_zh_wiki_02_sp027', 'std_zh_wiki_02_sp028', 'std_zh_wiki_02_sp029', 'std_zh_wiki_02_sp030']
# input_file_dir = r'C:\Code\NeuralSpeech\FastCorrect'
# input_file_names= [r'std_wiki_cn.txt']

dict_file_path = "../dictionary/short.dict.CN_char.txt"
noise_ratio = 0.15
MAX_CORPUS_NUM = 200000 #一个文件最多保存的语料行数

TRAIN = 0
VALID = 1
TEST = 2
set_ops = [TRAIN, VALID, TEST]

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

with open(r'./sim_prun_char.txt', 'r', encoding='utf-8') as infile:
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
        for chs in sim_vocab:
            trie_dict.insert([vocab], [ch for ch in chs])

with open(r'./chinese_char_sim.txt', 'r', encoding='utf-8') as infile:
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
#force_correction_rule_files = []
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

def add_tokens_noise(token, op, candidates):
    if op == SUB:
        if candidates is None:
            random_token = np.random.choice(vocab_1char)
            return 1, [random_token]
        else:
            cfg_idx = 0
            prob_candidate = []
            priority_sum = 0
            # 考虑纠错词长度，如果相同，并且纠错词长度为1，则考虑纠错配置出现顺序（先配置的优先考虑），
            # 如果长度相同，并且都大于1，则各个词机会均等
            # 如果长度不同，优先考虑长度长的纠错词，所有长词匹配比例是单词匹配概率的两倍
            long_matches_cnt = 0
            short_matches_cnt = 0
            for c in candidates:
                if c.matched_tokens_num > 1 or len(c.sim_words) > 1:
                    long_matches_cnt += c.matched_tokens_num
                else:
                    short_matches_cnt += 1
            short_matche_logits_sum = 0
            for c in candidates:
                if c.matched_tokens_num == 1 and len(c.sim_words) == 1:
                    priority = char_pos_logit[cfg_idx]
                    priority_sum += priority
                    short_matche_logits_sum += priority
                    prob_candidate.append(priority)
                    if cfg_idx < len(char_pos_logit) - 1:
                        cfg_idx += 1
                else:
                    priority = ((float)(2*c.matched_tokens_num*(short_matche_logits_sum+1))) / long_matches_cnt
                    priority_sum += priority
                    prob_candidate.append(priority)
            prob_candidate = [p/priority_sum for p in prob_candidate]
            matched_info = np.random.choice(candidates, p = prob_candidate)
            return matched_info.matched_tokens_num, matched_info.sim_words
    # 如何区分hypo中 DEL 空字符(用 werdur>=2表示) 和 待删除的错误字符(werdur=0)???
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

def set_timeout(num, callback):
    def wrap(func):
        def handle(signum, frame):
            raise RuntimeError

        def to_do(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handle)
                signal.alarm(num)
                # print('start alarm signal.')
                r = func(*args, **kwargs)
                # print('close alarm signal.')
                signal.alarm(0)  #
                return r
            except RuntimeError as e:
                callback()

        return to_do

    return wrap

def after_timeout():
    pass

@set_timeout(30, after_timeout)  # 30s limitation for align
def align_encoder(hypo_sen, ref_sen):
    werdur, _ = cal_wer_dur_v1.calculate_wer_dur_v1(hypo_sen, ref_sen, return_path_only=False)

    assert len(werdur) == len(hypo_sen)
    assert len(ref_sen) == sum([abs(i) for i in werdur])

    return werdur

time_sim_chars = ['时', '是', '事', '四', '十', '分', '份', '封', '疯']
bi_sim_chars = ['比', '笔', '毕', '逼', '币', '必', '闭']
dot_sim_chars = ['点', '电', '店', '段', '限', '典', '蛋', '垫', '歉', '廉', '辨', '吊', '颠', '淀', '殿']
def noise_sentence(sentence):
    tokens = sentence.split()
    tokens_num = len(tokens)
    if tokens_num == 0:
        return "", [], []

    new_tokens = []
    filted_tokens = []

    i = 0
    prev_tok = ""
    is_time = False
    while i < tokens_num:
        tok = tokens[i]
        if not token_count_dict.__contains__(tok):
            i += 1
            continue  # 跳过不在词表中的token
        if random.random() < noise_ratio:
            if tok == ":":
                # 给汉字后面的冒号/句末的冒号/不是两个数字中间的冒号加噪声，只可能是删除该冒号
                if prev_tok == "" or ('\u4e00' <= prev_tok <= '\u9fa5' or prev_tok < '0' or prev_tok > '9') \
                        or i == (tokens_num -1) or (tokens[i+1] < '0' or tokens[i+1] > '9'):
                    i += 1
                    filted_tokens.append(tok)
                    prev_tok = tok
                    continue
                if is_time:
                    sim_token = np.random.choice(time_sim_chars)
                else:
                    sim_token = np.random.choice(bi_sim_chars)
                new_tokens.append(sim_token)
                prev_tok = tok
                i += 1
                filted_tokens.append(tok)
                continue

            if tok == ".":
                # 给汉字后面的点号/句末的点号/不是两个数字中间的点号加噪声，只可能是删除该点号
                if prev_tok == "" or ('\u4e00' <= prev_tok <= '\u9fa5' or prev_tok < '0' or prev_tok > '9') \
                        or i == (tokens_num -1) or (tokens[i+1] < '0' or tokens[i+1] > '9'):
                    i += 1
                    filted_tokens.append(tok)
                    prev_tok = tok
                    continue
                sim_token = np.random.choice(dot_sim_chars)
                new_tokens.append(sim_token)
                prev_tok = tok
                i += 1
                filted_tokens.append(tok)
                continue
            if tok == "、" or tok == '·' or tok == "'":
                #这些字符噪声只有删除
                i += 1
                filted_tokens.append(tok)
                prev_tok = tok
                continue
            if tok in preprocess.kept_char_map: #找特殊符号对应的相似读音的中文汉字
                candidates = trie_dict.get_pairs(tokens[i : i+1])
                matched_info = np.random.choice(candidates)
                new_tokens.extend(matched_info.sim_words)
                prev_tok = tok
                filted_tokens.extend(tokens[i:i + matched_info.matched_tokens_num])
                i += matched_info.matched_tokens_num
                continue
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
                matched_tokens_num, sim_tokens = add_tokens_noise(tok, meta_noise, matched_info)
                new_tokens.extend(sim_tokens)
                if prev_tok == '时' and tok == '间':
                    is_time = True
                prev_tok = tok
                filted_tokens.extend(tokens[i : i+matched_tokens_num])
                i += matched_tokens_num
                continue

        new_tokens.append(tok) #不加噪声
        if prev_tok == '时' and tok == '间':
            is_time = True
        prev_tok = tok
        i += 1
        filted_tokens.append(tok)
    if len(new_tokens) > 0:
        werdurs = align_encoder(new_tokens, filted_tokens)
        return " ".join(filted_tokens), werdurs, new_tokens
    return "", [], []

print(noise_sentence("马 丁 、 富 勒 讲 话 2 . 0 : 冲 啊 ."))
print(noise_sentence("3 × 五 = 六"))
# tokens = noise_sentence(preprocess.normAndTokenize("欢迎来到咪咕体育", 3, True)[0])
# print(noise_sentence(preprocess.normAndTokenize("欢迎参加miguday", 3, True)[0]))

import time
begin_time = time.time()
#删除老的文件
path_list=os.listdir(input_file_dir)
for filename in path_list:
    post_fix = os.path.splitext(filename)[1]
    if post_fix ==".tgt" or post_fix == ".full":
        file_path = os.path.join(input_file_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
train_output_file_idx = 0
valid_output_file_idx = 0
test_output_file_idx = 0

def write_split_align_result(data_set_name, file_idx, hypo_werdurs, refs):
    hypo_file_name = f"{data_set_name}_hypo_std_noised{random_seed:02d}_corpus{file_idx:03d}.full"
    hypo_file_path = os.path.join(input_file_dir, hypo_file_name)
    with open(hypo_file_path, 'w', encoding='utf-8') as output_hypo_file:
        output_hypo_file.writelines(hypo_werdurs)

    ref_file_name = f"{data_set_name}_ref_std_noised{random_seed:02d}_corpus{file_idx:03d}.tgt"
    ref_file_path = os.path.join(input_file_dir, ref_file_name)
    with open(ref_file_path, 'w', encoding='utf-8') as output_ref_file:
        output_ref_file.writelines(refs)

corpus_count = 0
for input_file_name in input_file_names:
    if not input_file_name.startswith("std_"): #必须是经过预处理后的
        continue
    input_file_path = os.path.join(input_file_dir, input_file_name)

    train_hypo_werdurs = []
    valid_hypo_werdurs = []
    test_hypo_werdurs = []
    train_refs = []
    valid_refs = []
    test_refs = []
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        for line in infile.readlines():
            corpus_count = corpus_count + 1
            if corpus_count % 5000 == 1:
                print("{} finished in {}s".format(corpus_count-1, time.time()-begin_time))

            line = line.strip()
            if not line:
                continue
            filt_sentence, werdurs, new_tokens = noise_sentence(line)
            if len(new_tokens) > 1: # 一句处理完成（一行有一句）
                hypo_werdur = " ".join(new_tokens) + " |||| " + " ".join([str(w) for w in werdurs]) + '\n'
                ref = filt_sentence + "\n"
                set_op = np.random.choice(set_ops, p=split_rate)
                #set_op = TRAIN
                if set_op == TRAIN:
                    train_hypo_werdurs.append(hypo_werdur)
                    train_refs.append(ref)
                elif set_op == VALID:
                    valid_hypo_werdurs.append(hypo_werdur)
                    valid_refs.append(ref)
                else:
                    test_hypo_werdurs.append(hypo_werdur)
                    test_refs.append(ref)
            if len(train_hypo_werdurs) >= MAX_CORPUS_NUM:
                write_split_align_result("train", train_output_file_idx, train_hypo_werdurs, train_refs)
                train_output_file_idx = train_output_file_idx + 1
                train_hypo_werdurs.clear()
                train_refs.clear()
            if len(valid_hypo_werdurs) >= MAX_CORPUS_NUM:
                write_split_align_result("valid", valid_output_file_idx, valid_hypo_werdurs, valid_refs)
                valid_output_file_idx = valid_output_file_idx + 1
                valid_hypo_werdurs.clear()
                valid_refs.clear()
            if len(test_hypo_werdurs) > MAX_CORPUS_NUM:
                write_split_align_result("test", test_output_file_idx, test_hypo_werdurs, test_refs)
                test_output_file_idx = test_output_file_idx + 1
                test_hypo_werdurs.clear()
                test_refs.clear()

        if len(train_hypo_werdurs) > 0:
            write_split_align_result("train", train_output_file_idx, train_hypo_werdurs, train_refs)
            train_output_file_idx = train_output_file_idx + 1
        if len(valid_hypo_werdurs) > 0:
            write_split_align_result("valid", valid_output_file_idx, valid_hypo_werdurs, valid_refs)
            valid_output_file_idx = valid_output_file_idx + 1
        if len(test_hypo_werdurs) > 0:
            write_split_align_result("test", test_output_file_idx, test_hypo_werdurs, test_refs)
            test_output_file_idx = test_output_file_idx + 1

