# -*- coding: utf-8 -*-
import os
import re
import codecs
import preprocess

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
    data_path = '../extracted/AA/'
    data_names = ['zh_wiki_00', 'zh_wiki_01', 'zh_wiki_02']
    # data_path = '../'
    # data_names = ['sports.txt']
    for data_name in data_names:
        replace_func(data_path + data_name)
        print('{0} has been processed !'.format(data_name))
    #记录词表
    with codecs.open(data_path + '/dict.CN_char.txt', 'w', 'utf-8') as dictfile:
        tokens = []
        for token in preprocess.g2pM_dict.keys():
            tokens.append(token+'\n')
            if len(tokens) > 10000:
                dictfile.writelines(tokens)
                tokens = []
        if len(tokens) > 0:
            dictfile.writelines(tokens)

if __name__ == '__main__':
    run()

