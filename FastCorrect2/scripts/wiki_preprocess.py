# -*- coding: utf-8 -*-
import os
import re
import codecs

# removeMap = {}
# for ch in r'「『」』(\[（)\])\'"‘’“”':
#     removeMap[ch] = ch

changeMap = {}
digits='0123456789'
for digit in digits:
    if digit == '0':
        changeMap[digit] = '零'
    if digit == '1':
        changeMap[digit] = '一'
    if digit == '2':
        changeMap[digit] = '二'
    if digit == '3':
        changeMap[digit] = '三'
    if digit == '4':
        changeMap[digit] = '四'
    if digit == '5':
        changeMap[digit] = '五'
    if digit == '6':
        changeMap[digit] = '六'
    if digit == '7':
        changeMap[digit] = '七'
    if digit == '8':
        changeMap[digit] = '八'
    if digit == '9':
        changeMap[digit] = '九'

seperatorMap = {}
for ch in r'，。！？；：':
    seperatorMap[ch] = ch
keepMap = {}
for ch in r'＋×÷+-*/,.?~:':
    keepMap[ch] = ch

punctuationMap = {}
for ch in r'＋×÷+-*/,.?:~，。！？；：':
    punctuationMap[ch] = ch

def replace_func(input_file):
    input_file_dir = os.path.dirname(input_file)
    input_file_name = os.path.basename(input_file)
    outfile = codecs.open(input_file_dir + '/std_' + input_file_name, 'w', 'utf-8')
    with codecs.open(input_file, 'r', 'utf-8') as myfile:
        sentences = []
        for line in myfile:
            if r'<doc ' in line or r'</doc>' in line or r'<doc>' in line:
                continue
            sentence = ''
            pre_ch = ''
            for ch in line:
                if seperatorMap.__contains__(ch):
                    if len(sentence) >= 1 and len(sentence) <= 4: #语句太短
                        sentence += ch
                    else:
                        sentence += ch
                        if len(sentence) > 1 or not punctuationMap.__contains__(sentence[0]):
                            sentences.append(sentence + "\n")
                            sentence = ""
                elif changeMap.__contains__(ch):
                    sentence += changeMap[ch]
                elif keepMap.__contains__(ch):
                    if (ch == '.' or ch == ',' or ch == '?' or ch == ':') and '\u4e00' <= pre_ch <= '\u9fa5':
                        if ch == '.':
                            sentence += '。'
                        elif ch == ',':
                            sentence += '，'
                        elif ch == '?':
                            sentence += '？'
                        elif ch == ':':
                            sentence += '：'
                    elif (ch == '+' or ch == '-' or ch == '*' or ch == '/' or ch == '＋' or ch=='×' or ch == '÷') \
                        and '0' <= pre_ch <= '9':
                        sentence += ch
                    else:
                        sentence += ch
                elif '\u4e00' <= ch <= '\u9fa5':
                    sentence += ch
                pre_ch = ch
            #一行扫描结束
            if len(sentence) > 0:
                if len(sentence) > 1 or not punctuationMap.__contains__(sentence[0]):
                    sentences.append(sentence + "\n")
            if len(sentences) >= 1000: #内存中不能缓存太多句子
                outfile.writelines(sentences)
                sentences = []
        #文件扫描结束
        if len(sentences) > 0:
            outfile.writelines(sentences)
    outfile.close()


def run():
    data_path = './extracted/AA/'
    data_names = ['zh_wiki_00', 'zh_wiki_01', 'zh_wiki_02']
    for data_name in data_names:
        replace_func(data_path + data_name)
        print('{0} has been processed !'.format(data_name))


if __name__ == '__main__':
    run()

