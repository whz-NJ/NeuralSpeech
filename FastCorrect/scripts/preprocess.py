import cn2an

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
def str2Digits(str):
    digits = ''
    for ch in str:
        digit = digitMap.get(ch)
        if digit:
            digits += digit
    return digits

def my_an2cn(digitsStr):
    if len(digitsStr) == 0:
        return ''
    if digitsStr[0] == '0' or digitsStr[0] == '.' or digitsStr.count('.') > 1 or len(digitsStr) > 9:
        return str2Digits(digitsStr)
    return cn2an.an2cn(digitsStr, 'low')

seperatorMap = {}
for ch in r'<>+-*/?~,，。！？;；()（）@&[]【】{}、—_《》':
    seperatorMap[ch] = ch
keepMap = {}
for ch in r'.:':
    keepMap[ch] = ch

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

def normalize(line):
    result = []
    sentence = ''

    digits = ''
    prev_ch = ''
    english_word = False
    line = line.strip()
    idx = 0
    while idx < len(line):
        ch = Q2B(line[idx])
        if idx < (len(line)-1):
            next_ch = Q2B(line[idx+1])
            if ch == '°' and (next_ch == 'C' or next_ch == 'c'):
                if(len(digits) > 0):
                    sentence += my_an2cn(digits)
                    sentence += '摄氏度'
                    digits = ''
                idx = idx + 1 # 跳过下一个字符
        else:
            next_ch = ''
        if seperatorMap.__contains__(ch): #句子分隔符
            if len(digits) > 0:
                sentence += my_an2cn(digits)
                digits = ''
            if len(sentence) >= 2:
                result.append(sentence)
                sentence = ""
            else:
                sentence = "" # 跳过过短的句子
            english_word = False
        elif ('0' <= ch and '9' >= ch): #数字
            if english_word:
                if len(digits) > 0:
                    sentence += digits
                    digits = ''
                sentence += ch #英文单词中的数字
            else:
                digits += ch
        elif ch == '%' and len(digits) > 0:
            digits = '百分之' + my_an2cn(digits)
            sentence += digits
            digits = ''
            english_word = False
        elif keepMap.__contains__(ch): #需要保留的符号
            if '0' <= prev_ch <= '9' and ('0' <= next_ch <= '9'): #两边都是数字
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
                                        sentence += my_an2cn(digits) + '点'
                                        digits = ''
                                        is_time = True
                    if not is_time:
                        sentence += my_an2cn(digits) + '比'
                        digits = ''
            else: #冒号不在两个数字中间，则作为句子分隔符
                if len(digits) > 0:
                    sentence += my_an2cn(digits)
                    digits = ''
                if(len(sentence) > 1):
                    result.append(sentence)
                sentence = ''
            english_word = False
        elif ('\u4e00' <= ch <= '\u9fa5') or ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'): #汉字或数字
            if len(digits) > 0:
                if ch == '年' and (len(digits) == 2 or len(digits) == 4) \
                        and (digits.find('.') == -1 and (int(digits) <= 99 or 1000 <= int(digits) <= 2099)):
                    sentence += str2Digits(digits) #xxxx年时，不变成带数量单位
                else:
                    sentence += my_an2cn(digits)
                digits = ''
            if ('\u4e00' <= ch <= '\u9fa5'): #汉字
                english_word = False
            else: #英文
                english_word = True
            sentence += ch
        elif ch == ' ' or ch == "\t":
            if english_word:
                sentence += ' ' #英文单词之间需要用空格分割
                english_word = False
        prev_ch = ch
        idx = idx + 1
    #一行扫描结束
    if len(digits) > 0:
        sentence += my_an2cn(digits)
    if len(sentence) > 0:
        result.append(sentence)
    return result

def tokenize(sentence):
    tokens = []
    idx = 0
    english_word = ''
    prev_ch = ''
    while idx < len(sentence):
        ch = sentence[idx]
        if '\u4e00' <= ch <= '\u9fa5':
            if len(english_word) > 0:
                tokens.append(english_word)
                english_word = ''
            tokens.append(ch)
        elif ('a' <= ch <= 'z') or ('A' <= ch <= 'Z') or ('0' <= ch <= '9'):
            english_word += ch
        elif ' ' == ch or "\t" == ch:
            if len(english_word) > 0:
                tokens.append(english_word)
                english_word = ''
            if prev_ch != ' ' and prev_ch != '\t': #仅保留一个空格
                tokens.append(' ')
        idx = idx + 1
        prev_ch = ch
    if len(english_word) > 0:
        tokens.append(english_word)
    return tokens

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
