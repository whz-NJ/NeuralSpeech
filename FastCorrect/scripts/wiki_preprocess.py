# -*- coding: utf-8 -*-
import os
import re
import codecs

# removeMap = {}
# for ch in r'「『」』(\[（)\])\'"‘’“”':
#     removeMap[ch] = ch

digitMap = {}
digits='0123456789'
for digit in digits:
    if digit == '0':
        digitMap[digit] = '零'
    if digit == '1':
        digitMap[digit] = '一'
    if digit == '2':
        digitMap[digit] = '二'
    if digit == '3':
        digitMap[digit] = '三'
    if digit == '4':
        digitMap[digit] = '四'
    if digit == '5':
        digitMap[digit] = '五'
    if digit == '6':
        digitMap[digit] = '六'
    if digit == '7':
        digitMap[digit] = '七'
    if digit == '8':
        digitMap[digit] = '八'
    if digit == '9':
        digitMap[digit] = '九'

seperatorMap = {}
for ch in r'，。！？；：“”':
    seperatorMap[ch] = ch
keepMap = {}
for ch in r'+-*/,.?~:':
    keepMap[ch] = ch

def replace_func(input_file):
    input_file_dir = os.path.dirname(input_file)
    input_file_name = os.path.basename(input_file)
    outfile = codecs.open(input_file_dir + '/std_' + input_file_name, 'w', 'utf-8')
    with codecs.open(input_file, 'r', 'utf-8') as myfile:
        sentences = []
        for line in myfile:
            if r'<doc ' in line or r'</doc>' in line or r'<doc>' in line:
                continue
            digits = ''
            sentence = ''
            pre_ch = ''
            line2 = line[1:]
            for ch,next_ch in zip(line, line2):
                if seperatorMap.__contains__(ch): #句子分隔符
                    if len(digits) > 0:
                        sentence += digits
                        digits = ''
                    if len(sentence) >= 2:
                        sentences.append(sentence + "\n")
                        sentence = ""
                    else:
                        sentence = "" # 跳过过短的句子
                elif digitMap.__contains__(ch): #数字
                    # sentence += digitMap[ch]
                    digits += digitMap[ch]
                elif ch == '%' and len(digits) > 0:
                    digits = '百分之' + digits
                elif keepMap.__contains__(ch): #需要保留的符号
                    if ch == '.' and ('0' <= pre_ch and pre_ch <= '9') or ('0' <= next_ch and next_ch <= '9'):
                        digits += '点'
                    elif (ch == '.' or ch == ',' or ch == '?' or ch == ':') and '\u4e00' <= pre_ch <= '\u9fa5':
                        if len(digits) > 0:
                            sentence += digits
                            digits = ''
                        if len(sentence) >= 2: # 半角符号，此时把它当作句子分隔符
                            sentences.append(sentence + "\n")
                            sentence = ""
                    else: #保留符号
                        if len(digits) > 0:
                            sentence += digits
                            digits = ''
                        sentence += ch
                elif '\u4e00' <= ch <= '\u9fa5': #汉字
                    if len(digits) > 0:
                        sentence += digits
                        digits = ''
                    sentence += ch
                pre_ch = ch
            #一行扫描结束
            if len(digits) > 0:
                sentence += digits
            if len(sentence) > 0:
                sentences.append(sentence + "\n")
            if len(sentences) >= 1000: #内存中不能缓存太多句子
                outfile.writelines(sentences)
                sentences = []
        #文件扫描结束
        if len(sentences) > 0:
            outfile.writelines(sentences)
    outfile.close()


def run():
    # data_path = './extracted/AA/'
    # data_names = ['zh_wiki_00', 'zh_wiki_01', 'zh_wiki_02']
    data_path = '../'
    data_names = ['short_track.txt']
    for data_name in data_names:
        replace_func(data_path + data_name)
        print('{0} has been processed !'.format(data_name))


if __name__ == '__main__':
    run()

