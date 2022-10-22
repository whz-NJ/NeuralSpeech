# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

#Usage python align_cal_werdur_v2.py <input-tokened-hypo-text-file> <input-tokened-ref-text-file>
#Note:
#  The script will align <input-tokened-hypo-text-file> (text with errors) with <input-tokened-ref-text-file> (ground-truth text) and obtain the number of target token corresponding with each source token
#  The script might skip sentence which takes too much time for alignment.
#  The aligned result of <input-tokened-hypo-text-file> is in <input-tokened-hypo-text-file>.src.werdur.full, which consists of source tokens with their duration.
#  The aligned result of <input-tokened-ref-text-file> is in <input-tokened-hypo-ref-file>.tgt, which consists of target tokens.
#  The sum of all source token durations is equal to the number of target token.
#  <input-tokened-hypo-text-file>.src.werdur.full is used as source file when generating binary dataset; <input-tokened-hypo-ref-file>.tgt is used as target file when generating binary dataset
import os.path
import sys
import numpy as np
import copy
import random
import signal
import time
import cal_wer_dur_v1

#random_seed = sys.argv[1]
#random_seed = 3

# input_file_dir = '/root/sports_corpus2/'
# input_file_dir = r'c:/code/neuralspeech/fastcorrect/'
#input_file_dir = '/root/extracted/AA/'
#input_file_dir = '/root/std_sports_corpus_en/'
input_file_dir = '/root/std_sports_corpus_en3'
#output of gen_hypo_ref_file.py
# hypo_input_file_names = [r'hypo7.txt']
# ref_input_file_names = [r'ref7.txt']
#hypo_input_file_names = [r'hypo_noised1_std_zh_wiki_01',r'hypo_noised1_std_zh_wiki_02',
#        ]
#ref_input_file_names = [r'ref_noised1_std_zh_wiki_01',r'ref_noised1_std_zh_wiki_02',
#        ]
hypo_input_file_names = ['hypo_train_std_noised_corpus.txt', 'hypo_valid_std_noised_corpus.txt', 'hypo_test_std_noised_corpus.txt']
ref_input_file_names = ['ref_train_std_noised_corpus.txt', 'ref_valid_std_noised_corpus.txt', 'ref_test_std_noised_corpus.txt']

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

# @set_timeout(30, after_timeout)  # 30s limitation for align
def align_encoder(hypo_sen, ref_sen):
    werdur, _ = cal_wer_dur_v1.calculate_wer_dur_v1(hypo_sen, ref_sen, return_path_only=False)
    output_token_str = " ".join(hypo_sen)
    output_werdur_str = " ".join([str(m) for m in werdur])

    assert len(werdur) == len(hypo_sen)
    assert len(ref_sen) == sum([abs(i) for i in werdur])

    output_src_str = output_token_str + " |||| " + output_werdur_str
    output_tgt_str = " ".join(ref_sen)

    return output_src_str, output_tgt_str

out = align_encoder("数 学 对 肝 这 些 领 域 的 蓟 应 用 通 常 被 辰 为 应 数 学".split(),
                    "数 学 对    这 些 领 域 的    应 用 通 常 被 称 为 应 用 数 学".split())
print(out)

out = align_encoder("1 9 8 0 视 剧 集 上 绫 海 滩 症 饰 严 冯 精 尧".split(),
                    "1 9 8 0 年 在 电 视 剧 集 上 海 滩 中 饰 演 冯 敬 尧".split())
print(out)

out = align_encoder("地 球 村 遍 得 过 时".split(),
                    "地 球 村 逐 渐 变 得 过 时".split())
print(out)

for hypo_file_name, ref_file_name in zip(hypo_input_file_names, ref_input_file_names):
    hypo_file_path = os.path.join(input_file_dir, hypo_file_name)
    ref_file_path = os.path.join(input_file_dir, ref_file_name)

    all_hypo_line = []
    all_ref_line = []
    print(f"Loading: {hypo_file_path} ...")
    with open(hypo_file_path, 'r', encoding='utf-8') as infile:
        for line in infile.readlines():
            tokens = line.strip().split()
            all_hypo_line.append(tokens)
    print(f"Loading: {ref_file_path} ...")
    with open(ref_file_path, 'r', encoding='utf-8') as infile:
        for line in infile.readlines():
            tokens = line.strip().split()
            all_ref_line.append(tokens)
    ##计算对齐效果 富尔基耶	-2这副耳机
    start_time = time.time()
    count = 0
    count_no_skip = 0
    with open(ref_file_path + '.tgt', 'w', encoding='utf-8') as outfile_tgt:
        with open(hypo_file_path + '.src.werdur.full', 'w', encoding='utf-8') as outfile_full:
            outfile_full_lines = []
            outfile_tgt_lines = []
            for hypo_list, ref_list in zip(all_hypo_line, all_ref_line):
                skip_this = False
                if not hypo_list:
                    skip_this = True
                if not ref_list:
                    skip_this = True
                if not skip_this:
                    results = align_encoder(hypo_list, ref_list)
                    if results:
                        count_no_skip += 1
                        output_src_str, output_tgt_str = results
                        outfile_full_lines.append(output_src_str + "\n")
                        outfile_tgt_lines.append(output_tgt_str + "\n")
                        if len(outfile_tgt_lines) > 10000:
                            outfile_full.writelines(outfile_full_lines)
                            outfile_tgt.writelines(outfile_tgt_lines)
                            outfile_full_lines = []
                            outfile_tgt_lines =[]
                count += 1

                if count % 10000 == 0:
                    print(count, "in", time.time() - start_time, "s")
                    print(count_no_skip, "not skipped!")
            if len(outfile_tgt_lines) > 0:
                outfile_full.writelines(outfile_full_lines)
                outfile_tgt.writelines(outfile_tgt_lines)
    print("Overall: {}/{} finished successful!".format(count_no_skip, count))


