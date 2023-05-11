# -*- coding: utf-8 -*-
import cn2an
import re
from g2pM import G2pM
import zhconv

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
# %@.:+-=/×÷~&
# 单音节的特殊符号和汉字读音可以通过模型互转，不处理（语料是什么就是什么）
# 多音节的特殊符号%的汉字恢复为原始特殊符号
# :既可能读做 比 也可能读做 点
# 当两段比较文字中特殊字符不一致时，通过模糊拼音对齐

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

