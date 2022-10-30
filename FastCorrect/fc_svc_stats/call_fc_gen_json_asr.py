# -*- coding: utf-8 -*-
import sys
import os.path
import codecs
import json
import requests
import bson
sys.path.append("..")
from scripts import preprocess
#import preprocess

correctUrl = "http://39.105.31.210:5051/fast_correct"
corpus_root_dir=r'C:\corpus\valid'
asr_file_names = ["std_【厂家】10_8切尔西vsAC米兰_asr.txt", "std_【厂家】10_8马略卡vs巴塞罗那_asr.txt", "std_【厂家】10_9伯恩茅斯vs莱斯特城_asr.txt",
                  "std_【厂家】10_9曼城vs南安普顿_asr.txt", "std_【厂家】10_9赫塔菲vs皇家马德里_asr.txt",
                  "std_【厂家】21_22赛季意甲第38轮全场回放_国际米兰3_0桑普多利亚_刘腾_贺宇_asr.txt", "std_【厂家】恩波利VSAC米兰_asr.txt",
                  "std_【厂家】曼联vs布莱顿_2022_8_12_asr.txt", "std_【厂家】韩国女足VS中国台北女足_asr.txt",
                  "std_【验证】全场回放_2019法国女足世界杯小组赛E组第二轮_加拿大2_0新西兰02_asr.txt", "std_厂家8_21斯特拉斯堡vs兰斯_asr.txt",
                  "std_厂家_09_13赫塔菲vs皇家社会_asr.txt", "std_厂家_21_22赛季西甲第36轮全场回放-格拉纳达1_0毕尔巴鄂竞技_asr.txt",
                  "std_厂家_8_15_多特蒙德vs勒沃库森_asr.txt", "std_厂家_8_22亚特兰大vsAC米兰_asr.txt", "std_厂家_8_28尤文图斯VS罗马_asr.txt",
                  "std_厂家_8_28尼斯vs马赛_asr.txt", "std_厂家_8_28阿斯顿维拉vs西汉姆联_asr.txt", "std_厂家_8_29巴塞罗那vs巴拉多利德_asr.txt",
                  "std_厂家_9_17_斯图加特vs法兰克福_asr.txt", "std_厂家_9_1昂热vs兰斯_asr.txt", "std_厂家_9_1阿森纳vs阿斯顿维拉_asr.txt",
                  "std_厂家_9_4兰斯vs朗斯_asr.txt", "std_厂家_9_4切尔西vs西汉姆联_asr.txt", "std_验证__2022_8_11_利兹联vs狼队_asr.txt"]
def fc_correct(text):
    headers = {'Content-Type': 'application/json'}
    body = {'text': text}
    body = json.dumps(body)
    resp = requests.request("POST", correctUrl, headers=headers, data=body, verify=False)
    resp_json = resp.json()
    if resp_json['result_code'] and "200" == resp_json['result_code']:
        corrections = resp_json['corrections']
        if len(corrections) == 1:
            return corrections[0]["fc_text"]
    return ""

for asr_file_name in asr_file_names:
    asr_file = codecs.open(os.path.join(corpus_root_dir, asr_file_name), 'r', 'utf-8')
    asr_lines = asr_file.readlines()
    asr_objects = {}
    asr_objects["utts"] = {}
    fc_objects = {}
    fc_objects["utts"]={}
    for asr_line in asr_lines:
        fields = asr_line.split("\t")
        if len(fields) != 2:
            continue
        ref_tokens = fields[0]
        asr_tokens = fields[1]
        ref_sentences = preprocess.normAndTokenize(" ".join(ref_tokens), min_sentence_len=3, split_sentences=True)
        asr_sentences = preprocess.normAndTokenize(" ".join(asr_tokens), min_sentence_len=3,split_sentences=True)
        if len(asr_sentences) != len(ref_sentences):
            continue
        for asr_sentence,ref_sentence in zip(asr_sentences, ref_sentences):
            fc_result_text = fc_correct("".join(asr_sentence.split()))
            fc_result_tokens = preprocess.normAndTokenize(fc_result_text)[0]
            output0 = {'rec_text': fc_result_text, 'rec_token': fc_result_tokens,
                       'text': "".join("".join(ref_sentence.split())),
                       'token': " ".join(ref_sentence.split())}
            id = str(bson.ObjectId())
            output1 = [output0]
            output = {'output': output1}
            fc_objects["utts"][id] = output

            output0 = {'rec_text': "".join(asr_sentence.split()), 'rec_token': " ".join(asr_sentence.split()),
                       'text': "".join("".join(ref_sentence.split())),
                       'token': " ".join(ref_sentence.split())}
            output1 = [output0]
            output = {'output': output1}
            asr_objects["utts"][id] = output
    asr_string = json.dumps(asr_objects, ensure_ascii=False, indent=2)
    fc_string = json.dumps(fc_objects, ensure_ascii=False, indent=2)

    asr_json_file_name = "asr_" + asr_file_name[0:-4] + ".json"
    fc_json_file_name = "fc_" + asr_file_name[0:-4] + ".json"
    with open(os.path.join(corpus_root_dir, asr_json_file_name), "w", encoding='utf-8') as f:
        f.write(asr_string)
    with open(os.path.join(corpus_root_dir, fc_json_file_name), "w", encoding='utf-8') as f:
        f.write(fc_string)


