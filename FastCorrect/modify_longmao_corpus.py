import os
import codecs
import cn2an
import re

sports_asr_root_dir=r'C:\Code\NeuralSpeech\FastCorrect\noised_sports_corpus2'
normed_sports_asr_root_dir=r'C:\Code\NeuralSpeech\FastCorrect\normed_noised_sports_corpus2'

aiui_football_asr_root_dir = r'C:\Code\NeuralSpeech\FastCorrect\noised_aiui_football2'
normed_aiui_football_asr_root_dir = r'C:\Code\NeuralSpeech\FastCorrect\normed_noised_aiui_football2'

std_aiui_football_asr_root_dir = r'C:\Code\NeuralSpeech\FastCorrect\std_noised_aiui_football2'
normed_std_aiui_football_asr_root_dir = r'C:\Code\NeuralSpeech\FastCorrect\normed_std_noised_aiui_football2'

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
cn_digit_map['负'] = ''
dao_pattern = re.compile("[零一二三四五六七八九十百千万亿]+(到)[零一二三四五六七八九十百千万亿]+")

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

def replace_cn_digits(sentence):
    modified_sentence = ""
    cn_digits = ""
    for ch in sentence:
        ch = Q2B(ch)
        if ch == " ": #删除空格
            continue
        if cn_digit_map.__contains__(ch) or '0' <= ch <='9':
            cn_digits += ch
        else:
            if len(cn_digits) > 0:
                try:
                    digits = cn2an.cn2an(cn_digits, mode="smart")
                except Exception as e:
                    modified_sentence += cn_digits + ch
                    cn_digits = ""
                    continue
                digits = str(digits)
                # cn2an.cn2an('11', mode="smart") 返回浮点数 11.0，这里把 .0 丢弃
                if digits.endswith(".0") and not cn_digits.endswith(".0"):
                    digits = digits[0:-2]
                modified_sentence += (digits + ch)
                cn_digits = ""
            else:
                modified_sentence += ch
    if len(cn_digits) > 0:
        try:
            digits = cn2an.cn2an(cn_digits, mode="smart")
        except Exception as e:
            modified_sentence += cn_digits
            return modified_sentence
        digits = str(digits)
        # cn2an.cn2an('11', mode="smart") 返回浮点数 11.0，这里把 .0 丢弃
        if digits.endswith(".0") and not cn_digits.endswith(".0"):
            digits = digits[0:-2]
        modified_sentence += digits
    return modified_sentence

# def test(orig_sentence, hypo_sentence):
#     ref_corpus_map = {}
#     orig_sentence = orig_sentence.strip(".")
#     hypo_sentence = hypo_sentence.strip(".")
#
#     orig_sentence = re.sub(r"([零一二三四五六七八九十百千万亿]+)(~)([零一二三四五六七八九十百千万亿]+)", r'\1到\3', orig_sentence)
#     hypo_sentence = re.sub(r"([零一二三四五六七八九十百千万亿]+)(~)([零一二三四五六七八九十百千万亿]+)", r'\1到\3', hypo_sentence)
#     orig_sentence = re.sub(r"([0-9]+)(到)([0-9]+)", r'\1~\3', orig_sentence)
#     hypo_sentence = re.sub(r"([0-9]+)(到)([0-9]+)", r'\1~\3', hypo_sentence)
#
#     orig_sentence = re.sub(r"([零一二三四五六七八九十百千万亿]+)(:)([零一二三四五六七八九十百千万亿]+)", r'\1比\3', orig_sentence)
#     hypo_sentence = re.sub(r"([零一二三四五六七八九十百千万亿]+)(:)([零一二三四五六七八九十百千万亿]+)", r'\1比\3', hypo_sentence)
#     orig_sentence = re.sub(r"([0-9]+)(比)([0-9]+)", r'\1:\3', orig_sentence)
#     hypo_sentence = re.sub(r"([0-9]+)(比)([0-9]+)", r'\1:\3', hypo_sentence)
#
#     # 的/得 按照讯飞的转写习惯
#     if len(orig_sentence) == len(hypo_sentence):
#         tmp_orig_sentence = ""
#         for idx in range(len(orig_sentence)):
#             orig_ch = orig_sentence[idx]
#             hypo_ch = hypo_sentence[idx]
#             if orig_ch == '的':
#                 if hypo_ch == '得' or hypo_ch == '地':
#                     tmp_orig_sentence += hypo_ch
#                 else:
#                     tmp_orig_sentence += orig_ch
#             elif orig_ch == '得':
#                 if hypo_ch == '的' or hypo_ch == '地':
#                     tmp_orig_sentence += hypo_ch
#                 else:
#                     tmp_orig_sentence += orig_ch
#             elif orig_ch == '地':
#                 if hypo_ch == '得' or hypo_ch == '的':
#                     tmp_orig_sentence += hypo_ch
#                 else:
#                     tmp_orig_sentence += orig_ch
#             elif orig_ch == '是' and hypo_ch == '1' and idx < (len(orig_sentence)-1):
#                 next_orig_ch = orig_sentence[idx+1]
#                 if '0' <= next_orig_ch <= '9':
#                     tmp_orig_sentence += hypo_ch
#                 else:
#                     tmp_orig_sentence += orig_ch
#             else:
#                 tmp_orig_sentence += orig_ch
#     else:
#         tmp_orig_sentence = orig_sentence
#     #句末尾的 的/了 按照讯飞的转写习惯
#     if tmp_orig_sentence[-1] == '了' and hypo_sentence[-1] == '的':
#         tmp_orig_sentence = tmp_orig_sentence[:-1] + '的'
#     if tmp_orig_sentence[-1] == '的' and hypo_sentence[-1] == '了':
#         tmp_orig_sentence = tmp_orig_sentence[:-1] + '了'
#     #讯飞经常把 数字到数字 转写为 阿拉伯数字~阿拉伯数字，也是可以的
#     tmp_orig_sentence = re.sub(r"([零一二三四五六七八九十百千万亿0-9]+)(到)([零一二三四五六七八九十百千万亿0-9]+)", r'\1~\3', tmp_orig_sentence)
#     tmp_orig_sentence = re.sub(r"([零一二三四五六七八九十百千万亿0-9]+)(比)([零一二三四五六七八九十百千万亿0-9]+)", r'\1:\3', tmp_orig_sentence)
#     if tmp_orig_sentence == hypo_sentence:  # 龙猫和讯飞完全一样
#         ref_corpus_map[orig_sentence] = hypo_sentence  # 强制更新为正确语料
#     else:
#         tmp_orig_sentence = replace_cn_digits(tmp_orig_sentence)
#         tmp_hypo_sentence = replace_cn_digits(hypo_sentence)
#         if tmp_orig_sentence == tmp_hypo_sentence:  # 讯飞是正确的
#             ref_corpus_map[orig_sentence] = hypo_sentence  # 更新为讯飞语料
#         else:  # 讯飞不正确
#             if not ref_corpus_map.__contains__(orig_sentence):  # 只有在讯飞语料没有时才暂存龙猫语料
#                 ref_corpus_map[orig_sentence] = orig_sentence
#     print (f"{orig_sentence} {ref_corpus_map[orig_sentence]}")
#test("他们也是一个四二三幺的阵型", "他们也是一个4231的阵型")
# test("范围是十九到二十九", "范围19~29")
# test("范围是10到29", "范围是19到29")
# test("范围是十九~二十九", "范围19到29")
# test("周薪提到二十万英镑", "周薪提到20万英镑")
# # test("小朋友了", "小朋友的")
# test("干的不错", "干地不错")
# test("现在比分是9:1", "现在比分19:1")
# test("11到十二赛季", "11~12赛季")
# test("智利队二号梅纳", "智利队2号梅纳")

def asr_replace_func(input_file_path, root_dir, normed_root_dir):
    input_file_name = os.path.basename(input_file_path)
    input_file_dir = os.path.dirname(input_file_path)
    common_path = input_file_dir.replace(root_dir, "").strip("\\").strip("/")
    output_file_dir = os.path.join(normed_root_dir, common_path)
    if not os.path.isdir(output_file_dir):
        os.makedirs(output_file_dir)
    outfile = codecs.open(os.path.join(output_file_dir, input_file_name), 'w', 'utf-8')
    ref_corpus_map = {}
    sentences = []
    with codecs.open(input_file_path, 'r', 'utf-8') as myfile:
        for line in myfile:
            if len(line) == 0 or line.isspace():
                continue
            fields = line.split('\t')
            if len(fields) != 2:
                continue
            orig_sentence = fields[0].strip()
            #经过预处理的句子是单句，不会再包含逗号点号了（暂时不考虑断句模型输出，经过FC模型训练的情况）
            # orig_sentence = orig_sentence.strip(",")
            # orig_sentence = orig_sentence.strip("，")
            orig_sentence = orig_sentence.strip(".")
            # 大数字中asr结果有英文的,但是经过预处理，英文逗号没有了（暂时不考虑断句模型输出，经过FC模型训练的情况）
            # orig_sentence.replace(",", "，")
            hypo_sentence = fields[1].strip()
            # hypo_sentence = hypo_sentence.strip(",")
            # hypo_sentence = hypo_sentence.strip("，")
            hypo_sentence = hypo_sentence.strip(".")
            if len(orig_sentence) == 0 or len(hypo_sentence) == 0:
                continue

            orig_sentence = re.sub(r"([零一二三四五六七八九十百千万亿]+)(~)([零一二三四五六七八九十百千万亿]+)", r'\1到\3', orig_sentence)
            hypo_sentence = re.sub(r"([零一二三四五六七八九十百千万亿]+)(~)([零一二三四五六七八九十百千万亿]+)", r'\1到\3', hypo_sentence)
            orig_sentence = re.sub(r"([0-9]+)(到)([0-9]+)", r'\1~\3', orig_sentence)
            hypo_sentence = re.sub(r"([0-9]+)(到)([0-9]+)", r'\1~\3', hypo_sentence)

            orig_sentence = re.sub(r"([零一二三四五六七八九十百千万亿]+)(:)([零一二三四五六七八九十百千万亿]+)", r'\1比\3', orig_sentence)
            hypo_sentence = re.sub(r"([零一二三四五六七八九十百千万亿]+)(:)([零一二三四五六七八九十百千万亿]+)", r'\1比\3', hypo_sentence)
            orig_sentence = re.sub(r"([0-9]+)(比)([0-9]+)", r'\1:\3', orig_sentence)
            hypo_sentence = re.sub(r"([0-9]+)(比)([0-9]+)", r'\1:\3', hypo_sentence)
            # 得/的/地 按照讯飞的转写习惯
            if len(orig_sentence) == len(hypo_sentence):
                tmp_orig_sentence = ""
                for idx in range(len(orig_sentence)):
                    orig_ch = orig_sentence[idx]
                    hypo_ch = hypo_sentence[idx]
                    if orig_ch == '的':
                        if hypo_ch == '得' or hypo_ch == '地':
                            tmp_orig_sentence += hypo_ch
                        else:
                            tmp_orig_sentence += orig_ch
                    elif orig_ch == '得':
                        if hypo_ch == '的' or hypo_ch == '地':
                            tmp_orig_sentence += hypo_ch
                        else:
                            tmp_orig_sentence += orig_ch
                    elif orig_ch == '地':
                        if hypo_ch == '得' or hypo_ch == '的':
                            tmp_orig_sentence += hypo_ch
                        else:
                            tmp_orig_sentence += orig_ch
                    #是9 转写为 19 ，以讯飞为准
                    elif orig_ch == '是' and hypo_ch == '1' and idx < (len(orig_sentence)-1):
                        next_orig_ch = orig_sentence[idx+1]
                        if '0' <= next_orig_ch <= '9':
                            tmp_orig_sentence += hypo_ch
                        else:
                            tmp_orig_sentence += orig_ch
                    else:
                        tmp_orig_sentence += orig_ch
            else:
                tmp_orig_sentence = orig_sentence
            # 句末尾的 的/了 按照讯飞的转写习惯
            if orig_sentence[-1] == '了' and hypo_sentence[-1] == '的':
                tmp_orig_sentence = tmp_orig_sentence[:-1] + '的'
            # 讯飞经常把 数字到数字 转写为 阿拉伯数字~阿拉伯数字，也是可以的
            tmp_orig_sentence = re.sub(r"([零一二三四五六七八九十百千万亿0-9]+)(到)([零一二三四五六七八九十百千万亿0-9]+)", r'\1~\3', tmp_orig_sentence)
            # 讯飞经常把 数字比数字 转写为 阿拉伯数字:阿拉伯数字，也是可以的
            tmp_orig_sentence = re.sub(r"([零一二三四五六七八九十百千万亿0-9]+)(比)([零一二三四五六七八九十百千万亿0-9]+)", r'\1:\3', tmp_orig_sentence)
            if tmp_orig_sentence == hypo_sentence: #龙猫语料转换后和讯飞完全一样
                ref_corpus_map[orig_sentence] = hypo_sentence #更新为讯飞语料
            else:
                tmp_orig_sentence = replace_cn_digits(tmp_orig_sentence)
                tmp_hypo_sentence = replace_cn_digits(hypo_sentence)
                if tmp_hypo_sentence == tmp_orig_sentence: #讯飞是正确的
                    ref_corpus_map[orig_sentence] = hypo_sentence #更新为讯飞语料
                else: #讯飞不正确
                    if not ref_corpus_map.__contains__(orig_sentence): #只有在讯飞语料没有时才暂存龙猫语料
                        ref_corpus_map[orig_sentence] = orig_sentence
                    #下面考虑的是预处理时输出带有seperator符号的情况（没有分句，分句是通过另外的断句模型进行），暂时不考虑
                    # orig_idx = 0
                    # hypo_idx = 0
                    # orig_seg = ""
                    # hypo_seg = ""
                    # while orig_idx < len(mod_orig_sentence) and hypo_idx < len(mod_hypo_sentence):
                    #     if mod_hypo_sentence[hypo_idx] == '，' or mod_hypo_sentence[hypo_idx] == '。':
                    #         if len(orig_seg) > 1 and hypo_seg == orig_seg:
                    #             sentences.append(orig_seg + "\t" + orig_seg + "\n")
                    #             hypo_seg = ""
                    #             orig_seg = ""
                    #             hypo_idx += 1
                    #         elif orig_idx == 0:
                    #             hypo_idx += 1
                    #         else:
                    #             break
                    #     elif mod_hypo_sentence[hypo_idx] == mod_orig_sentence[orig_idx]:
                    #         hypo_seg += mod_hypo_sentence[hypo_idx]
                    #         orig_seg += mod_orig_sentence[orig_idx]
                    #         orig_idx += 1
                    #         hypo_idx += 1
                    #     else:
                    #         break
                    # if len(orig_seg) > 1 and hypo_seg == orig_seg:
                    #     sentences.append(orig_seg + "\t" + orig_seg + "\n")

    with codecs.open(input_file_path, 'r', 'utf-8') as myfile:
        for line in myfile:
            if len(line) == 0 or line.isspace():
                continue
            fields = line.split('\t')
            if len(fields) != 2:
                continue

            orig_sentence = fields[0].strip()
            # orig_sentence = orig_sentence.strip(",")
            # orig_sentence = orig_sentence.strip("，")
            orig_sentence = orig_sentence.strip(".")
            hypo_sentence = fields[1].strip()
            # hypo_sentence = hypo_sentence.strip(",")
            # hypo_sentence = hypo_sentence.strip("，")
            hypo_sentence = hypo_sentence.strip(".")
            if len(orig_sentence) == 0 or len(hypo_sentence) == 0:
                continue
            orig_sentence = ref_corpus_map[orig_sentence]
            pair = orig_sentence + "\t" + hypo_sentence + "\n"
            sentences.append(pair)

            if len(sentences) >= 10000:
                outfile.writelines(sentences)
                sentences = []
    #文件扫描结束
    if len(sentences) > 0:
        outfile.writelines(sentences)

    outfile.close()

def preprocess_sports_asr(root_dir, normed_root_dir):
    for root,dirs,files in os.walk(root_dir):
        for file in files:
            if not file.endswith(".txt"):
                continue
            file_path = os.path.join(root, file)
            asr_replace_func(file_path, root_dir, normed_root_dir) #运动语料出现的词语必须出现
            print(f"{file_path} has been processed.")
#s1 = replace_cn_digits("五 打 二")
#s2 = replace_cn_digits(" 5 打 2")
#print(s1)
# print(s2)
# print(s1==s2)
# preprocess_sports_asr(sports_asr_root_dir, normed_sports_asr_root_dir)
# preprocess_sports_asr(aiui_football_asr_root_dir, normed_aiui_football_asr_root_dir)
preprocess_sports_asr(std_aiui_football_asr_root_dir, normed_std_aiui_football_asr_root_dir)
