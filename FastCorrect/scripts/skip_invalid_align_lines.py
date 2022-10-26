import os
import re

align_files_dir=r"./"

tgt_file_names=['train_ref_std_noised01_corpus.tgt', 'train_ref_std_noised03_corpus.tgt','train_ref_std_noised05_corpus.tgt', 'train_ref_std_noised07_corpus.tgt', 'train_ref_std_noised09_corpus.tgt',
                'valid_ref_std_noised01_corpus.tgt', 'valid_ref_std_noised03_corpus.tgt','valid_ref_std_noised05_corpus.tgt', 'valid_ref_std_noised07_corpus.tgt', 'valid_ref_std_noised09_corpus.tgt',
                'test_ref_std_noised01_corpus.tgt', 'test_ref_std_noised03_corpus.tgt','test_ref_std_noised05_corpus.tgt', 'test_ref_std_noised07_corpus.tgt', 'test_ref_std_noised09_corpus.tgt']
full_file_names=['train_hypo_std_noised01_corpus.full', 'train_hypo_std_noised03_corpus.full', 'train_hypo_std_noised05_corpus.full', 'train_hypo_std_noised07_corpus.full', 'train_hypo_std_noised09_corpus.full',
                 'valid_hypo_std_noised01_corpus.full', 'valid_hypo_std_noised03_corpus.full', 'valid_hypo_std_noised05_corpus.full', 'valid_hypo_std_noised07_corpus.full', 'valid_hypo_std_noised09_corpus.full',
                 'test_hypo_std_noised01_corpus.full', 'test_hypo_std_noised03_corpus.full', 'test_hypo_std_noised05_corpus.full', 'test_hypo_std_noised07_corpus.full', 'test_hypo_std_noised09_corpus.full']

seed_pattern = re.compile(r'(train|valid|test)_hypo_std_noised(\d{2})_corpus.full')
for full_file_name,tgt_file_name in zip(full_file_names, tgt_file_names):
    match = seed_pattern.match(full_file_name)
    if not match:
        print("unexpected full file name: " + full_file_name)
        continue
    seed = match.group(2)
    full_file0 = open(os.path.join(align_files_dir, full_file_name), 'r', encoding='UTF-8')
    tgt_file0 = open(os.path.join(align_files_dir, tgt_file_name), 'r', encoding='UTF-8')
    full_lines0 = full_file0.readlines()
    tgt_lines0 = tgt_file0.readlines()
    full_file0.close()
    tgt_file0.close()

    full_lines = []
    tgt_lines = []
    assert len(full_lines0) == len(tgt_lines0)
    for full_line, tgt_line in zip(full_lines0, tgt_lines0):
        fields = full_line.split(" |||| ")
        assert len(fields) == 2
        hypo=fields[0].replace(" ", "")
        ref = tgt_line.replace(" ", "")
        if len(hypo) <= 1 or len(ref) <= 1:
            continue
        full_lines.append(full_line)
        tgt_lines.append(tgt_line)

    if full_file_name.startswith("train"):
        full_file = open(os.path.join(align_files_dir, f"train{seed}.zh_CN"), 'w', encoding='UTF-8')
        tgt_file = open(os.path.join(align_files_dir, f"train{seed}.zh_CN_tgt"), 'w', encoding='UTF-8')
    elif full_file_name.startswith("valid"):
        full_file = open(os.path.join(align_files_dir, f"valid{seed}.zh_CN"), 'w', encoding='UTF-8')
        tgt_file = open(os.path.join(align_files_dir, f"valid{seed}.zh_CN_tgt"), 'w', encoding='UTF-8')
    else:
        full_file = open(os.path.join(align_files_dir, f"test{seed}.zh_CN"), 'w', encoding='UTF-8')
        tgt_file = open(os.path.join(align_files_dir, f"test{seed}.zh_CN_tgt"), 'w', encoding='UTF-8')
    full_file.writelines(full_lines)
    tgt_file.writelines(tgt_lines)
    full_file.close()
    tgt_file.close()

