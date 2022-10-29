import os
import json
import codecs

asr_json_path=r'/root/std_noised_sports_corpus4/valid/data.json'
fc_json_path=r'/root/fastcorrect/models/finetune.ftb4/results_19_asr_b0_t0.0/valid/data.json'
MAX_CORPUS=15000

with codecs.open(asr_json_path, encoding="utf-8") as f:
    asr_json = json.load(f)

with codecs.open(fc_json_path, encoding="utf-8") as f:
    fc_json = json.load(f)

ks = asr_json["utts"].keys()

asr_json2 = {}
asr_json2["utts"] = {}
fc_json2 = {}
fc_json2["utts"] = {}

idx = 0
for k in ks:
    orig_text = asr_json["utts"][k]["output"][0]["text"].replace("<eos>","")
    asr_text = asr_json["utts"][k]["output"][0]["rec_text"].replace("<eos>","")
    fc_text = fc_json["utts"][k]["output"][0]["rec_text"].replace("<eos>","")

    orig_token = asr_json["utts"][k]["output"][0]["token"].replace("<eos>","")
    asr_token = asr_json["utts"][k]["output"][0]["rec_token"].replace("<eos>","")
    fc_token = fc_json["utts"][k]["output"][0]["rec_token"].replace("<eos>","")

    asr_item = {}
    asr_item["rec_text"] = asr_text
    asr_item["rec_token"] = asr_token
    asr_item["text"] = orig_text
    asr_item["token"] = orig_token
    asr_json2["utts"][k] = {}
    asr_json2["utts"][k]["output"] = [asr_item]

    fc_item = {}
    fc_item["rec_text"] = fc_text
    fc_item["rec_token"] = fc_token
    fc_item["text"] = orig_text
    fc_item["token"] = orig_token
    fc_json2["utts"][k] = {}
    fc_json2["utts"][k]["output"] = [fc_item]

    idx = idx + 1
    if idx >= MAX_CORPUS:
        break

with codecs.open("asr_data.json", mode="w", encoding="utf-8") as f:
    json_string = json.dumps(asr_json2, ensure_ascii=False, indent=2)
    f.write(json_string)

with codecs.open("fc_data.json", mode="w", encoding="utf-8") as f:
    json_string = json.dumps(fc_json2, ensure_ascii=False, indent=2)
    f.write(json_string)
