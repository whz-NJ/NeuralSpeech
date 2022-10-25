import os
import codecs

input_file_dir = r'./'
input_file_names = [r'std_zh_wiki_00', r'std_zh_wiki_01', r'std_zh_wiki_02'] #output of wiki_preprocess.py
# input_file_dir = r'C:\Code\NeuralSpeech\FastCorrect'
# input_file_names = [r'std_wiki_cn.txt'] #output of wiki_preprocess.py
MAX_LINES_PER_FILE = 200000

for input_file_name in input_file_names:
    if not input_file_name.startswith("std_") or input_file_name.find("_sp") != -1: #必须是经过预处理后未分割的文件
        continue
    input_file_path = os.path.join(input_file_dir, input_file_name)
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        lines = []
        files_count = 0
        for line in infile.readlines():
            lines.append(line.strip() + "\n")
            if len(lines) >= MAX_LINES_PER_FILE:
                output_file_name = f"{input_file_name}_sp{files_count:03d}"
                with open(os.path.join(input_file_dir, output_file_name), 'w', encoding='utf-8') as output_file:
                    output_file.writelines(lines)
                lines = []
                files_count = files_count + 1
