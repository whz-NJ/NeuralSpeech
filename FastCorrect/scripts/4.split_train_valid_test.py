import os
import random

# 源文件路径
corpus_root_dir = r"/root/asr/"
#corpus_root_dir = r"C:\Code\NeuralSpeech\FastCorrect"
#output of align_cal_werdur_v2.py
hypo_full_file_name="hypo_std_noised_corpus.txt.src.werdur.full"
ref_tgt_file_name="ref_std_noised_corpus.txt.tgt"
#hypo_full_file_name="hypo7.txt.src.werdur.full"
#ref_tgt_file_name="ref7.txt.tgt"

# 划分数据比例为8:1:1
split_rate = [0.97, 0.02, 0.01]
hypo_full_file_path = os.path.join(corpus_root_dir, hypo_full_file_name)
ref_tgt_file_path = os.path.join(corpus_root_dir, ref_tgt_file_name)
ref_hypos_map = {}
with open(hypo_full_file_path, 'r', encoding='utf-8') as hypo_full_file:
    with open(ref_tgt_file_path, 'r', encoding='utf-8') as ref_tgt_file:
        hypo_full_lines = hypo_full_file.readlines()
        ref_tgt_lines = ref_tgt_file.readlines()
        for ref_tgt_line,hypo_full_line in zip(ref_tgt_lines, hypo_full_lines):
            ref_hypos = ref_hypos_map.get(ref_tgt_line.strip(), [])
            ref_hypos.append(hypo_full_line.strip())
            ref_hypos_map[ref_tgt_line.strip()] = ref_hypos

sorted_ref_hypos = sorted(ref_hypos_map.items(), key=lambda x: x[0])
refs_num = len(sorted_ref_hypos)

refs_indexes = list(range(refs_num))
random.shuffle(refs_indexes)
train_stop_index = int(refs_num * split_rate[0])
valid_stop_index = int(refs_num * (split_rate[0] + split_rate[1]))

#抽取训练集hypo数据
hypo_sampled_lines = []
ref_sampled_lines = []
for ref_idx in refs_indexes[0:train_stop_index]:
    ref = sorted_ref_hypos[ref_idx][0].strip()
    hypos = sorted_ref_hypos[ref_idx][1]
    for hypo in hypos:
        hypo_sampled_line = hypo.strip()
        ref_sampled_line = ref
        if len(hypo_sampled_line) > 0 and len(ref_sampled_line) > 0:
            hypo_sampled_lines.append(hypo_sampled_line+"\n")
            ref_sampled_lines.append(ref_sampled_line+"\n")
# 抽取训练集ref数据
train_hypo_full_file_path = os.path.join(corpus_root_dir, "train.zh_CN")
with open(train_hypo_full_file_path, 'w', encoding='utf-8') as train_hypo_full_file:
    train_hypo_full_file.writelines(hypo_sampled_lines)
train_ref_tgt_file_path = os.path.join(corpus_root_dir, "train.zh_CN_tgt")
with open(train_ref_tgt_file_path, 'w', encoding='utf-8') as train_ref_tgt_file:
    train_ref_tgt_file.writelines(ref_sampled_lines)

# 抽取验证集hypo数据
hypo_sampled_lines = []
ref_sampled_lines = []
for ref_idx in refs_indexes[train_stop_index:valid_stop_index]:
    ref = sorted_ref_hypos[ref_idx][0].strip()
    hypos = sorted_ref_hypos[ref_idx][1]
    for hypo in hypos:
        hypo_sampled_line = hypo.strip()
        ref_sampled_line = ref
        if len(hypo_sampled_line) > 0 and len(ref_sampled_line) > 0:
            hypo_sampled_lines.append(hypo_sampled_line+"\n")
            ref_sampled_lines.append(ref_sampled_line+"\n")
valid_hypo_full_file_path = os.path.join(corpus_root_dir, "valid.zh_CN")
with open(valid_hypo_full_file_path, 'w', encoding='utf-8') as valid_hypo_full_file:
    valid_hypo_full_file.writelines(hypo_sampled_lines)
# 抽取验证集ref数据
valid_ref_tgt_file_path = os.path.join(corpus_root_dir, "valid.zh_CN_tgt")
with open(valid_ref_tgt_file_path, 'w', encoding='utf-8') as valid_ref_tgt_file:
    valid_ref_tgt_file.writelines(ref_sampled_lines)

# 抽取测试集hypo数据
hypo_sampled_lines = []
ref_sampled_lines = []
for ref_idx in refs_indexes[valid_stop_index:]:
    ref = sorted_ref_hypos[ref_idx][0].strip()
    hypos = sorted_ref_hypos[ref_idx][1]
    for hypo in hypos:
        hypo_sampled_line = hypo.strip()
        ref_sampled_line = ref
        if len(hypo_sampled_line) > 0 and len(ref_sampled_line) > 0:
            hypo_sampled_lines.append(hypo_sampled_line+"\n")
            ref_sampled_lines.append(ref_sampled_line+"\n")
test_hypo_full_file_path = os.path.join(corpus_root_dir, "test.zh_CN")
with open(test_hypo_full_file_path, 'w', encoding='utf-8') as test_hypo_full_file:
    test_hypo_full_file.writelines(hypo_sampled_lines)
# 抽取测试集ref数据
test_ref_tgt_file_path = os.path.join(corpus_root_dir, "test.zh_CN_tgt")
with open(test_ref_tgt_file_path, 'w', encoding='utf-8') as test_ref_tgt_file:
    test_ref_tgt_file.writelines(ref_sampled_lines)

