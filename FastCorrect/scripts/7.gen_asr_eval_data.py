import os.path
import sys
import json
import bson

# label_file_path=sys.argv[1]
# asr_result_file_path=sys.argv[2]
#label_file_path="/root/asr/test.zh_CN_tgt"
#asr_result_file_path="/root/asr/test.zh_CN"
#eval_file_path="/root/fastcorrect/asr_eval_data/test/data.json"
#label_file_path="/root/asr/valid.zh_CN_tgt"
#asr_result_file_path="/root/asr/valid.zh_CN"
#eval_file_path="/root/fastcorrect/asr_eval_data/dev/data.json"
#label_file_path="/root/sports_corpus2/test/test.zh_CN_tgt"
#asr_result_file_path="/root/sports_corpus2/test/test.zh_CN"
#eval_file_path="/root/sports_corpus2/test/data.json"
#label_file_path="/root/sports_corpus2/valid/valid.zh_CN_tgt"
#asr_result_file_path="/root/sports_corpus2/valid/valid.zh_CN"
#eval_file_path="/root/sports_corpus2/valid/data.json"

label_file_path="/root/std_ftb_sports_corpus_en/test.zh_CN_tgt"
asr_result_file_path="/root/std_ftb_sports_corpus_en/test.zh_CN"
eval_file_path="/root/std_ftb_sports_corpus_en/test/data.json"

label_file = open(label_file_path, 'r', encoding='UTF-8')
label_lines = []
for line in label_file:
    label_lines.append(line.replace(" ", ""))
label_file.close()

asr_result_file = open(asr_result_file_path, 'r', encoding='UTF-8')
asr_result_lines = []
for line in asr_result_file:
    asr_result_lines.append(line.split(" |||| ")[0].replace(" ", ""))
asr_result_file.close()

tts_objects = {}
for label0, asr_result0 in zip(label_lines, asr_result_lines):
    tts_id = str(bson.ObjectId())
    label = label0.replace('<void>', '').replace(' ', '').strip()
    asr_result = asr_result0.replace('<void>', '').replace(' ', '').strip()
    output0 = {}
    output0['rec_text'] = asr_result + '<eos>';
    output0['rec_token'] = " ".join(asr_result) + ' <eos>'
    output0['text'] = label
    output0['token'] = " ".join(label)
    output1 = []
    output1.append(output0)
    output = {}
    output['output'] = output1
    tts_objects[tts_id] = output
result_object = {}
result_object['utts'] = tts_objects
result_string = json.dumps(result_object, ensure_ascii=False, indent = 2)

eval_file_dir = os.path.dirname(eval_file_path)
if not os.path.isdir(eval_file_dir):
    os.makedirs(eval_file_dir)
with open(eval_file_path, 'w', encoding='utf-8') as f:
    f.write(result_string)

