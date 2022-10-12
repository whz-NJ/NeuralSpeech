# -*- coding: utf-8 -*-
import sys
import os.path
import codecs
import json
import requests
import bson
sys.path.append(r'/')
from scripts import preprocess
#import preprocess

correctUrl = "http://39.105.31.210:5051/fast_correct"
corpus_root_dir=r'C:\工作任务\AIUI\NLP模型测试\侯德成语料\比赛文本'
hypo_file_names=["原始字幕_9_18里昂vs巴黎圣日耳曼.txt", "原始字幕_9_18南特vs朗斯.txt", "原始字幕_厂家_9_18_埃弗顿vs西汉姆联.txt",
            "原始字幕_厂家_9_18皇家社会VS西班牙人.txt","原始字幕_厂家_9_18霍芬海姆vs弗赖堡.txt","原始字幕_厂家9_18罗马VS亚特兰大.txt",
            "原始字幕_厂家9_18蒙扎vs尤文图斯.txt"]
ref_file_names=["转写后标注字幕_9_18里昂vs巴黎圣日耳曼.txt", "转写后标注字幕_9_18南特vs朗斯.txt", "转写后标注字幕_厂家_9_18_埃弗顿vs西汉姆联.txt",
            "转写后标注字幕_厂家_9_18皇家社会VS西班牙人.txt","转写后标注字幕_厂家_9_18霍芬海姆vs弗赖堡.txt","转写后标注字幕_厂家9_18罗马VS亚特兰大.txt",
            "转写后标注字幕_厂家9_18蒙扎vs尤文图斯.txt"]

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

for hypo_file_name,ref_file_name in zip(hypo_file_names, ref_file_names):
    hypo_file = codecs.open(os.path.join(corpus_root_dir, hypo_file_name), 'r', 'utf-8')
    ref_file = codecs.open(os.path.join(corpus_root_dir, ref_file_name), 'r', 'utf-8')
    hypo_lines = hypo_file.readlines()
    ref_lines = ref_file.readlines()
    hypo_objects = {}
    hypo_objects["utts"] = {}
    fc_objects = {}
    fc_objects["utts"]={}
    for hypo_line,ref_line in zip(hypo_lines, ref_lines):
        hypo_sentences = preprocess.normAndTokenize(hypo_line,min_sentence_len=2,split_sentences=True)
        ref_sentences = preprocess.normAndTokenize(ref_line,min_sentence_len=2,split_sentences=True)
        if len(hypo_sentences) != len(ref_sentences):
            continue
        for hypo_sentence,ref_sentence in zip(hypo_sentences, ref_sentences):
            if hypo_sentence.find(":") != -1:
                continue
            fc_result = fc_correct("".join(hypo_sentence.split()))
            output0 = {'rec_text': fc_result, 'rec_token': " ".join(fc_result),
                       'text': "".join(ref_sentence),
                       'token': " ".join(ref_sentence)}
            id = str(bson.ObjectId())
            output1 = [output0]
            output = {'output': output1}
            fc_objects["utts"][id] = output

            output0 = {'rec_text': "".join(hypo_sentence.split()), 'rec_token': " ".join(hypo_sentence.split()),
                       'text': "".join(ref_sentence),
                       'token': " ".join(ref_sentence)}
            output1 = [output0]
            output = {'output': output1}
            hypo_objects["utts"][id] = output
    hypo_string = json.dumps(hypo_objects, ensure_ascii=False, indent=2)
    fc_string = json.dumps(fc_objects, ensure_ascii=False, indent=2)

    hypo_json_file_name = "hypo_" + hypo_file_name[0:-4] + ".json"
    fc_json_file_name = "fc_" + hypo_file_name[0:-4] + ".json"
    with open(os.path.join(corpus_root_dir, hypo_json_file_name), "w", encoding='utf-8') as f:
        f.write(hypo_string)
    with open(os.path.join(corpus_root_dir, fc_json_file_name), "w", encoding='utf-8') as f:
        f.write(fc_string)




