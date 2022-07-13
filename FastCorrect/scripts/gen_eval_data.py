import sys
import json
import bson

# label_file_path=sys.argv[1]
# asr_result_file_path=sys.argv[2]
label_file_path="C:\\Code\\NeuralSpeech\FastCorrect\\label.txt"
asr_result_file_path="C:\\Code\\NeuralSpeech\\FastCorrect\\asc_result.txt"
eval_file_path="C:\\Code\\NeuralSpeech\\FastCorrect\\eval.txt"

label_file = open(label_file_path, 'r', encoding='UTF-8')
label_lines = []
for line in label_file:
    label_lines.append(line)
label_file.close()

asr_result_file = open(asr_result_file_path, 'r', encoding='UTF-8')
asr_result_lines = []
for line in asr_result_file:
    asr_result_lines.append(line)
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
result_string = json.dumps(result_object, ensure_ascii=False)

with open(eval_file_path, 'w', encoding='utf-8') as f:
    f.write(result_string)
