import os
import re

import bson
import json

input_file_dir = r'C:\工作任务\AIUI\NLP模型测试\BERT\足球2场'

asr_corpus_file_paths = []
bert_asr_corpus_file_paths = []

de_assist_chars = ['的', '地', '得']

for root, dirs, files in os.walk(input_file_dir):
    for file in files:
        file_path = os.path.join(root, file)
        if not file.endswith(".txt"):
            continue

        if file.startswith("bert_std_"):
            bert_asr_corpus_file_paths.append(file_path)
        elif file.startswith("std_"):
            asr_corpus_file_paths.append(file_path)

for asr_corpus_file_path in asr_corpus_file_paths:
    corpus_file_name = os.path.basename(asr_corpus_file_path).replace("std_", "").replace("_asr.txt", ".txt")
    corpus_file_path = os.path.join(input_file_dir, corpus_file_name)
    with open(asr_corpus_file_path, 'r', encoding='utf-8') as asr_file:
        asr_corpus_lines = asr_file.readlines()
    with open(corpus_file_path, 'r', encoding='utf-8') as asr_file:
        corpus_lines = asr_file.readlines()

    asr_tts_objects = {}
    for corpus_line, asr_corpus_line in zip(corpus_lines, asr_corpus_lines):
        label = corpus_line.replace('<void>', '').replace(' ', '').strip()
        asr_result0 = asr_corpus_line.replace('<void>', '').replace(' ', '').strip()
        if len(label) != len(asr_result0):
            continue

        asr_result = ""
        for label_char, asr_char in zip(label, asr_result0):
            if label_char in de_assist_chars and asr_char in de_assist_chars: #不考虑 的地得
                asr_result += label_char
            else:
                asr_result += asr_char

        tts_id = str(bson.ObjectId())
        output0 = {'rec_text': asr_result + '<eos>', 'rec_token': " ".join(asr_result) + ' <eos>', 'text': label,
                   'token': " ".join(label)}
        output1 = [output0]
        output = {'output': output1}
        asr_tts_objects[tts_id] = output
    result_object = {'utts': asr_tts_objects}

    result_string = json.dumps(result_object, ensure_ascii=False, indent = 2)
    data_file_name = os.path.basename(asr_corpus_file_path).replace(".txt", ".json")
    data_file_path = os.path.join(input_file_dir, data_file_name)
    with open(data_file_path, 'w', encoding='utf-8') as f:
        f.write(result_string)

error_pos_pattern = re.compile(r'(\*+)\(([^()]+)\)')
for bert_asr_corpus_file_paths in bert_asr_corpus_file_paths:
    corpus_file_name = os.path.basename(bert_asr_corpus_file_paths).replace("bert_std_", "").replace("_asr.txt", ".txt")
    corpus_file_path = os.path.join(input_file_dir, corpus_file_name)
    with open(bert_asr_corpus_file_paths, 'r', encoding='utf-8') as asr_file:
        bert_asr_corpus_lines = asr_file.readlines()
    with open(corpus_file_path, 'r', encoding='utf-8') as asr_file:
        corpus_lines = asr_file.readlines()

    asr_tts_objects = {}
    for corpus_line, bert_asr_corpus_line in zip(corpus_lines, bert_asr_corpus_lines):
        tts_id = str(bson.ObjectId())
        label = corpus_line.replace('<void>', '').replace(' ', '').strip()
        asr_result0 = bert_asr_corpus_line.replace('<void>', '').replace(' ', '').strip()
        asr_result = error_pos_pattern.sub(r'\2', asr_result0) #恢复为讯飞转写结果
        if len(label) != len(asr_result):
            continue

        bert_asr_result0 = error_pos_pattern.sub(r'\1', asr_result0) #将错误部分的讯飞转写结果用*代替
        bert_asr_result = ""
        idx = 0
        while idx < len(label):
            label_char = label[idx]
            asr_char = asr_result[idx]
            bert_char = bert_asr_result0[idx]
            if asr_char == label_char:
                if asr_char == bert_char: #转写/BERT和语料一致
                    bert_asr_result += asr_char
                    idx += 1
                elif bert_char == '*': #转写正确，BERT判断为错误
                    label_chars = str(label_char)
                    star_chars = '*'

                    idx += 1
                    if idx == len(label):
                        if asr_char in de_assist_chars and label_char in de_assist_chars:
                            bert_asr_result += label_char #不考虑 的地得
                        else:
                            bert_asr_result += '' # BERT误判为错误位置，这里DEL变高
                        break

                    de_find = False
                    if asr_char in de_assist_chars and label_char in de_assist_chars:
                        de_find = True
                    label_char = label[idx]
                    asr_char = asr_result[idx]
                    bert_char = bert_asr_result0[idx]
                    error_find = False
                    stars_num = 1 #BERT中连续星号的个数
                    while idx < len(label) and bert_char == '*': # 找后续连续的*
                        stars_num += 1
                        if label_char != asr_char:
                            error_find = True
                        label_chars += str(label_char)
                        star_chars += '*'

                        idx += 1
                        if idx == len(label):
                            break
                        label_char = label[idx]
                        asr_char = asr_result[idx]
                        bert_char = bert_asr_result0[idx]
                    if not error_find: #BERT误判的错误位置（实际讯飞转写正确）
                        if stars_num == 1 and de_find: #不考虑 的地得
                            bert_asr_result += label_char
                        else: # 讯飞转写，BERT认为全错
                            bert_asr_result += "" #这里会导致DEL变高(删除了正确的转写)，SUB不变（因为讯飞转写正确，不计入SUB）
                    else:
                        bert_asr_result += label_chars # 这里SUB值降低
                else:
                    raise ValueError("Unsupported condition!")
            else: #讯飞转写结果和原始语料不同（转写错误）
                if bert_char == '*': #BERT判断也是错误
                    bert_asr_result += str(label_char) #将原来的*替换为讯飞转写得到的字符 这里会导致SUB值降低，INS/DEL不变(字符数没变)
                else: #BERT未检测出错误
                    if label_char in de_assist_chars and asr_char in de_assist_chars: #不考虑 的地得
                        bert_asr_result += str(label_char)  # 将原来的*替换为语料字符
                    else:
                        bert_asr_result += str(asr_char) + '*' # 这里会导致INS值变大，SUB不变(保留了错误的转写)
                idx += 1

        output0 = {'rec_text': bert_asr_result + '<eos>', 'rec_token': " ".join(bert_asr_result) + ' <eos>', 'text': label,
                   'token': " ".join(label)}
        output1 = [output0]
        output = {'output': output1}
        asr_tts_objects[tts_id] = output
    result_object = {'utts': asr_tts_objects}

    result_string = json.dumps(result_object, ensure_ascii=False, indent = 2)
    data_file_name = os.path.basename(bert_asr_corpus_file_paths).replace(".txt", ".json")
    data_file_path = os.path.join(input_file_dir, data_file_name)
    with open(data_file_path, 'w', encoding='utf-8') as f:
        f.write(result_string)
