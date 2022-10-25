import os
import re

align_files_dir=r"./"

tgt_file_names=['train_ref_std_noised01_corpus.tgt', 'train_ref_std_noised03_corpus.tgt','train_ref_std_noised05_corpus.tgt', 'train_ref_std_noised07_corpus.tgt', 'train_ref_std_noised09_corpus.tgt',
                'valid_ref_std_noised01_corpus.tgt', 'valid_ref_std_noised03_corpus.tgt','valid_ref_std_noised05_corpus.tgt', 'valid_ref_std_noised07_corpus.tgt', 'valid_ref_std_noised09_corpus.tgt',
                'test_ref_std_noised01_corpus.tgt', 'test_ref_std_noised03_corpus.tgt','test_ref_std_noised05_corpus.tgt', 'test_ref_std_noised07_corpus.tgt', 'test_ref_std_noised09_corpus.tgt']
full_file_names=['train_hypo_std_noised01_corpus.full', 'train_hypo_std_noised03_corpus.full', 'train_hypo_std_noised05_corpus.full', 'train_hypo_std_noised07_corpus.full', 'train_hypo_std_noised09_corpus.full',
                 'valid_hypo_std_noised01_corpus.full', 'valid_hypo_std_noised03_corpus.full', 'valid_hypo_std_noised05_corpus.full', 'valid_hypo_std_noised07_corpus.full', 'valid_hypo_std_noised09_corpus.full',
                 'test_hypo_std_noised01_corpus.full', 'test_hypo_std_noised03_corpus.full', 'test_hypo_std_noised05_corpus.full', 'test_hypo_std_noised07_corpus.full', 'test_hypo_std_noised09_corpus.full']

if os.path.exists(os.path.join(align_files_dir, "train.zh_CN")):
    os.remove(os.path.join(align_files_dir, "train.zh_CN"))
if os.path.exists(os.path.join(align_files_dir, "train.zh_CN_tgt")):
    os.remove(os.path.join(align_files_dir, "train.zh_CN_tgt"))

if os.path.exists(os.path.join(align_files_dir, "valid.zh_CN")):
    os.remove(os.path.join(align_files_dir, "valid.zh_CN"))
if os.path.exists(os.path.join(align_files_dir, "valid.zh_CN_tgt")):
    os.remove(os.path.join(align_files_dir, "valid.zh_CN_tgt"))

if os.path.exists(os.path.join(align_files_dir, "test.zh_CN")):
    os.remove(os.path.join(align_files_dir, "test.zh_CN"))
if os.path.exists(os.path.join(align_files_dir, "test.zh_CN_tgt")):
    os.remove(os.path.join(align_files_dir, "test.zh_CN_tgt"))

merged_train_full_file = open(os.path.join(align_files_dir, "train.zh_CN"), 'w+', encoding='UTF-8')
merged_train_tgt_file = open(os.path.join(align_files_dir, "train.zh_CN_tgt"), 'w+', encoding='UTF-8')
merged_valid_full_file = open(os.path.join(align_files_dir, "valid.zh_CN"), 'w+', encoding='UTF-8')
merged_valid_tgt_file = open(os.path.join(align_files_dir, "valid.zh_CN_tgt"), 'w+', encoding='UTF-8')
merged_test_full_file = open(os.path.join(align_files_dir, "test.zh_CN"), 'w+', encoding='UTF-8')
merged_test_tgt_file = open(os.path.join(align_files_dir, "test.zh_CN_tgt"), 'w+', encoding='UTF-8')

train_full_lines = []
train_tgt_lines = []
valid_full_lines = []
valid_tgt_lines = []
test_full_lines = []
test_tgt_lines = []
for full_file_name,tgt_file_name in zip(full_file_names, tgt_file_names):
    full_file = open(os.path.join(align_files_dir, full_file_name), 'r', encoding='UTF-8')
    tgt_file = open(os.path.join(align_files_dir, tgt_file_name), 'r', encoding='UTF-8')
    full_lines = full_file.readlines()
    tgt_lines = tgt_file.readlines()
    assert len(full_lines) == len(tgt_lines)
    for full_line, tgt_line in zip(full_lines, tgt_lines):
        fields = full_line.split(" |||| ")
        hypo=fields[0].replace(" ", "")
        ref = tgt_line.replace(" ", "")
        if len(hypo) <= 1 or len(ref) <= 1:
            continue
        full_lines.append(full_line)
        tgt_lines.append(tgt_line)
    if full_file_name.startswith("train"):
        train_full_lines.extend(full_lines)
        train_tgt_lines.extend(tgt_lines)
    elif full_file_name.startswith("valid"):
        valid_full_lines.extend(full_lines)
        valid_tgt_lines.extend(tgt_lines)
    else:
        test_full_lines.extend(full_lines)
        test_tgt_lines.extend(tgt_lines)

merged_train_full_file.writelines(train_full_lines)
merged_train_tgt_file.writelines(train_tgt_lines)
merged_valid_full_file.writelines(valid_full_lines)
merged_valid_tgt_file.writelines(valid_tgt_lines)
merged_test_full_file.writelines(test_full_lines)
merged_test_tgt_file.writelines(test_tgt_lines)

merged_train_full_file.close()
merged_train_tgt_file.close()
merged_valid_full_file.close()
merged_valid_tgt_file.close()
merged_test_full_file.close()
merged_test_tgt_file.close()
