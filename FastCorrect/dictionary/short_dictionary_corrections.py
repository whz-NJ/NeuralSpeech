import codecs

dict_file_path = "./dict.CN_char.txt"
noised_english_file_path = "./noised_English.txt"
short_dict_file_path = "./short.dict.CN_char.txt"
short_noised_english_file_path = "./short_noised_English.txt" #丢弃不常见单词的英文纠错规则
MAX_TOKENS = 40000 #后续预处理/训练/预测时，如果出现词表中未出现的词，直接丢弃

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


token_count_map = {}
unknown_english_word_count_map = {}
tokens_num = 0
with open(dict_file_path, 'r', encoding='utf-8') as infile:
    for line in infile.readlines():
        tokens_num += 1
        if tokens_num > MAX_TOKENS:
            break
        fields = line.split()
        word = fields[0].strip()
        count = fields[1].strip()
        token_count_map[word] = int(count)


def split_tokens(line):
    tokens = []
    english = ""

    def add_english():
        nonlocal tokens, english
        if len(english) > 0:
            if english.upper() != english:
                tokens.append(english.lower())
                if not token_count_map.__contains__(english.lower()):
                    unknown_english_word_count_map[english.lower()] = \
                        unknown_english_word_count_map.get(english.lower(), 0) + 1
            else:
                tokens.append(english.upper())
                if not token_count_map.__contains__(english.upper()):
                    unknown_english_word_count_map[english.upper()] = \
                        unknown_english_word_count_map.get(english.upper(), 0) + 1
            english = ""
    for ch in line:
        if '\u4e00' <= ch <= '\u9fa5': #汉字
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
with open(noised_english_file_path, 'r', encoding='utf-8') as infile:
    for line in infile.readlines():
        fields = line.split('\t')
        word = fields[0]
        if not token_count_map.__contains__(word): # 跳过不频繁出现的token
            continue
        error_words = split_tokens(fields[1])
        if len(error_words) == 1 and error_words[0] == word:
            continue #跳过纠错词和原词相同的纠错规则
        if short_token_corrections_rules.__contains__(word):
            short_token_corrections_rules[word].append(error_words)
        else:
            short_token_corrections_rules[word] = [error_words]

short_dict_file = codecs.open(short_dict_file_path, 'w', 'utf-8')
token_count_map.update(unknown_english_word_count_map)
for token,count in sorted(token_count_map.items(), key=lambda x:x[1], reverse = True):
    short_dict_file.write(token + " " + str(count) + "\n")
short_dict_file.close()

short_noised_english_file = codecs.open(short_noised_english_file_path, 'w', 'utf-8')
for token in short_token_corrections_rules.keys():
    for correction_rule in short_token_corrections_rules.get(token):
        short_noised_english_file.write(token + "\t" + " ".join(correction_rule) + "\n")
short_noised_english_file.close()




