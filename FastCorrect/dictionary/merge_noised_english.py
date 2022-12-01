import codecs

short_noised_english_file_path = "./short_noised_English.txt"

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


def split_tokens(line):
    tokens = []
    english = ""

    def add_english():
        nonlocal tokens, english
        if len(english) > 0:
            if len(english) > 1:
                if english.upper() != english: #如果不是全大写，则转为全小写（统一）
                    tokens.append(english.lower())
                else:
                    tokens.append(english)
            else:
                tokens.append(english.upper()) # 字母统一用大写
            english = ""
    for ch in line:
        if '\u4e00' <= ch <= '\u9fa5' or '\u3400' <= ch <= '\u4DB5': #汉字
            add_english()
            tokens.append(Q2B(ch))
        elif ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'): #英文
            english += ch
        elif ('0' <= ch <= '9'):
            tokens.append(ch)
        elif ch == ' ' or ch == "\t":
            add_english()
        else:
            add_english()
    add_english()
    return tokens

# print(split_tokens("legs."))
# print(split_tokens("take so."))

short_token_corrections_rules = {}
with open(short_noised_english_file_path, 'r', encoding='utf-8') as infile:
    for line in infile.readlines():
        fields = line.split('\t')
        word = fields[0]
        if len(word) > 1:
            if word.upper() != word:  #如果不是全大写，则转为全小写（统一）
                word = word.lower()
        elif len(word) == 1: #字母统一是大写
            word = word.upper()
        else:
            continue
        error_words = split_tokens(fields[1])
        if len(error_words) == 1 and (error_words[0].upper() == word.upper()):
            continue #跳过纠错词和原词相同的纠错规则
        if short_token_corrections_rules.__contains__(word):
            old_error_words = short_token_corrections_rules[word]
            if error_words not in old_error_words:
                short_token_corrections_rules[word].append(error_words)
        else:
            short_token_corrections_rules[word] = [error_words]

short_noised_english_file = codecs.open(short_noised_english_file_path+"2", 'w', 'utf-8')
for token in short_token_corrections_rules.keys():
    for correction_rule in short_token_corrections_rules.get(token):
        short_noised_english_file.write(token + "\t" + " ".join(correction_rule) + "\n")
short_noised_english_file.close()




