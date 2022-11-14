# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import sys
import torch
import argparse
import re
#from fastcorrect_model import FastCorrectModel
import os
import os.path
import time
import json
import numpy as np

from fairseq import utils
utils.import_user_module(argparse.Namespace(user_dir='./FastCorrect'))
from FastCorrect.fastcorrect_model import FastCorrectModel

def remove_ch_spaces(input_str):
    return re.sub(r"(?<=[\u4e00-\u9fff])(\s+)(?=[\u4e00-\u9fff])", "", input_str.strip())


try:
    model_name_or_path = sys.argv[3]
except:
    model_name_or_path = "checkpoints/shared_baseline"

try:
    iter_decode_max_iter = int(sys.argv[5])
except:
    iter_decode_max_iter = -1

try:
    edit_thre = float(sys.argv[6])
except:
    edit_thre = 0

try:
    test_epoch = int(sys.argv[7])
    checkpoint_file = "checkpoint{}.pt".format(test_epoch)
except:
    test_epoch = 'best'
    checkpoint_file = "checkpoint_best.pt"

print("test {}/{}".format(model_name_or_path, checkpoint_file))
# the model will only use the dictionary in data_name_or_path.
# data_name_or_path = "/root/fastcorrect/data/werdur_data_aishell.bin" # <Path-to-AISHELL1-Training-Binary-Data>
data_name_or_path = sys.argv[4] # <Path-to-AISHELL1-Training-Binary-Data>
bpe = "sentencepiece"
sentencepiece_model = "/root/fastcorrect/sentencepiece/FastCorrect_zhwiki_sentencepiece.model" # <path-to-sentencepiece_model>, you can use arbitrary sentencepiece for our pretrained model since it is a char-level model

commonset_dir = sys.argv[1]
res_dir = os.path.join(model_name_or_path, ("results_asr" if (iter_decode_max_iter == -1) else ("results_asr_b" + str(iter_decode_max_iter) + '_t' + str(edit_thre))).replace('results', 'results_' + str(test_epoch)))
tmp_dir = os.path.join(model_name_or_path, ("tmp_asr" if (iter_decode_max_iter == -1) else ("tmp_asr_b" + str(iter_decode_max_iter) + '_t' + str(edit_thre))).replace('tmp', 'tmp_' + str(test_epoch)))
os.makedirs(res_dir, exist_ok=True)
os.makedirs(tmp_dir, exist_ok=True)

try:
    short_set = sys.argv[2].split(',')
except:
    raise ValueError()
print("short_set:", short_set)

#transf_gec = FastCorrectModel.from_pretrained(model_name_or_path, checkpoint_file=checkpoint_file, data_name_or_path=data_name_or_path, bpe=bpe, sentencepiece_model=sentencepiece_model, user_dir='./FastCorrect')
transf_gec = FastCorrectModel.from_pretrained(model_name_or_path, checkpoint_file=checkpoint_file, data_name_or_path=data_name_or_path, bpe=bpe, sentencepiece_model=sentencepiece_model)

transf_gec.eval()
transf_gec.cuda()

for input_tsv in [os.path.join(commonset_dir, f, "data.json") for f in short_set]:
    all_time = []
    eval_origin_dict = json.load(open(input_tsv, 'r', encoding='utf-8'))
    translate_input_dict = {}
    for k, v in eval_origin_dict["utts"].items():
        translate_input_dict[k] = (v["output"][0]["rec_token"].replace('<eos>', '').strip(), v["output"][0]["token"])
    translated_output_dict = {}
    processed_items = 0
    for k, v in translate_input_dict.items():
        text = v[0] #ASR识别结果（value中的第一个元素：json中的rec_token字段）
        #print(text)
        gt = v[1] #原始语料value中的第二个元素：json中的token字段）
        start_time = time.time()
        time_ok = False
        try:
            if iter_decode_max_iter != -1:
                text = transf_gec.binarize(text)
                batched_hypos = transf_gec.generate(text, iter_decode_max_iter=iter_decode_max_iter)
                translated = [transf_gec.decode(hypos[0]['tokens']) for hypos in batched_hypos][0]
                #translated = transf_gec.translate(text, iter_decode_max_iter=iter_decode_max_iter, edit_thre=edit_thre)
            else:
                translated = transf_gec.translate(text)
            if isinstance(translated, tuple):
                all_time.append(translated[1])
                time_ok = True
                translated = translated[0]
            # text：ASR识别结果，gt：原始的正确语料 translated：fc纠错结果
            translated_output_dict[k] = (text, gt, translated)
        except Exception as e:
            print(input_tsv + "\t" + text + "\n")
            translated_list.append(text)
            raise e
            processed_items += 1
            continue
        end_time = time.time()
        if not time_ok:
            all_time.append(end_time - start_time)
        # 这里的分词不准确，应该用 preprocess 分词
        eval_origin_dict["utts"][k]["output"][0]["rec_text"] = " ".join("".join(translated.split()).replace('▁', ' ').strip().split())
        translated_char = [i for i in eval_origin_dict["utts"][k]["output"][0]["rec_text"]]
        # 将ASR转写出的结果，经过FC模型处理后，替换到 data.json 中的 rec_token/rec_text 中
        eval_origin_dict["utts"][k]["output"][0]["rec_token"] = " ".join(translated_char)
        processed_items += 1
        if processed_items % 500 == 0:
            ratio = int(processed_items * 100 / len(translate_input_dict.items()))
            print(f"{ratio}% ({processed_items}/{len(translate_input_dict.items())}) processed.")
        #print(" ".join(translated_char))
    os.makedirs(os.path.join(res_dir, input_tsv.split('/')[-2]), exist_ok=True)
    with open(os.path.join(res_dir, input_tsv.split('/')[-2], input_tsv.split('/')[-2] + "_time.txt"), 'w') as outfile:
        outfile.write("{}\t{}\t{}\n".format(len(all_time), sum(all_time), sum(all_time)/len(all_time)))
    json.dump(eval_origin_dict, open(os.path.join(res_dir, input_tsv.split('/')[-2], 'data.json'), 'w', encoding='utf-8'), indent=4, sort_keys=True, ensure_ascii=False)


