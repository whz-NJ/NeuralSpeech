import cn2an
import re

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

def str_to_digits(str):
    digits = ''
    for ch in str:
        digit = digit_map.get(ch)
        if digit:
            digits += digit
    return digits

def my_an2cn(digitsStr):
    if len(digitsStr) == 0:
        return ''
    if digitsStr[0] == '0' or digitsStr[0] == '.' or digitsStr.count('.') > 1 or len(digitsStr) > 9:
        return str_to_digits(digitsStr)
    return cn2an.an2cn(digitsStr, 'low')

seperator_map = {}
for ch in r'<>?,，。！？;；()（）[]【】{}、《》「」—':
    seperator_map[ch] = ch
kept_char_map = {}
for ch in r'%@.:+-=/×÷~&': #虽然英文里有'这里也不要了，后面实际纠错时也调用preprocess，删除不要的符号
    kept_char_map[ch] = ch

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
# %@.:+-=/×÷~&
# 单音节的特殊符号和汉字读音可以通过模型互转，不处理（语料是什么就是什么）
# 多音节的特殊符号%的汉字恢复为原始特殊符号
# :既可能读做 比 也可能读做 点，这里不设置其拼音，统一用原始字符代替其读音
# 当两段比较文字中特殊字符不一致时，通过模糊拼音对齐
g2pM_dict['+'] = unify_pinyin(''.join(model('加', tone=False, char_split=True)))
g2pM_dict['-'] = unify_pinyin(''.join(model('减', tone=False, char_split=True)))
g2pM_dict['.'] = unify_pinyin(''.join(model('点', tone=False, char_split=True)))
g2pM_dict['@'] = unify_pinyin(''.join(model('爱', tone=False, char_split=True)))
g2pM_dict['×'] = unify_pinyin(''.join(model('乘', tone=False, char_split=True)))
g2pM_dict['÷'] = unify_pinyin(''.join(model('除', tone=False, char_split=True)))
g2pM_dict['='] = unify_pinyin(''.join(model('等', tone=False, char_split=True)))
#注意后面分词如何处理的，是否支持多个字的词
g2pM_dict['/'] = unify_pinyin(''.join(model('分', tone=False, char_split=True))) #分之，讯飞ASR，不会把 / 符号当作除
g2pM_dict['~'] = unify_pinyin(''.join(model('至', tone=False, char_split=True)))
g2pM_dict['&'] = unify_pinyin(''.join(model('和', tone=False, char_split=True)))
for digit in digit_map.keys():
    g2pM_dict[digit] = unify_pinyin(''.join(model(digit_map[digit], tone=False, char_split=True)))

def my_cn2an(cnDigitsStr):
    cnDigits = cnDigitsStr.split('点')
    result = ""
    for cnDigit in cnDigits:
        if len(cnDigit) > 0:
            if len(cnDigit) > 1 or (cnDigit != '十' and cnDigit != '百' and cnDigit != '千' and cnDigit != '万' and cnDigit != '亿'):
                try:
                    result += str(cn2an.cn2an(cnDigit, mode='smart')) + "."
                except:
                    return ""
            else:#十分之 百分之 千分之 万分之 亿分之 中的 十/百/千/万/亿
                result += str(cn2an.cn2an('一' + cnDigit, mode='smart')) + "."
    if not cnDigitsStr.endswith('点'):
        result = result[0:-1] #删除for循环中固定加的.
    if cnDigitsStr.startswith('点'):
        result = '.' + result
    return result

#拆成独立发音的 tokens
def normAndTokenize(line, min_sentence_len=2, split_sentences=False):
    sentences = []

    def append_english_digits(append_english=False, append_digits=False, append_cn_digits=False, cn_to_an = False):
        nonlocal tokens, english, digits, cn_digits
        if append_english and len(english) > 0:
            if english.upper() != english: #如果不是全大写，则转为全小写（统一）
                english = english.lower()
            tokens.append(english)
            tokens_count_dict[english] = tokens_count_dict.get(english, 0) + 1
            english = ''
        if append_digits and len(digits) > 0: #数字分开
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

    def extract_cn_digits(line, start_index, cn_to_an = False):
        digits_count = 0
        nonlocal tokens
        cn_digits = ""
        idx = start_index
        while idx < len(line):
            ch = Q2B(line[idx])
            if cn_digit_map.__contains__(ch):
                cn_digits += ch
                digits_count += 1
                idx += 1
            else:
                break
        if idx < len(line):
            ch = Q2B(line[idx])
            if ch == '几' or ch == '多': #中文数字后面跟有概数
                return -1 # 不应该把中文概数数字转换为阿拉伯数字
        if not cn_to_an:
            for digit in cn_digits:
                tokens.append(digit)
                tokens_count_dict[digit] = tokens_count_dict.get(digit, 0) + 1
        else:
            an_digits = my_cn2an(cn_digits)
            if not an_digits or len(an_digits) == 0:
                return -1 #可能是两个中文数字连在一起，不应该把它们转换为阿拉伯数字
            for digit in an_digits:
                tokens.append(digit)
                tokens_count_dict[digit] = tokens_count_dict.get(digit, 0) + 1
        return digits_count

    tokens = []
    english = ''
    digits = ''
    cn_digits = ''
    prev_ch = ''
    line = line.strip()
    idx = 0
    while idx < len(line):
        ch = Q2B(line[idx])
        if ch == '°':
            append_english_digits(True, True, True)  # 如果有中文数字，保持原样，不转换为阿拉伯数字
            tokens.append(ch)
            tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
        if idx < (len(line)-1):
            next_ch = Q2B(line[idx+1])
            if (ch == '°') and (next_ch == 'C' or next_ch == 'c'):
                tokens.append('C')
                tokens_count_dict['C'] = tokens_count_dict.get('C', 0) + 1
                prev_ch = ch
                idx += 2  # 跳过下一个字符
                continue
            # 将中文摄氏度统一转换为°C，如果是单独的度，就不转换为°了，让模型自己转换
            elif ch == '摄' and next_ch == '氏' and idx < (len(line)-2):
                next_next_ch = Q2B(line[idx+2])
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
        elif '\u4e00' <= ch <= '\u9fa5': #汉字
            if ch != '分' and not cn_digit_map.__contains__(ch):
                append_english_digits(True, True, True) # 当前汉字为普通的汉字。前面如果有中文数字，保持原样，不转换为阿拉伯数字
                tokens.append(ch)
                tokens_count_dict[ch] = tokens_count_dict.get(ch, 0) + 1
            elif ch == '分':
                if next_ch == '之':
                    if cn_digit_map.__contains__(prev_ch):
                        # 中文读比例数字时，分子在后面读，而阿拉伯数字表示比例，分子在前面
                        # 这里先提取阿拉伯数字表示法中需要的分子
                        digits_num = extract_cn_digits(line, idx + 2, True)
                        if digits_num == -1: #遇到了中文概数，此时不应该转换为阿拉伯数字
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
                                append_english_digits(append_english=True, append_digits=True)
                                tokens.append('/')
                                tokens_count_dict['/'] = tokens_count_dict.get('/', 0) + 1
                                # 最后提取阿拉伯数字表示法中需要的分母
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

# '%@.:+-=/×÷~&'
punctMap = {}
punctMap['+'] = '加'
punctMap['@'] = '艾特'
punctMap['×'] = '乘'
punctMap['='] = '等于'
punctMap['&'] = '安得'
punctMap['-'] = '减'
punctMap['÷'] = '除'
punctMap['~'] = '至'
punctMap['.'] = '点'
def normAndTokenize4Ch(line, min_sentence_len=2, split_sentences=False):
    sentences = []
    def append_digits():
        nonlocal tokens, digits
        if len(digits) > 0: #数字分开
            tokens.extend([c for c in my_an2cn(digits)])
            digits = ''

    def extract_digits(words):
        digits_count = 0
        digits = ""
        nonlocal tokens
        for ch in words:
            if '0' <= ch <= '9' or ch == '.':
                digits += ch
                digits_count += 1
            else:
                break
        tokens.extend([c for c in my_an2cn(digits)])
        return digits_count

    tokens = []
    digits = ''
    prev_ch = ''
    line = line.strip()
    idx = 0
    while idx < len(line):
        ch = Q2B(line[idx])
        if idx < (len(line)-1):
            next_ch = Q2B(line[idx+1])
            if ch == '°':
                append_digits()
                if next_ch == 'C' or next_ch == 'c':
                    tokens.append('摄')
                    tokens.append('氏')
                    tokens.append('度')
                    idx += 2  # 跳过下一个字符
                else:
                    idx += 1
                    tokens.append('度')
                prev_ch = ''
                continue
        else:
            next_ch = ''

        if seperator_map.__contains__(ch): #句子分隔符
            append_digits()
            if not split_sentences: #不分句（处理ASR输出或强制纠错规则时）
                prev_ch = ch
                idx = idx + 1  # 丢弃，跳到下一个字符
                continue
            if len(tokens) >= min_sentence_len: # 分句且当前句子token数满足要求
                sentences.append(" ".join(tokens))
            tokens = []
        elif '0' <= ch <= '9': #数字
            digits += ch
        elif kept_char_map.__contains__(ch): #需要保留的符号
            if ch == '%':
                if '0' <= prev_ch <= '9':  # 百分号跟在数字后
                    tokens.append('百')  # 先加百分号，再加数字
                    tokens.append('分')
                    tokens.append('之')
                append_digits()  # 先加百分号，再加数字
                prev_ch = ch
                idx = idx + 1
                continue
            if ch == '+' or ch == '=' or ch =='@' or ch == '×'\
                    or ch == '&' or ch == '~' or ch == '÷':
                append_digits()
                tokens.extend([c for c in punctMap[ch]]) #拆出来
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
                                        append_digits()
                                        tokens.append('点')
                                        is_time = True
                    if not is_time:
                        append_digits()
                        tokens.append('比')
                elif ch == '/':
                        digits_count = extract_digits(line[idx+1:]) #先取后面数字
                        tokens.append('分') # 再取 /
                        tokens.append('之')
                        append_digits() # 再取前面的数字
                        idx += digits_count
                elif ch == '-': #ch是-，两边都是数字
                    append_digits()
                    tokens.append('减')
            elif '0' <= next_ch <= '9' and ch == '-': #ch是需保留符号，右边是数字，左边不是数字
                tokens.append('负')
            else: #ch是需保留符号，两边都不是数字
                if ch == '.':
                    append_digits()
                    tokens.append('点')
                else: #不在两个数字或英文字母之间的特殊符号，作为词分隔符
                    append_digits()
                    if not split_sentences:
                        prev_ch = ch
                        idx = idx + 1  # 丢弃，跳到下一个字符
                        continue
        elif '\u4e00' <= ch <= '\u9fa5': #汉字
            append_digits()
            tokens.append(ch)
        elif ch == ' ' or ch == "\t":
            append_digits()
        prev_ch = ch
        idx = idx + 1
    #一行扫描结束
    append_digits()
    if len(tokens) >= min_sentence_len:  # 分句且当前句子token数满足要求
        sentences.append(" ".join(tokens))
    return sentences

def main():
    print(normAndTokenize("二点三零点四"))
    print(normAndTokenize("版本号是V二点三零点四"))
    # print(normAndTokenize("版本号是V二点三零点四"))
    # print(normAndTokenize("百分之七十六七十九点八啊"))
    # print(normAndTokenize("百分之七十六九"))
    # print(normAndTokenize("七十六°的样子"))
    # print(normAndTokenize("七十六°"))
    # print(normAndTokenize("气温七十六九度"))
    # print(normAndTokenize("气温七十六九摄氏度"))
    # print(normAndTokenize("百分之七十多"))
    # print(normAndTokenize("比例百分之七十几"))
    # print(normAndTokenize("四分之的概率"))
    # print(normAndTokenize("Vlog占比百分之三十点五或千分之三十，BYE",split_sentences=True))
    # print(normAndTokenize("十分之一、四分之一、一百分之一、1/4、32/1000的概率，很好"))
    # print(normAndTokenize("今天温度三十摄氏度=30°c，好热", split_sentences=True))
    # print(normAndTokenize("域名是migu.cn或咪咕点。Cn", split_sentences=True))
    # print(normAndTokenize("登陆咪咕 + 木鸡结算系统"))
    print(normAndTokenize("log佛j单身dog.v23.ab"))
    print(normAndTokenize("ocean log佛j单身dog.v23.ab"))
    # print(normAndTokenize("hello，今天是周万军的生日"))

    # print(normAndTokenize4Ch('1034.5秒')[0])
    # print(normAndTokenize4Ch('112:100，37.1秒')[0])
    # print(normAndTokenize4Ch('3 7 . 1 秒')[0])
    print(normAndTokenize4Ch('我们1/23的人abc30%的概率，59.2÷37=32.5-35.3=0')[0])
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

# print(model('摄氏度', tone=False, char_split=True))
if __name__ == "__main__":
    main()
