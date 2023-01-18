# -*- coding: utf-8 -*-
import cn2an
import re
from g2pM import G2pM
import zhconv

digit_map = {}
digit_map['0'] = '零'
digit_map['1'] = '一'
digit_map['2'] = '二'
digit_map['3'] = '三'
digit_map['4'] = '四'
digit_map['5'] = '五'
digit_map['6'] = '六'
digit_map['7'] = '七'
digit_map['8'] = '八'
digit_map['9'] = '九'
digit_map['.'] = '点'
digit_map['+'] = '正'
digit_map['-'] = '负'

cn_digit_map = {}
cn_digit_map['零'] = '0'
cn_digit_map['一'] = '1'
cn_digit_map['二'] = '2'
cn_digit_map['三'] = '3'
cn_digit_map['四'] = '4'
cn_digit_map['五'] = '5'
cn_digit_map['六'] = '6'
cn_digit_map['七'] = '7'
cn_digit_map['八'] = '8'
cn_digit_map['九'] = '9'
cn_digit_map['点'] = '.'
cn_digit_map['十'] = ''
cn_digit_map['百'] = ''
cn_digit_map['千'] = ''
cn_digit_map['万'] = ''
cn_digit_map['亿'] = ''

mark_cn_map = {}
mark_cn_map['+'] = '加'
mark_cn_map['-'] = '至'
mark_cn_map['~'] = '至'
mark_cn_map['×'] = '乘以'
mark_cn_map['*'] = '乘以'
mark_cn_map['÷'] = '除以'
mark_cn_map['/'] = '除以'
mark_cn_map['='] = '等于'
mark_cn_map[':'] = '比'

# def str_to_digits(str):
#     digits = ''
#     for ch in str:
#         digit = digit_map.get(ch)
#         if digit:
#             digits += digit
#     return digits

# def my_an2cn(digitsStr, verbatim):
#     if len(digitsStr) == 0:
#         return ''
#     sign = digitsStr[0]
#     if sign == '+' or sign == '-':
#         if sign == '+':
#             sign = '正'
#         else:
#             sign = '负'
#         verbatim = False
#         digitsStr = digitsStr[1:]
#     else:
#         sign = ""
#     if verbatim or digitsStr[0] == '.' or digitsStr.count('.') > 1 or len(digitsStr) > 7:
#         return sign + str_to_digits(digitsStr), False
#     try:
#         return sign + cn2an.an2cn(digitsStr, mode='low'), True
#     except Exception as e:
#         return sign + str_to_digits(digitsStr), False

seperator_map = {}
for ch in r'<>。！!？?;；()（）[]【】{}「」—，,：':
    seperator_map[ch] = ch
kept_char_map = {}
for ch in r"%@.*+-=/×÷~&、·':<>":
    kept_char_map[ch] = ch

def Q2B_F2J(uchar):
    """全角转半角/繁体转简体"""

    if uchar in kept_char_map or uchar in seperator_map:
        return uchar

    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
        return zhconv.convert(uchar, 'zh-hans')
    return zhconv.convert(chr(inside_code), 'zh-hans')

def unify_pinyin(pinyin):
    py = pinyin
    if len(pinyin) >= 2:
        prefix = pinyin[:2]
        if prefix == "zh" or prefix == 'ch' or prefix == 'sh':
            py = prefix[:1] + pinyin[2:]
    if py[0] == 'n' and len(py) > 1:
        py = 'l' + py[1:]
    if len(py) >= 3:
        postfix = py[-3:]
        if postfix == "ang" or postfix == 'eng' or postfix == 'ing':
            py = py[:-3] + postfix[:2]
    return py

model = G2pM()
g2pM_dict = {}
tokens_count_dict = {}
# %@.:+-=/×÷~&
# 单音节的特殊符号和汉字读音可以通过模型互转，不处理（语料是什么就是什么）
# 多音节的特殊符号%的汉字恢复为原始特殊符号
# :既可能读做 比 也可能读做 点
# 当两段比较文字中特殊字符不一致时，通过模糊拼音对齐
for digit in digit_map.keys():
    g2pM_dict[digit] = unify_pinyin(''.join(model(digit_map[digit], tone=False, char_split=True)))

# en_cn_map = {}
# with open("noised_English.txt", 'r', encoding='utf-8') as infile:
#     for line in infile.readlines():
#         fields = line.split("\t")
#         if len(fields) != 2:
#             continue
#         en = fields[0].strip()
#         cn = fields[1].strip()
#         if len(en) > 0 and len(cn) > 0:
#             en_cn_map[en] = cn
#
# def en2cn(english_word):
#     length = len(english_word)
#     if length == 0:
#         return []
#
#     if length == 1:
#         return [en_cn_map[english_word[0]]]
#     elif length == 2:
#         return [en_cn_map[english_word[0]], en_cn_map[english_word[1]]]
#     else:
#         return [en_cn_map[english_word[0]], en_cn_map[english_word[int(length/2)]], en_cn_map[english_word[-1]]]

#提取阿拉伯数字并转换为中文数字
# def extract_digits2cn(line, prev_ch, is_time, tokens, start_index=0):
#     def extract_digits(line, start_index):
#         an_digits = ""
#         digits_count = 0
#         is_float = False
#         idx = start_index
#         is_normal_digits = True
#         dot_count = 0
#         while idx < len(line):
#             ch = Q2B_F2J(line[idx])
#             if '0' <= ch <= '9':
#                 an_digits += ch
#                 digits_count += 1
#                 idx += 1
#             elif ch == '.':
#                 an_digits += ch
#                 dot_count += 1
#                 if digits_count > 0 and dot_count == 1:
#                     is_float = True
#                 else:
#                     is_float = False
#                     is_normal_digits = False
#                 idx += 1
#             else:
#                 break
#         if an_digits.endswith('.'):
#             is_float = False
#             is_normal_digits = False
#         return an_digits, idx-start_index, digits_count, is_float, is_normal_digits
#
#     def peek_next_ch(line, start_index):
#         idx = start_index
#         while idx < len(line):
#             ch = line[idx]
#             if ch == ' ' or ch == '\t' or ch == '\r' or ch == '\n':
#                 idx += 1
#             else:
#                 ch = Q2B_F2J(ch)
#                 return ch, idx - start_index
#         return "", 0
#
#     def show_in_verbatim(prev_ch, an_digits, line, idx):
#         next_ch, blank_count = peek_next_ch(line, idx)
#         if '在' == prev_ch:
#             if next_ch == '年':  # 在22年的世界杯上
#                 return True, next_ch, blank_count
#         elif next_ch == '年':
#             if (len(an_digits) == 4) and (an_digits.startswith("19") or not an_digits.startswith("200")):
#                 return True, next_ch, blank_count
#         if next_ch == '赛':
#             next_next_ch, blank_count = peek_next_ch(line, idx + 1)
#             if next_next_ch == '季':
#                 return True, next_ch, blank_count
#         return False, next_ch, blank_count
#
#     sign = ""
#     digits_tokens = []
#     idx = start_index
#     if idx == len(line):
#         return 0
#
#     ch = Q2B_F2J(line[idx])
#     if ch == '-' or ch == '+':
#         prev_ch = ch
#         if (idx+1) < len(line):
#             next_ch = Q2B_F2J(line[idx + 1])
#             if not '0' <= next_ch <= '9':
#                 return 1 #丢弃这个+/-号
#         sign = ch
#         idx += 1
#     an_digits0, chars_count0, digits_count0, is_float0, is_normal_digits = extract_digits(line, idx)
#     idx += chars_count0
#     if digits_count0 > 0:
#         in_verbatim, next_ch, blank_count = show_in_verbatim(prev_ch, an_digits0, line, idx)
#         idx += blank_count
#         if is_normal_digits and not in_verbatim and idx < len(line):
#             ch = next_ch
#             if ch == '%':
#                 idx += 1
#                 digits_tokens.extend(list("百分之"))
#                 cn_digits0, is_normal_digits = my_an2cn(sign+an_digits0, False)
#                 for ch in list(cn_digits0):
#                     digits_tokens.append(ch)
#             elif mark_cn_map.__contains__(ch):
#                 idx += 1
#                 next_ch, blank_count = peek_next_ch(line, idx)
#                 idx += blank_count
#                 if '0' <= next_ch <= '9':
#                     an_digits1, chars_count1, digits_count1, is_float1,is_normal_digits = extract_digits(line, idx)
#                     idx += chars_count1
#                     if not is_normal_digits:
#                         cn_digits0, is_normal_digits = my_an2cn(sign+an_digits0, False) #第一串数字是有效的数值
#                         cn_digits1, is_normal_digits = my_an2cn(an_digits1, True) #第二串数字不是有效的数值
#                         for ch in list(cn_digits0 + cn_digits1): #不认识的字符不放入 tokens
#                             tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
#                             digits_tokens.append(ch)
#                         tokens.extend(digits_tokens)
#                         return idx - start_index
#                     if not is_float0 and not is_float1 and (ch == '/' or ch == ':' or ch == "-" or ch == "~"):
#                         if ch == "/":
#                             cn_digits0, is_normal_digits = my_an2cn(sign+an_digits0, False)
#                             cn_digits1, is_normal_digits = my_an2cn(an_digits1, False)
#                             for ch in list(cn_digits1):
#                                 digits_tokens.append(ch)
#                             digits_tokens.extend(list("分之"))
#                             for ch in list(cn_digits0):
#                                 digits_tokens.append(ch)
#                         elif (ch == '-' or ch  == '~'):
#                             next_ch, blank_count = peek_next_ch(line, idx)
#                             next_next_ch, blank_count = peek_next_ch(line, idx+blank_count+1)
#                             if next_ch == '年' or (next_ch == '赛' and next_next_ch == '季'):
#                                 cn_digits0, is_normal_digits = my_an2cn(an_digits0, True)
#                                 cn_digits1, is_normal_digits = my_an2cn(an_digits1, True)
#                                 for ch in list(cn_digits0):
#                                     digits_tokens.append(ch)
#                                 digits_tokens.append("至")
#                                 for ch in list(cn_digits1):
#                                     digits_tokens.append(ch)
#                         else:
#                             cn_digits0, is_normal_digits = my_an2cn(an_digits0, False)
#                             cn_digits1, is_normal_digits = my_an2cn(an_digits1, False)
#                             for ch in list(cn_digits0):
#                                 digits_tokens.append(ch)
#                             if is_time:
#                                 digits_tokens.append("点")
#                             else:
#                                 digits_tokens.append("比")
#                             for ch in list(cn_digits1):
#                                 digits_tokens.append(ch)
#                     else:
#                         cn_digits0, is_normal_digits = my_an2cn(sign+an_digits0, False)
#                         cn_digits1, is_normal_digits = my_an2cn(an_digits1, False)
#                         ch0 = ch
#                         for ch in list(cn_digits0):
#                             digits_tokens.append(ch)
#                         digits_tokens.extend(list(mark_cn_map[ch0]))
#                         for ch in list(cn_digits1):
#                             digits_tokens.append(ch)
#                 else: #非数字、符号token本方法不处理
#                     cn_digits0, is_normal_digits = my_an2cn(sign + an_digits0, False)
#                     for ch in list(cn_digits0):
#                         digits_tokens.append(ch)
#             elif '0' <= ch <= '9':
#                 an_digits1, chars_count1, digits_count1, is_float1, is_normal_digits = extract_digits(line, idx)
#                 idx += chars_count1
#                 in_verbatim, next_ch, blank_count = show_in_verbatim(prev_ch, an_digits1, line, idx)
#                 idx += blank_count
#                 cn_digits0, is_normal_digits = my_an2cn(sign+an_digits0, in_verbatim)
#                 cn_digits1, is_normal_digits = my_an2cn(an_digits1, in_verbatim)
#                 for ch in list(cn_digits0):
#                     digits_tokens.append(ch)
#                 for ch in list(cn_digits1):
#                     digits_tokens.append(ch)
#             else: #非数字、符号token本方法不处理
#                 cn_digits0, is_normal_digits = my_an2cn(sign + an_digits0, False)
#                 for ch in list(cn_digits0):
#                     digits_tokens.append(ch)
#         else:
#             cn_digits0, is_normal_digits = my_an2cn(sign + an_digits0, in_verbatim)
#             for ch in list(cn_digits0):
#                 digits_tokens.append(ch)
#
#         for ch in digits_tokens:
#             tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
#         tokens.extend(digits_tokens)
#     return idx - start_index

#将中文数字转换为阿拉伯数字
def my_cn2an(cnDigitsStr):
    cnDigits = cnDigitsStr.split('点')
    result = ""
    for cnDigit in cnDigits:
        if len(cnDigit) > 0:
            if len(cnDigit) > 1 or (cnDigit != '十' and cnDigit != '百' and cnDigit != '千' and cnDigit != '万' and cnDigit != '亿'):
                try:
                    result += str(cn2an.cn2an(cnDigit, mode='smart')) + "."
                except: #可能是两串中文数字连在一起导致
                    for idx in range(1, len(cnDigit)):
                        cnDigit1 = cnDigit[0: idx]
                        cnDigit2 = cnDigit[idx:]
                        result1 = None
                        result2 = None
                        try:
                            result1 = cn2an.cn2an(cnDigit1, mode='smart')
                            result2 = cn2an.cn2an(cnDigit2, mode='smart')
                        except:
                            if result1 and result2:
                                break #前面已经找到最合适的分词位置，不需要继续找了
                            result1 = None
                            result2 = None
                            continue
                    if result1 == None or result2 == None:
                        return ""
                    else:
                        result += str(result1) + str(result2) + "."
            else:#十分之 百分之 千分之 万分之 亿分之 中的 十/百/千/万/亿
                result += str(cn2an.cn2an('一' + cnDigit, mode='smart')) + "."
    if not cnDigitsStr.endswith('点'):
        result = result[0:-1] #删除for循环中固定加的.
    if cnDigitsStr.startswith('点'):
        result = '.' + result
    return result
#my_cn2an("十零")
#提取中文数字
def extract_cn_digits(line, tokens, start_index=0, cn_to_an = False):
    digits_count = 0
    cn_digits = ""
    an_digits = ""
    idx = start_index
    if idx == len(line):
        return -1
    ch = Q2B_F2J(line[idx])
    if ch == '负':
        if cn_to_an:
            an_digits += "-"
        else:
            cn_digits += ch
        idx += 1
        digits_count += 1
    elif ch == '正':
        if cn_to_an:
            an_digits = "+" #因为cn2an不支持 '正三十五' 这种格式字符串，所以这里手工将'正'变成'+'
        else:
            cn_digits += ch
        idx += 1
        digits_count += 1

    while idx < len(line):
        ch = Q2B_F2J(line[idx])
        if cn_digit_map.__contains__(ch):
            cn_digits += ch
            digits_count += 1
            idx += 1
        else:
            break
    ending_ch = ""
    if idx < len(line):
        ending_ch = Q2B_F2J(line[idx])

    if not cn_to_an:
        if ending_ch == '多' or ending_ch == '几':
            # 因为cn_to_an为false，不需要调用cn2an模块，可以直接在后面加cn2an不支持的'多'
            cn_digits += ending_ch
            digits_count += 1
        for digit in cn_digits:
            tokens.append(digit)
            tokens_count_dict[digit] = tokens_count_dict.get(digit, 0) + 1
    else: #需要把中文数字转换为阿拉伯数字
        mid_an_digits = my_cn2an(cn_digits)
        if not mid_an_digits or len(mid_an_digits) == 0:
            return -1
        an_digits += mid_an_digits
        for digit in an_digits:
            tokens.append(digit)
            tokens_count_dict[digit] = tokens_count_dict.get(digit, 0) + 1
            # digits_count += 1
        if ending_ch == '多' or ending_ch == '几':
            tokens.append('+')
            tokens_count_dict['+'] = tokens_count_dict.get('+', 0) + 1
            digits_count += 1
    return digits_count

#拆成独立发音的 tokens
def normAndTokenize(line, min_sentence_len=2, split_sentences=False, drop_seperator=False):
    sentences = []
    def append_english_digits(append_english=False, append_digits=False, append_cn_digits=False, cn_to_an = False):
        nonlocal tokens, english, digits, cn_digits
        if append_english and len(english) > 0:
            if len(english) > 1:
                if english.upper() != english: #如果单词不是全大写，则转为全小写（统一）
                    english = english.lower()
            else: # 如果是字母，统一用大写
                english = english.upper()
            tokens.append(english)
            tokens_count_dict[english] = tokens_count_dict.get(english, 0) + 1
            english = ''
        if append_digits and len(digits) > 0: #数字分开(否则词典太大)
            for digit in digits:
                tokens.append(digit)
                tokens_count_dict[digit] = tokens_count_dict.get(digit, 0) + 1
            digits = ''
        if append_cn_digits and len(cn_digits) > 0:
            if not cn_to_an:
                for digit in cn_digits:
                    tokens.append(digit)
                    tokens_count_dict[digit] = tokens_count_dict.get(digit, 0) + 1
            else:
                an_digits = my_cn2an(cn_digits)
                if not an_digits or len(an_digits) == 0:
                    return False
                for digit in an_digits: #将中文数字转换为阿拉伯数字
                    tokens.append(digit)
                    tokens_count_dict[digit] = tokens_count_dict.get(digit, 0) + 1
            cn_digits = ''

        return True

    tokens = []
    english = ''
    digits = ''
    cn_digits = ''
    prev_ch = ''
    line = line.strip()
    idx = 0
    while idx < len(line):
        ch = Q2B_F2J(line[idx])
        if ch == '°':
            append_english_digits(True, True, True, True)  # 如果有中文数字，转换为阿拉伯数字
            tokens.append(ch)
            tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
        if idx < (len(line)-1):
            next_ch = Q2B_F2J(line[idx+1])
            if (ch == '°') and (next_ch == 'C' or next_ch == 'c'):
                tokens.append('C')
                tokens_count_dict['C'] = tokens_count_dict.get('C', 0) + 1
                prev_ch = ch
                idx += 2  # 跳过下一个字符
                continue
            # 将中文摄氏度统一转换为°C，如果是单独的度，就不转换为°了，让模型自己转换
            elif ch == '摄' and next_ch == '氏' and idx < (len(line)-2):
                next_next_ch = Q2B_F2J(line[idx+2])
                if next_next_ch == '度':
                    if append_english_digits(True, True, True, True): #如果有中文数字，转换为阿拉伯数字
                        tokens.append('°')
                        tokens.append('C')
                        tokens_count_dict['°'] = tokens_count_dict.get('°', 0) + 1
                        tokens_count_dict['C'] = tokens_count_dict.get('C', 0) + 1
                        prev_ch = '度'
                        idx += 3  # 跳过下两个字符
                    else: #中文数字无法转换为阿拉伯数字
                        append_english_digits(False, False, True) #中文数字无法转换为对应阿拉伯数字，保留为中文数字
                        tokens.append(ch)
                        tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
                        prev_ch = ch
                        idx += 1
                    continue
        else:
            next_ch = ''

        if seperator_map.__contains__(ch): #句子分隔符
            append_english_digits(True, True, True) #如果有中文数字，保持原样，不转换为阿拉伯数字
            if not split_sentences: #不分句（处理ASR输出或强制纠错规则时）
                prev_ch = ch
                if not drop_seperator:
                    tokens.append(ch)  # 将分句的标点符号保存下来
                idx = idx + 1  # 丢弃，跳到下一个字符
                continue
            if len(tokens) >= min_sentence_len: # 分句且当前句子token数满足要求
                sentences.append(" ".join(tokens)) # 每个token中间用空格分隔
            tokens = []
        elif '0' <= ch <= '9': #数字
            append_english_digits(append_english=True, append_cn_digits=True) #如果有中文数字，保持原样，不转换为阿拉伯数字
            digits += ch
        # '%@.:+-=/\'×÷~&':
        elif kept_char_map.__contains__(ch): #需要保留的符号
            if(ch != '.') or not (('0' <= prev_ch <= '9') or ('0' <= next_ch <= '9')):
                append_english_digits(True, True, True) #如果有中文数字，保持原样，不转换为阿拉伯数字
                tokens.append(ch) # 不在数字中间的点作为独立的 token
                tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
            else:
                append_english_digits(append_english=True, append_cn_digits=True) #如果有中文数字，保持原样，不转换为阿拉伯数字
                digits += ch # 阿拉伯数字中的点号
        # elif '\u4e00' <= ch <= '\u9fa5' or '\u3400' <= ch <= '\u4DB5': #汉字
        elif '\u4e00' <= ch <= '\u9fa5' or '\u3400' <= ch <= '\u4DB5':  # 汉字
            if ch != '分' and ch != '比' and not cn_digit_map.__contains__(ch):
                append_english_digits(True, True, True) # 当前汉字为普通的汉字。前面如果有中文数字，保持原样，不转换为阿拉伯数字
                tokens.append(ch)
                tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
            elif ch == '分':
                if next_ch == '之':
                    if cn_digit_map.__contains__(prev_ch):
                        # 中文读比例数字时，分子在后面读，而阿拉伯数字表示比例，分子在前面
                        # 这里先提取阿拉伯数字表示法中需要的分子
                        digits_num = extract_cn_digits(line, tokens, idx + 2, True)
                        if digits_num == -1: #未提取到分子，此时不应该转换为阿拉伯数字
                            append_english_digits(True, True, True)  # 中文数字保持原样，不转换为阿拉伯数字
                            tokens.append(ch)
                            tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
                        else:
                            #再提取阿拉伯数字中的比例符号
                            if prev_ch == '百' and cn_digits == '百':
                                cn_digits = '' #把前面的汉字数字清空，因为比例符号包含了
                                append_english_digits(append_english=True, append_digits=True)
                                tokens.append('%')
                                tokens_count_dict['%'] = tokens_count_dict.get('%', 0) + 1
                            else:
                                # 提取分子（前面 extract_cn_digits(line, tokens, idx + 2, True) 已经把分子保存在 digits 里了）
                                append_english_digits(append_english=True, append_digits=True)
                                tokens.append('/')
                                tokens_count_dict['/'] = tokens_count_dict.get('/', 0) + 1
                                # 提取分母（前面已经把分母保存在 cn_digits 里了）
                                append_english_digits(append_cn_digits=True, cn_to_an=True)
                        idx += digits_num + 2
                        prev_ch = ''
                        continue
                    else: #不是比例数字
                        append_english_digits(True, True, True) #中文数字保持原样，不转换为阿拉伯数字
                        tokens.append(ch)
                        tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
                else:
                    append_english_digits(True, True, True) #中文数字保持原样，不转换为阿拉伯数字
                    tokens.append(ch)
                    tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
            elif ch == '比':
                if len(cn_digits) > 0 and prev_ch in cn_digit_map and next_ch in cn_digit_map:
                    digits1 = []
                    #先提取第一个数
                    extract_cn_digits(cn_digits, digits1, 0, False)
                    #再提取第二个数
                    digits2 = []
                    digits_num = extract_cn_digits(line, digits2, idx+1, False)
                    idx += (1+digits_num)
                    next_next_ch = ""
                    if idx < len(line):
                        next_next_ch = Q2B_F2J(line[idx])
                    # 是比分格式
                    if next_next_ch != '大' and next_next_ch != '小' and next_next_ch != '多' and next_next_ch != '少':
                        tokens.extend([d for d in my_cn2an("".join(digits1))])
                        tokens.append(":")
                        tokens_count_dict[':'] = tokens_count_dict.get(':', 0) + 1
                        tokens.extend([d for d in my_cn2an("".join(digits2))])
                    else: #不是比分格式
                        tokens.extend(digits1)
                        tokens.append("比")
                        tokens_count_dict['比'] = tokens_count_dict.get('比', 0) + 1
                        tokens.extend(digits2)
                    cn_digits = ""
                    prev_ch = digits2[-1]
                    continue
                else:
                    append_english_digits(True, True, True)  # 中文数字保持原样，不转换为阿拉伯数字
                    tokens.append(ch)
                    tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
            else: #ch 是中文数字或汉字点
                cn_digits += ch
        elif ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'): #英文
            append_english_digits(append_digits=True, append_cn_digits=True) #中文数字保持原样，不转换为阿拉伯数字
            english += ch
        elif ch == ' ' or ch == "\t":
            append_english_digits(True, True, True) #跳过语料中的空格（函数结束前统一加空格作为各token分隔符），中文数字保持原样，不转换为阿拉伯数字
        prev_ch = ch
        idx = idx + 1
    #一行扫描结束
    append_english_digits(True, True, True) #中文数字保持原样，不转换为阿拉伯数字
    if len(tokens) >= min_sentence_len:  # 分句且当前句子token数满足要求
        sentences.append(" ".join(tokens))
    return sentences


def main():
    # print(normAndTokenize("朋友们，随着主裁判韦伯的一声哨响，二零一四年巴西世界杯小组赛C组第二轮，",
    #                       keep_sep_chars=True, split_sentences=False))
    # print(normAndTokenize("现在时间是03:50，比分是3:5", keep_sep_chars=True, split_sentences=False))

    print(normAndTokenize("四十比三十八大二"))
    print(normAndTokenize("四十比三十八"))
    print(normAndTokenize("在2022年世界杯上"))
    print(normAndTokenize("现在时间是03:50，比分是3:5"))
    print(normAndTokenize("22 23赛季"))
    print(normAndTokenize("12 13 年毕业"))
    print(normAndTokenize("2012-13年"))
    print(normAndTokenize("七十六°C 的样子"))
    print(normAndTokenize("六°的样子"))
    print(normAndTokenize("中国三分之二人口"))
    print(normAndTokenize("在20 22年世界杯上"))
    print(normAndTokenize("02 :  00封诺丁汉02%%03%"))
    print(normAndTokenize("1998年春"))
    print(normAndTokenize("2002年春"))
    print(normAndTokenize("2012年春"))

    # print(normAndTokenize("现 在 + C B A 赛 事 转 播"))
    # print(normAndTokenize("= 6"))
    #print(normAndTokenize("3.5 / 3.5.4"))
    #print(normAndTokenize("比例1.5% 3/5 3.5/5"))
    print(normAndTokenize("迈克尔SHOW了一把"))
    print(normAndTokenize("时间03:50"))

    # print(normAndTokenize("你好。，好。。在吗", min_sentence_len=2, split_sentences=True))
    # print(normAndTokenize("啊迈克尔SHOW了一把脚下火？你好，在吗", split_sentences=True))
    # print(normAndTokenize("啊迈克尔SHOW了一把脚下火？你好，在吗"))
    # print(normAndTokenize("\u597d\u6c42"))
    # print(normAndTokenize("好求，乌拉归进求啦！"))
    # print(normAndTokenize("二点三零点四"))
    # print(normAndTokenize("就是正在为你书看呢2:8，克罗斯世界杯A组第3轮的比赛", split_sentences=False))
    # print(normAndTokenize("现在时间是9:20，开始9:30", split_sentences=True))
    # print(normAndTokenize("现在时间是9:20，开始时间9:30", split_sentences=True))
    # print(normAndTokenize("9:20"))
    # print(normAndTokenize("现在比分是9:20"))
    # print(normAndTokenize("职业生涯CBA的第3场比赛"))
    # print(normAndTokenize("21.34"))

    print(normAndTokenize("现 在 C B A 赛 事 转 播"))
    # print(normAndTokenize("现在CBA赛事转播"))
    print(normAndTokenize("比例是百分之三十点三"))
    print(normAndTokenize('我们1/23的人abc30%的概率，59.2÷37=32.5-35.3=0')[0])
    #
    print(normAndTokenize("版本号是V二点三零点四"))
    print(normAndTokenize("版本号是V二点三零点四"))
    print(normAndTokenize("百分之七十六七十九点八啊"))
    print(normAndTokenize("百分之七十六九"))
    print(normAndTokenize("七十六°的样子"))
    print(normAndTokenize("七十六°"))
    print(normAndTokenize("气温七十六九度"))
    print(normAndTokenize("气温七十六九摄氏度"))
    print(normAndTokenize("百分之七十多"))
    print(normAndTokenize("比例百分之七十几"))
    print(normAndTokenize("四分之的概率"))
    print(normAndTokenize("Vlog占比百分之三十点五或千分之三十，BYE BYE",split_sentences=True))
    print(normAndTokenize("十分之一、四分之一、一百分之一、1/4、32/1000的概率，很好"))
    print(normAndTokenize("今天温度三十摄氏度=30°c，好热", split_sentences=True))
    print(normAndTokenize("log佛j单身dog.v23.ab"))
    print(normAndTokenize("ocean log佛j单身dog.v23.ab"))
    print(normAndTokenize("hello，今天是周万军的生日"))

    # print(normAndTokenize4Ch('1034.5秒')[0])
    # print(normAndTokenize4Ch('112:100，37.1秒')[0])
    # print(normAndTokenize4Ch('3 7 . 1 秒')[0])
    #print(normAndTokenize('3/Y', split_sentences=True))
    # print(normAndTokenize('A&cd十五~十六13—14bA_cdef-gh', 2, True))
    # print(normAndTokenize('我们「救中国」啊',split_sentences=True))
    # print(normalize('3/Y'))
    # print(normalize('3@性'))
    # print(normalize('AI-7'))
    # print(split_english_digits('x24'))
    # print(tokenize('4B72'))
    # print(tokenize('dancing. Docker'))
    # print(tokenize('bl'))
    # print(tokenize('log4j'))
    # print(tokenize('log4j2'))
    # print(normalize('N+GR'))
    # print(normalize('Australia\'s rest'))
    # print(normalize('-2GF'))
    # sentences = normalize("A.I.")
    # sentences = normalize("是7x24支持")
    # sentences = normalize("是=1")
    # sentences = normalize("dory2.0")
    # sentences = normalize("I'm happy")
    # sentences = normalize("G-4")
    # for sentence in sentences:
    #     print(tokenize(sentence))

# tokens = normAndTokenize("今天这场比赛克洛普教练看起来是要远程来指挥了好的随着本场主裁西蒙霍珀的一声哨响英超第16轮利物浦对阵南安普顿的比赛已经正式打强性我们来看看利物浦在开场阶段取得的一个右侧的定位球的机会利物浦这个赛季打进了7个定位球仅仅是比热刺的9个少一些做一下再来前点头球后蹭5球进了哇特扫开窍第6分钟又卡一次定位球的机会菲尔米诺抢球打进最近状态真是好太好了最近的状态菲尔米诺这个赛季这是第7个进球较早这就是基突埃没有立刻头球应该是个摆渡的性质这个真的是好像是在和队友做一个衔接但是这个球这球严重判断失误了罗伯逊开出来注意他一开始确实往左边挑的太多了往左边挑得太1米9以上的球员马竞有三人三中卫南伯顿这个赛季定位球打进两个哇这个球也进了双方各进一个定位球这是什么戏剧性啊噢来看看切亚当斯哈哈哈正说到南安普顿这个赛季也打进两个定位球这也是第3个并没有直接的去逼响到球路啊但是影响了利物浦防守的注意力这下切亚当斯不是最高的但是他在冲击一点方面是有很好的这种素质同样利物浦这个球的防线啊他仍然是处于大禁区线一带的这个位置大一线一带的位置就给了对方冲起来可能有一个空间的余地如果你的防线离门将更近的话你可能会让出更多外围的空间但是对门将来说可能会好一些所以这就是你的选择取舍刚才曼城也是遇到这种换帅的球队不好踢啊看看这次直接在边路来找努涅斯努涅斯传中看看这球的落点萨拉斯克嗯就是性格会有一点那种就是非常有英雄感的所以慢慢的也要适应再来看看这一次这个球啊我觉得传的还是质量很高的啊这个球裁判没有表示哈外围还是能够保护下来罗伯逊的传中菲尔米诺还让他继续传努涅斯球进了埋伏反超了比分凭借努涅斯的进球比分被改写成了2:1刚才我们其实不断的在夸今天这场比赛努涅斯塔很兴奋他不断的参与到利物浦的进攻中他会速度非常快整个的过程注意他的无球动与不动之间埃利奥特的传中给的脚法非常好第150次为南安普顿出场看看这次进攻机就出来了嗯做一下尼斯在这一侧门现在做一下转身菲尔米诺来打这个球80米抱住了三个人他们是在变换位置的不断的在更换跑位然后前插然后呢和队友之间结合得都是不错当然现在埃利奥特的一个重要的价值啊他还是要去发挥自己体能这次传中找努涅斯菲尔米诺把球保护下来我不逊分球巴赫在门前转身打门很猛也就是现在靠这个三个1米9还能够去蹭一下就靠身体对抗但是现在这么下去迟早会丢第3个球我觉得这个节奏不应该踢的太急应该稍微再稳一稳对于南安普顿来说看看这次又要打穿了球又进了3:1又是一次边中结合的完美的配合非常的漂亮啊今年利物浦真的打开了这意思应该是直接去了中路阿诺这一下很关键直塞交给罗伯逊直接完成传中门前其实萨拉赫和努涅斯都在包抄所以菲尔米诺又起到了什么作用对吧拉出来还是有作用还是能送没错两脚传球完成完成了这个镜头进球像刚才用左脚的解围就非常稳妥唉这次门前很有机会小角度的来打打机会完成了一次封堵我是萨利苏的一张红牌安菲尔德的球迷朋友们也是发出了雷鸣般的不满之声嗯但是确实有点疑问多齐门前起脚这次又是压力性做出了很精彩的扑救唉扬科上场之后我沃尔科特叫到右边这个球传出来看看落点头球瓦利松立功啊又用宝贵的名额去换后卫下都是换进攻线会比较多第5个角球开出来中间的位置哇这个球啊还是很有威胁的有10来这盘带这样他来自几场比赛切亚当斯这个点还是需要来放纳和加强的好的金伦库珀吹响了全场比赛结束的哨音最终利物浦在自己的主场3:1战胜了南安普顿这场胜")
# sentence = "".join(tokens[0].split())
# # print(model('摄氏度', tone=False, char_split=True))
#
# tokens = normAndTokenize("今天这场比赛克洛普教练看起来是要远程来指挥了好的随着本场主裁西蒙霍珀的一声哨响英超第16轮利物浦对阵南安普顿的比赛已经正式打响性我们来看看利物浦在开场阶段取得的一个右侧的定位球的机会利物浦这个赛季打进了7个定位球仅仅是比热刺的9个少一些做一下再来前点头球后蹭5球进了哇特扫开窍第6分钟又卡一次定位球的机会菲尔米诺抢球打进最近状态真是好太好了最近的状态菲尔米诺这个赛季这是第7个进球较早这就是welcometoXXX头球应该是个摆渡的性质这个真的是好像是在和队友做一个衔接但是XXX这个球这球严重判断失误了罗伯逊开出来注意他一开始确实往左边跳的太多了往左边跳得太1米9以上的球员啊就有三人三中卫南安普顿这个赛季定位球打进两个哇这个球也进了双方各进一个定位球这是什么戏剧性啊噢来看看切亚当斯哈哈哈正说到南安普顿这个赛季也打进两个定位球这也是第3个并没有直接的去影响到球路啊但是影响了利物浦防守的注意力这下切亚当斯不是最高的但是他在冲击一点方面是有很好的这种素质同样利物浦这个球的防线啊他仍然是处于大禁区线一带的这个位置大一线一带的位置就给了对方冲起来可能有一个空间的余地如果你的防线离门将更近的话你可能会让出更多外围的空间但是对门将来说可能会好一些所以这就是你的选择取舍刚才曼城也是遇到这种换帅的球队不好踢啊看看这次直接在边路来找努涅斯努涅斯传中看看这球的落点萨拉斯克嗯就是性格会有一点那种就是非常有英雄感的所以慢慢的也要适应再来看看这一次这个球啊我觉得传的还是质量很高的啊这个球裁判没有表示哈外围还是能够保护下来罗伯逊的传中菲尔米诺还让他继续传努涅斯球进了XXX反超了比分凭借努涅斯的进球比分被改写成了2:1刚才我们其实不断的在夸今天这场比赛努涅斯塔很兴奋他不断的参与到利物浦的进攻中他会速度非常快整个的过程注意他的无球动与不动之间埃利奥特的传中给的脚法非常好第150次为南安普顿出场看看这次进攻机就出来了嗯做一下尼斯在这一侧门现在做一下转身菲尔米诺来打这个球XXX抱住了三个人他们是在变换位置的不断的在更换跑位然后前插然后呢和队友之间结合得都是不错当然现在埃利奥特的一个重要的价值啊他还是要去发挥自己体能这次传中找努涅斯菲尔米诺把球保护下来罗伯逊分球巴赫在门前转身打门很猛也就是现在靠这个三个1米9还能够去撑一下就靠身体对抗但是现在这么下去迟早会丢第3个球我觉得这个节奏不应该踢的太急应该稍微再稳一稳对于南安普顿来说看看这次又要打穿了球又进了3:1又是一次边中结合的完美的配合非常的漂亮啊今年利物浦真的打开了这意思应该是直接去了中路阿诺这一下很关键直塞交给罗伯逊直接完成传中门前其实萨拉赫和努涅斯都在包抄所以菲尔米诺又起到了什么作用对吧拉出来还是有作用还是能送没错两脚传球完成完成了这个镜头进球像刚才用左脚的解围就非常稳妥唉这次门前很有机会小角度的来打打机会完成了一次封堵我是萨利苏的一张红牌安菲尔德的球迷朋友们也是发出了雷鸣般的不满之声嗯但是确实有点疑问多齐门前起脚这次又是XXX做出了很精彩的扑救唉扬科上场之后我沃尔科特叫到右边这个球传出来看看落点头球哇阿利松立功啊又用宝贵的名额去换后卫下都是换进攻线会比较多第5个角球开出来中间的位置哇这个球啊还是很有威胁的又是来这盘带这样他来自几场比赛切亚当斯这个点还是需要来放大和加强的好的金伦库珀吹响了全场比赛结束的哨音最终利物浦在自己的主场3:1战胜了南安普顿这场胜")
# sentence = "".join(tokens[0].split())

if __name__ == "__main__":
    main()
