# -*- coding: utf-8 -*-
import sys
import os.path
import codecs
import json
import requests
import bson
from requests import Session
from requests.adapters import HTTPAdapter
sys.path.append("..")
from scripts import preprocess


correctUrl = "http://10.194.92.118:18081/fast_correct"
#corpus_root_dir=r'C:\corpus\valid'
corpus_root_dir=r'.'
asr_file_names = ["【厂家】11_1纽卡斯联_asr.txt"]

session = Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.keep_alive = True
def fc_correct(text):
    headers = {'Content-Type': 'application/json'}
    body = {'text': text}
    body = json.dumps(body)
    resp = requests.request("POST", correctUrl, headers=headers, data=body, verify=False)
    resp_json = resp.json()
    if resp_json['result_code'] and "200" == resp_json['result_code']:
        corrections = resp_json['corrections']
        if len(corrections) == 1:
            return corrections[0]["fc_tokens"]
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
            fc_result_tokens = fc_correct("".join(asr_sentence.split()))
            output0 = {'rec_text': "".join(fc_result_tokens), 'rec_token': " ".join(fc_result_tokens),
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


