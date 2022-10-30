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
corpus_root_dir=r'C:\工作任务\AIUI\NLP模型测试\侯德成语料3'

ref_asr_file_names = ["10_28那不勒斯vs流浪者_asr.txt"]

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


for ref_asr_file_name in ref_asr_file_names:
    ref_asr_file = codecs.open(os.path.join(corpus_root_dir, ref_asr_file_name), 'r', 'utf-8')
    ref_asr_lines = ref_asr_file.readlines()

    asr_objects = {}
    asr_objects["utts"] = {}
    fc_objects = {}
    fc_objects["utts"]={}
    for ref_asr_line in ref_asr_lines:
        fields = ref_asr_line.split("\t")
        ref_line = fields[0]
        asr_line = fields[1]
        asr_sentences = preprocess.normAndTokenize(asr_line,min_sentence_len=3,split_sentences=True)
        ref_sentences = preprocess.normAndTokenize(ref_line,min_sentence_len=3,split_sentences=True)
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

    asr_json_file_name = "asr_" + ref_asr_file_name[0:-4] + ".json"
    fc_json_file_name = "fc_" + ref_asr_file_name[0:-4] + ".json"
    with open(os.path.join(corpus_root_dir, asr_json_file_name), "w", encoding='utf-8') as f:
        f.write(asr_string)
    with open(os.path.join(corpus_root_dir, fc_json_file_name), "w", encoding='utf-8') as f:
        f.write(fc_string)


