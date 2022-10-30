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
corpus_root_dir=r'C:\工作任务\AIUI\NLP模型测试\侯德成语料2'
# asr_file_names=["原始字幕_9_18里昂vs巴黎圣日耳曼.txt", "原始字幕_9_18南特vs朗斯.txt", "原始字幕_厂家_9_18_埃弗顿vs西汉姆联.txt",
#             "原始字幕_厂家_9_18皇家社会VS西班牙人.txt","原始字幕_厂家_9_18霍芬海姆vs弗赖堡.txt","原始字幕_厂家9_18罗马VS亚特兰大.txt",
#             "原始字幕_厂家9_18蒙扎vs尤文图斯.txt"]
# ref_file_names=["转写后标注字幕_9_18里昂vs巴黎圣日耳曼.txt", "转写后标注字幕_9_18南特vs朗斯.txt", "转写后标注字幕_厂家_9_18_埃弗顿vs西汉姆联.txt",
#             "转写后标注字幕_厂家_9_18皇家社会VS西班牙人.txt","转写后标注字幕_厂家_9_18霍芬海姆vs弗赖堡.txt","转写后标注字幕_厂家9_18罗马VS亚特兰大.txt",
#             "转写后标注字幕_厂家9_18蒙扎vs尤文图斯.txt"]

asr_file_names = ["原始字幕_10_8云达不莱梅vs门兴格拉德巴赫.txt", "原始字幕_10_8国际米兰vs巴塞罗那.txt", "原始字幕_10_8拜仁慕尼黑vs勒沃库森.txt",
                  "原始字幕_10_8本菲卡vs巴黎圣日耳曼.txt", "原始字幕_10_8欧塞尔vs布雷斯特.txt", "原始字幕_10_8科隆vs多特蒙德.txt",
                  "原始字幕_10_9兰斯vs巴黎圣日耳曼.txt", "原始字幕_10_9切尔西vs狼队.txt", "原始字幕_10_9多特蒙德vs拜仁慕尼黑.txt", "原始字幕_10_9美因茨vsRB莱比锡.txt"]
ref_file_names = ["转写后标注字幕_【厂家】10_8云达不莱梅VS门兴格拉德巴赫.txt", "转写后标注字幕_【厂家】10_8国际米兰vs巴塞罗那.txt", "转写后标注字幕_【厂家】10_8拜仁慕尼黑vs勒沃库森.txt",
                  "转写后标注字幕_【厂家】10_8本菲卡vs巴黎圣日耳曼.txt", "转写后标注字幕_【厂家】10_8欧塞尔vs布雷斯特.txt", "转写后标注字幕_【厂家】10_8科隆vs多特蒙德.txt",
                  "转写后标注字幕_【厂家】10_9兰斯vs巴黎圣日耳曼.txt", "转写后标注字幕_【厂家】10_9切尔西vs狼队.txt", "转写后标注字幕_【厂家】10_9多特蒙德vs拜仁慕尼黑.txt", "转写后标注字幕_【厂家】10_9美因茨vsRB莱比锡.txt"]
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

for asr_file_name,ref_file_name in zip(asr_file_names, ref_file_names):
    asr_file = codecs.open(os.path.join(corpus_root_dir, asr_file_name), 'r', 'utf-8')
    ref_file = codecs.open(os.path.join(corpus_root_dir, ref_file_name), 'r', 'utf-8')
    asr_lines = asr_file.readlines()
    ref_lines = ref_file.readlines()
    asr_objects = {}
    asr_objects["utts"] = {}
    fc_objects = {}
    fc_objects["utts"]={}
    for asr_line,ref_line in zip(asr_lines, ref_lines):
        asr_sentences = preprocess.normAndTokenize(asr_line,min_sentence_len=3,split_sentences=True)
        ref_sentences = preprocess.normAndTokenize(ref_line,min_sentence_len=3,split_sentences=True)
        if len(asr_sentences) != len(ref_sentences):
            continue
        for asr_sentence,ref_sentence in zip(asr_sentences, ref_sentences):
            if asr_sentence.find(":") != -1:
                continue
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




