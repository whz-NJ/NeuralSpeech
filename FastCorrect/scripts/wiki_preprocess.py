# -*- coding: utf-8 -*-
import os
import re
import codecs
import preprocess

# data_path = '../'
# data_names = ['sports.txt']
data_path = '../extracted/AA/'
data_names = ['zh_wiki_00', 'zh_wiki_01', 'zh_wiki_02']
def replace_func(input_file):
    input_file_dir = os.path.dirname(input_file)
    input_file_name = os.path.basename(input_file)
    outfile = codecs.open(input_file_dir + '/std_' + input_file_name, 'w', 'utf-8')

    with codecs.open(input_file, 'r', 'utf-8') as myfile:
        sentences = []
        for line in myfile:
            if r'<doc ' in line or r'</doc>' in line or r'<doc>' in line:
                continue
            sentences.extend([sentence + '\n' for sentence in preprocess.normAndTokenize(line, split_sentences=True)])
            if len(sentences) >= 10000:
                outfile.writelines(sentences)
                sentences = []
        #文件扫描结束
        if len(sentences) > 0:
            outfile.writelines(sentences)
    outfile.close()


def run():
    for data_name in data_names:
        replace_func(data_path + data_name)
        print('{0} has been processed !'.format(data_name))
    #记录词表
    MAX_TOKENS = 40000
    with codecs.open(data_path + '/dict.CN_char.txt', 'w', 'utf-8') as dictfile:
        sorted_token_counts = sorted(preprocess.tokens_count_dict.items(), key= lambda  x:x[1], reverse=True)
        tokens = []
        count = 0
        for token_count in sorted_token_counts:
            tokens.append(token_count[0] + " " + str(token_count[1]) +'\n')
            if len(tokens) > 10000:
                dictfile.writelines(tokens)
                tokens = []
            count += 1
            if count >= MAX_TOKENS:
                break
        if len(tokens) > 0:
            dictfile.writelines(tokens)

if __name__ == '__main__':
    run()

