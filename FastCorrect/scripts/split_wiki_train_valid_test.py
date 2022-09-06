import os
import random
import numpy as np

# 源文件路径
corpus_root_dir = r"/root/extracted/AA"
#corpus_root_dir = r"C:\Code\NeuralSpeech\FastCorrect"
#output of align_cal_werdur_v2.py
hypo_full_file_names=["hypo_noised1_std_zh_wiki_00.src.werdur.full","hypo_noised1_std_zh_wiki_01.src.werdur.full","hypo_noised1_std_zh_wiki_02.src.werdur.full",
                      "hypo_noised3_std_zh_wiki_00.src.werdur.full","hypo_noised3_std_zh_wiki_01.src.werdur.full","hypo_noised3_std_zh_wiki_02.src.werdur.full",
                      "hypo_noised5_std_zh_wiki_00.src.werdur.full","hypo_noised5_std_zh_wiki_01.src.werdur.full","hypo_noised5_std_zh_wiki_02.src.werdur.full",
                      "hypo_noised7_std_zh_wiki_00.src.werdur.full","hypo_noised7_std_zh_wiki_01.src.werdur.full","hypo_noised7_std_zh_wiki_02.src.werdur.full",
                      "hypo_noised9_std_zh_wiki_00.src.werdur.full","hypo_noised9_std_zh_wiki_01.src.werdur.full","hypo_noised9_std_zh_wiki_02.src.werdur.full"]
ref_tgt_file_names=["ref_noised1_std_zh_wiki_00.tgt","ref_noised1_std_zh_wiki_01.tgt","ref_noised1_std_zh_wiki_02.tgt",
                      "ref_noised3_std_zh_wiki_00.tgt","ref_noised3_std_zh_wiki_01.tgt","ref_noised3_std_zh_wiki_02.tgt",
                      "ref_noised5_std_zh_wiki_00.tgt","ref_noised5_std_zh_wiki_01.tgt","ref_noised5_std_zh_wiki_02.tgt",
                      "ref_noised7_std_zh_wiki_00.tgt","ref_noised7_std_zh_wiki_01.tgt","ref_noised7_std_zh_wiki_02.tgt",
                      "ref_noised9_std_zh_wiki_00.tgt","ref_noised9_std_zh_wiki_01.tgt","ref_noised9_std_zh_wiki_02.tgt"]
# hypo_full_file_names = ["hypo.txt.src.werdur.full"]
# ref_tgt_file_names = ["ref.txt.tgt"]
random_seed = 3
split_rate = [0.998, 0.001, 0.001]
random.seed(random_seed)
np.random.seed(random_seed)

TRAIN = 0
VALID = 1
TEST = 2
set_ops = [TRAIN, VALID, TEST]
train_map = {}
valid_map = {}
test_map = {}
train_hypo_full_file_path = os.path.join(corpus_root_dir, "train.zh_CN")
train_ref_full_file_path = os.path.join(corpus_root_dir, "train.zh_CN_tgt")
valid_hypo_full_file_path = os.path.join(corpus_root_dir, "valid.zh_CN")
valid_ref_full_file_path = os.path.join(corpus_root_dir, "valid.zh_CN_tgt")
test_hypo_full_file_path = os.path.join(corpus_root_dir, "test.zh_CN")
test_ref_full_file_path = os.path.join(corpus_root_dir, "test.zh_CN_tgt")
if os.path.exists(train_hypo_full_file_path):
    os.remove(train_hypo_full_file_path)
if os.path.exists(train_ref_full_file_path):
    os.remove(train_ref_full_file_path)
if os.path.exists(valid_hypo_full_file_path):
    os.remove(valid_hypo_full_file_path)
if os.path.exists(valid_ref_full_file_path):
    os.remove(valid_ref_full_file_path)
if os.path.exists(test_hypo_full_file_path):
    os.remove(test_hypo_full_file_path)
if os.path.exists(test_ref_full_file_path):
    os.remove(test_ref_full_file_path)

for hypo_full_file_name,ref_tgt_file_name in zip(hypo_full_file_names, ref_tgt_file_names):
    hypo_full_file_path = os.path.join(corpus_root_dir, hypo_full_file_name)
    ref_tgt_file_path = os.path.join(corpus_root_dir, ref_tgt_file_name)
    # 抽取训练集hypo数据
    train_hypo_sampled_lines = []
    train_ref_sampled_lines = []
    valid_hypo_sampled_lines = []
    valid_ref_sampled_lines = []
    test_hypo_sampled_lines = []
    test_ref_sampled_lines = []
    with open(hypo_full_file_path, 'r', encoding='utf-8') as hypo_full_file:
        with open(ref_tgt_file_path, 'r', encoding='utf-8') as ref_tgt_file:
            hypo_full_lines = hypo_full_file.readlines()
            ref_tgt_lines = ref_tgt_file.readlines()
            for ref_tgt_line,hypo_full_line in zip(ref_tgt_lines, hypo_full_lines):
                if ref_tgt_line in train_map:
                    train_hypo_sampled_lines.append(hypo_full_line)
                    train_ref_sampled_lines.append(ref_tgt_line)
                elif ref_tgt_line in valid_map:
                    valid_hypo_sampled_lines.append(hypo_full_line)
                    valid_ref_sampled_lines.append(ref_tgt_line)
                elif ref_tgt_line in test_map:
                    test_hypo_sampled_lines.append(hypo_full_line)
                    test_ref_sampled_lines.append(ref_tgt_line)
                else:
                    set_op = np.random.choice(set_ops, p=split_rate)
                    if set_op == TRAIN:
                        train_hypo_sampled_lines.append(hypo_full_line)
                        train_ref_sampled_lines.append(ref_tgt_line)
                        train_map[ref_tgt_line] = "1"
                    elif set_op == VALID:
                        valid_hypo_sampled_lines.append(hypo_full_line)
                        valid_ref_sampled_lines.append(ref_tgt_line)
                        valid_map[ref_tgt_line] = "1"
                    else:
                        test_hypo_sampled_lines.append(hypo_full_line)
                        test_ref_sampled_lines.append(ref_tgt_line)
                        test_map[ref_tgt_line] = "1"
            with open(train_hypo_full_file_path, 'a', encoding='utf-8') as train_hypo_full_file:
                train_hypo_full_file.writelines(train_hypo_sampled_lines)
            with open(train_ref_full_file_path, 'a', encoding='utf-8') as train_ref_full_file:
                train_ref_full_file.writelines(train_ref_sampled_lines)
            with open(valid_hypo_full_file_path, 'a', encoding='utf-8') as valid_hypo_full_file:
                valid_hypo_full_file.writelines(valid_hypo_sampled_lines)
            with open(valid_ref_full_file_path, 'a', encoding='utf-8') as valid_ref_full_file:
                valid_ref_full_file.writelines(valid_ref_sampled_lines)
            with open(test_hypo_full_file_path, 'a', encoding='utf-8') as test_hypo_full_file:
                test_hypo_full_file.writelines(test_hypo_sampled_lines)
            with open(test_ref_full_file_path, 'a', encoding='utf-8') as test_ref_full_file:
                test_ref_full_file.writelines(test_ref_sampled_lines)
