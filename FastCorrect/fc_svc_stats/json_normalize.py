import cn2an
import os
import json

#corpus_root_dir=r'C:\工作任务\AIUI\NLP模型测试\侯德成语料2\\'
corpus_root_dir=r'C:\工作任务\AIUI\NLP模型测试\侯德成语料3\\'
cn_digit_map = {}
cn_digit_map['零'] = '0'
cn_digit_map['一'] = '1'
cn_digit_map['幺'] = '1'
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

def norm_tokenize(line):
    tokens = []
    cn_digits = ''
    english = ''
    line = line.strip()
    idx = 0
    while idx < len(line):
        ch = Q2B(line[idx])
        if cn_digit_map.__contains__(ch) or '0' <= ch <='9':
            cn_digits += ch
            if len(english) >0:
                tokens.append(english)
                english = ''
        elif ch == ' ' or ch == '\t':
            if len(english) >0:
                tokens.append(english)
                english = ''
            if len(cn_digits) >0:
                an_digits = my_cn2an(cn_digits)
                tokens.extend(an_digits.split())
                cn_digits = ''
        elif 'a' <= ch <= 'z' or 'A' <= ch <= 'Z':
            english += ch
            if (len(cn_digits) > 0):
                an_digits = my_cn2an(cn_digits)
                tokens.extend(an_digits.split())
                cn_digits = ''
        elif '~' == ch:
            tokens.append('到')
        elif '得' == ch:
            tokens.append('的')
        else:
            if len(english) > 0:
                tokens.append(english)
                english = ''
            if len(cn_digits) > 0:
                an_digits = my_cn2an(cn_digits)
                tokens.extend(an_digits.split())
                cn_digits = ''
            tokens.append(ch)
        idx += 1
    if len(english) > 0:
        tokens.append(english)
    if len(cn_digits) > 0:
        an_digits = my_cn2an(cn_digits)
        tokens.extend(an_digits.split())
    return tokens

string = norm_tokenize("是零四零五赛季")
print(string)
string = norm_tokenize("将会有3万多名球迷来到现场")
print(string)

corpus_root_dir = corpus_root_dir.strip(r'/')
corpus_root_dir = corpus_root_dir.strip(r'\\')
for root, dirs, files in os.walk(corpus_root_dir):
    for file in files:
        if not file.endswith(".json") or (not file.startswith("asr_") and not file.startswith("fc_")):
            continue
        root = root.strip(r'/')
        root = root.strip(r'\\')
        if root != corpus_root_dir: #忽略子目录
            continue
        file_path = os.path.join(root, file)
        with open(file_path, 'r', encoding='utf-8') as infile:
            j = json.load(infile)
            for x in j["utts"]:
                rec_text = j["utts"][x]["output"][0]["rec_text"]
                rec_tokens = norm_tokenize(rec_text)
                j["utts"][x]["output"][0]["rec_text"] = "".join(rec_tokens)
                j["utts"][x]["output"][0]["rec_token"] = " ".join(rec_tokens)

                text = j["utts"][x]["output"][0]["text"]
                tokens = norm_tokenize(text)
                j["utts"][x]["output"][0]["text"] = "".join(tokens)
                j["utts"][x]["output"][0]["token"] = " ".join(tokens)
        json_string = json.dumps(j, ensure_ascii=False, indent=2)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_string)
