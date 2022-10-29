import os
import json
import codecs

json_dir=r'C:\工作任务\AIUI\NLP模型测试\侯德成语料2'
asr_json_file="asr_data.json"
fc_json_file="fc_data.json"

orig_txt_file="orig.txt"
asr_txt_file="asr.txt"
fc_txt_file="fc.txt"

asr_json_file_path = os.path.join(json_dir, asr_json_file)
with codecs.open(asr_json_file_path, encoding="utf-8") as f:
    asr_json = json.load(f)

fc_json_file_path = os.path.join(json_dir, fc_json_file)
with codecs.open(fc_json_file_path, encoding="utf-8") as f:
    fc_json = json.load(f)

orig_lines = []
asr_lines = []
fc_lines = []
ks = asr_json["utts"].keys()
for k in ks:
    orig = asr_json["utts"][k]["output"][0]["text"]
    asr= asr_json["utts"][k]["output"][0]["rec_text"]
    fc = fc_json["utts"][k]["output"][0]["rec_text"]
    orig_lines.append(orig+"\n")
    asr_lines.append(asr+"\n")
    fc_lines.append(fc+"\n")

orig_txt_file_path = os.path.join(json_dir, orig_txt_file)
with codecs.open(orig_txt_file_path, mode="w", encoding="utf-8") as f:
    f.writelines(orig_lines)
asr_txt_file_path = os.path.join(json_dir, asr_txt_file)
with codecs.open(asr_txt_file_path, mode="w", encoding="utf-8") as f:
    f.writelines(asr_lines)
fc_txt_file_path = os.path.join(json_dir, fc_txt_file)
with codecs.open(fc_txt_file_path, mode="w", encoding="utf-8") as f:
    f.writelines(fc_lines)
