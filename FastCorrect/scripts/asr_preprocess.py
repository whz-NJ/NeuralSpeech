# -*- coding: utf-8 -*-
import os
import re
import codecs
import preprocess

# data_path = r'C:\工作任务\AIUI\NLP模型测试\刘旭明纠错'
# data_names = ['［世界杯］1_4决赛：乌拉圭VS法国_asr.txt']
# data_names = []
data_path = '/root/sports_corpus2'
data_names = ['train_noised_corpus.txt', 'valid_noised_corpus.txt', 'test_noised_corpus.txt']
def replace_func(input_file):
    input_file_dir = os.path.dirname(input_file)
    input_file_name = os.path.basename(input_file)
    output_file_path = os.path.join(input_file_dir, 'std_' + input_file_name)
    outfile = codecs.open(output_file_path, 'w', 'utf-8')

    with codecs.open(input_file, 'r', 'utf-8') as myfile:
        sentences = []
        for line in myfile:
            if len(line) == 0 or line.isspace():
                sentences.append("\n")
                continue
            fields = line.split('\t')
            if len(fields) == 2:
                orig_sentence = fields[0].replace(" ",  "")
                hypo_sentence = fields[1].replace(" ", "")
                sentences.append(preprocess.normAndTokenize4Ch(orig_sentence)[0] + '\t'
                                 + preprocess.normAndTokenize4Ch(hypo_sentence)[0] + '\n')
            else:
                normed_sentences = preprocess.normAndTokenize4Ch(fields[0].replace(" ",  ""),split_sentences=True)
                if normed_sentences and len(normed_sentences) > 0:
                    for sentence in normed_sentences:
                     sentences.append(sentence.replace(" ", "") + '\n')
            if len(sentences) >= 10000:
                outfile.writelines(sentences)
                sentences = []
        #文件扫描结束
        if len(sentences) > 0:
            outfile.writelines(sentences)
    outfile.close()


def run():
    #nonlocal data_names, data_path
    global data_names, data_path
    #处理各 ASR 输出文件
    if not data_names or len(data_names) == 0:
        data_names = []
        for root, dirs, files in os.walk(data_path):
            for file in files:
                if file.startswith("std_"):
                    continue
                data_names.append(file)
    for data_name in data_names:
        if data_name.startswith("std_") or not data_name.endswith(".txt"):
            continue
        replace_func(os.path.join(data_path, data_name))
        print('{0} has been processed !'.format(data_name))

if __name__ == '__main__':
    run()

