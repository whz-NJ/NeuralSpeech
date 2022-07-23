import cn2an
import re

digitMap = {}
digitMap['0'] = '零'
digitMap['1'] = '一'
digitMap['2'] = '二'
digitMap['3'] = '三'
digitMap['4'] = '四'
digitMap['5'] = '五'
digitMap['6'] = '六'
digitMap['7'] = '七'
digitMap['8'] = '八'
digitMap['9'] = '九'
digitMap['.'] = '点'
def str_to_digits(str):
    digits = ''
    for ch in str:
        digit = digitMap.get(ch)
        if digit:
            digits += digit
    return digits

def split_digits(str):
    digits = []
    for ch in str:
        digit = digitMap.get(ch)
        if digit:
            digits.append(digit)
    return digits

def my_an2cn(digitsStr):
    if len(digitsStr) == 0:
        return ''
    if digitsStr[0] == '0' or digitsStr[0] == '.' or digitsStr.count('.') > 1 or len(digitsStr) > 9:
        return str_to_digits(digitsStr)
    return cn2an.an2cn(digitsStr, 'low')

seperatorMap = {}
for ch in r'<>?,，。！？;；()（）[]【】{}、《》「」—':
    seperatorMap[ch] = ch
keepMap = {}
for ch in r'@.:+-=/\'×~&_':
    keepMap[ch] = ch

char_digits_pattern = re.compile(r'^([0-9.]*)([a-zA-Z]+)([0-9.]*)([a-zA-Z]*)([0-9.]*)$')
def split_english_digits(english_digits):
    tokens = []
    matched_result = char_digits_pattern.match(english_digits)
    if matched_result:
        digits1 = matched_result.group(1)
        english_word1 = matched_result.group(2)
        digits2 = matched_result.group(3)
        english_word2 = matched_result.group(4)
        digits3 = matched_result.group(5)
        if digits1:
            tokens.append(my_an2cn(digits1))
        tokens.append(english_word1)
        if digits2:
            tokens.append(my_an2cn(digits2))
        if english_word2:
            tokens.append(english_word2)
        if digits3:
            tokens.append(my_an2cn(digits3))
    else:
        tokens.append(english_digits)
    return tokens

def Q2B(uchar):
    """全角转半角"""
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e:  # 转完之后不是半角字符返回原来的字符
        return uchar
    return chr(inside_code)

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

from g2pM import G2pM
model = G2pM()
g2pM_dict = {}
tokens_count_dict = {}
# @.:+-=/\'×~&_
g2pM_dict['+'] = unify_pinyin(''.join(model('加', tone=False, char_split=True)))
g2pM_dict['.'] = unify_pinyin(''.join(model('点', tone=False, char_split=True)))
g2pM_dict['@'] = unify_pinyin(''.join(model('爱', tone=False, char_split=True)))
g2pM_dict['×'] = unify_pinyin(''.join(model('乘', tone=False, char_split=True)))
g2pM_dict['='] = unify_pinyin(''.join(model('等', tone=False, char_split=True)))
g2pM_dict['度'] = unify_pinyin(''.join(model('度', tone=False, char_split=True)))
#注意后面分词如何处理的，是否支持多个字的词
g2pM_dict['%'] = unify_pinyin(''.join(model('百', tone=False, char_split=True))) #百分之
g2pM_dict['比'] = unify_pinyin(''.join(model('比', tone=False, char_split=True)))
g2pM_dict['/'] = unify_pinyin(''.join(model('分', tone=False, char_split=True))) #分之，讯飞ASR，不会把 / 符号当作除
g2pM_dict['减'] = unify_pinyin(''.join(model('减', tone=False, char_split=True)))
g2pM_dict['负'] = unify_pinyin(''.join(model('负', tone=False, char_split=True)))
g2pM_dict['~'] = unify_pinyin(''.join(model('至', tone=False, char_split=True)))
g2pM_dict['&'] = unify_pinyin(''.join(model('和', tone=False, char_split=True)))
for digit in digitMap.keys():
    g2pM_dict[digit] = unify_pinyin(''.join(model(digitMap[digit], tone=False, char_split=True)))

#拆成独立发音的 tokens
def normAndTokenize(line, min_sentence_len=2, split_sentences=False):
    sentences = []

    def append_english_digits():
        nonlocal tokens, english, digits
        if len(english) > 0:
            english_lower = english.lower()  # 为了减小大小写字母不统一，统一转换为小写
            tokens.append(english_lower)
            tokens_count_dict[english_lower] = tokens_count_dict.get(english_lower, 0) + 1
            if not g2pM_dict.__contains__(english_lower):
                g2pM_dict[english_lower] = english_lower
            english = ''
        # elif combine_digits: #数字组合，不能组合，否则训练预测时会出现OOV问题
        #     if len(digits) > 0:
        #         tokens.append(digits)
        #         if not g2pM_dict.__contains__(digits):
        #             g2pM_dict[digits] = model(my_an2cn(digits), tone=False, char_split=True)
        #         digits = ''
        elif len(digits) > 0: #数字分开
            for digit in digits:
                tokens.append(digit)
                tokens_count_dict[digit] = tokens_count_dict.get(digit, 0) + 1
            digits = ''

    def extract_digits(words):
        digits_count = 0
        nonlocal tokens
        for ch in words:
            if '0' <= ch <= '9' or ch == '.':
                tokens.append(ch)
                tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
                digits_count += 1
            else:
                break
        return digits_count

    tokens = []
    english = ''
    digits = ''
    prev_ch = ''
    line = line.strip()
    idx = 0
    while idx < len(line):
        ch = Q2B(line[idx])
        if idx < (len(line)-1):
            next_ch = Q2B(line[idx+1])
            if ch == '°':
                if (next_ch == 'C' or next_ch == 'c'):
                    idx += 2  # 跳过下一个字符
                else:
                    idx += 1
                append_english_digits()
                tokens.append('度')
                tokens_count_dict['度'] = tokens_count_dict.get('度', 0) + 1
                prev_ch = ''
                continue
        else:
            next_ch = ''

        if seperatorMap.__contains__(ch): #句子分隔符
            append_english_digits()
            if not split_sentences: #不分句（处理ASR输出或强制纠错规则时）
                prev_ch = ch
                idx = idx + 1  # 丢弃，跳到下一个字符
                continue
            if len(tokens) >= min_sentence_len: # 分句且当前句子token数满足要求
                sentences.append(" ".join(tokens))
            tokens = []
        elif '0' <= ch <= '9': #数字
            if len(english) > 0:
                english_lower = english.lower()  # 为了减小大小写字母不统一，统一转换为小写
                tokens.append(english_lower)
                tokens_count_dict[english_lower] = tokens_count_dict.get(english_lower, 0) + 1
                if not g2pM_dict.__contains__(english_lower):
                    g2pM_dict[english_lower] = english_lower
                english = ''
            digits += ch
        elif ch == '%':
            if '0' <= prev_ch <= '9': #百分号跟在数字后
                tokens.append('%') #先加百分号，再加数字
                tokens_count_dict['%'] = tokens_count_dict.get('%', 0) + 1
            append_english_digits() #先加百分号，再加数字
        elif keepMap.__contains__(ch): #需要保留的符号
            if ch == '+' or ch == '=' or ch =='@' or ch == '×'\
                    or ch == '&' or ch == '~':
                append_english_digits()
                tokens.append(ch)
                tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
                prev_ch = ch
                idx = idx + 1
                continue
            if '0' <= prev_ch <= '9' and ('0' <= next_ch <= '9'): #ch是需保留符号，两边都是数字
                if ch == '.':
                    digits += '.' # 数字中的点
                elif ch == ':':
                    is_time = False
                    if digits.find('.') == -1 and len(digits) == 2 and int(digits) < 24:
                        if (idx < len(line) - 2):
                            next_next_ch = Q2B(line[idx+2])
                            if '0' <= next_next_ch <= '9':
                                next_digit = int('' + next_ch + next_next_ch)
                                if next_digit < 60:
                                    #当前字符往后数的第3个字符不是数字
                                    if (idx == len(line) - 3) or line[idx+3] < '0' or line[idx+3] > '9':
                                        append_english_digits()
                                        tokens.append('点')
                                        tokens_count_dict['点'] = tokens_count_dict.get('点', 0) + 1
                                        is_time = True
                    if not is_time:
                        append_english_digits()
                        tokens.append('比')
                        tokens_count_dict['比'] = tokens_count_dict.get('比', 0) + 1
                elif ch == '/':
                        digits_count = extract_digits(line[idx+1:]) #先取后面数字
                        tokens.append(ch) # 再取 /
                        tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
                        append_english_digits() # 再取前面的数字
                        idx += digits_count
                elif ch == '-':
                    append_english_digits()
                    tokens.append('减')
                    tokens_count_dict['减'] = tokens_count_dict.get('减', 0) + 1
            elif '0' <= next_ch <= '9' and ch == '-': #ch是需保留符号，右边是数字，左边不是数字
                if 'A' <= prev_ch <= 'Z' or 'a' <= prev_ch <= 'z':
                    tokens.append('减')
                    tokens_count_dict['减'] = tokens_count_dict.get('减', 0) + 1
                else:
                    tokens.append('负')
                    tokens_count_dict['负'] = tokens_count_dict.get('负', 0) + 1
                english = ''
            else: #ch是需保留符号，两边都不是数字
                if ch == '.':
                    append_english_digits()
                    if 'A' <= prev_ch <= 'Z' or 'a' <= prev_ch <= 'z' or 'A' <= next_ch <= 'Z' or 'a' <= next_ch <= 'z':
                        tokens.append(ch)
                        tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
                elif ch == '\'' and len(english) > 0 and (('A' <= next_ch <= 'Z') or ('a' <= next_ch <= 'z')): # 英文单词中的'号
                    english += ch
                elif ch == '/' and not ('\u4e00' <= prev_ch <= '\u9fa5') and not ('\u4e00' <= next_ch <= '\u9fa5'):
                    append_english_digits()
                    tokens.append(ch)
                    tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
                else: #不在两个数字或英文字母之间的特殊符号，作为词分隔符
                    append_english_digits()
                    if not split_sentences:
                        prev_ch = ch
                        idx = idx + 1  # 丢弃，跳到下一个字符
                        continue
        elif '\u4e00' <= ch <= '\u9fa5': #汉字
            append_english_digits()
            if not g2pM_dict.__contains__(ch):
                g2pM_dict[ch] = unify_pinyin(model(ch, tone=False, char_split=True)[0])
            tokens.append(ch)
            tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
        elif ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'): #英文
            if len(digits) > 0:
                for digit in digits:
                    tokens.append(digit)
                    tokens_count_dict[digit] = tokens_count_dict.get(digit, 0) + 1
                digits = ''
            english += ch
        elif ch == ' ' or ch == "\t":
            append_english_digits()
        prev_ch = ch
        idx = idx + 1
    #一行扫描结束
    append_english_digits()
    if len(tokens) >= min_sentence_len:  # 分句且当前句子token数满足要求
        sentences.append(" ".join(tokens))
    return sentences

def main():
    #print(normAndTokenize('3/Y', split_sentences=True))
    print(normAndTokenize('A&cd十五~十六13—14bA_cdef-gh', 2, True))
    print(normAndTokenize('我们「救中国」啊',split_sentences=True))
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

# print(model('摄氏度', tone=False, char_split=True))
if __name__ == "__main__":
    main()
