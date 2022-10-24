import os
import codecs
import cn2an

# sports_asr_root_dir = "/root/noised_sports_corpus4"
# aiui_football_asr_root_dir = "/root/noised_aiui_football2"
# std_aiui_football_asr_root_dir = "/root/std_noised_aiui_football2"

sports_asr_root_dir =r'C:\Code\NeuralSpeech\FastCorrect\noised_sports_corpus4'
aiui_football_asr_root_dir = r'C:\Code\NeuralSpeech\FastCorrect\noised_aiui_football2'
std_aiui_football_asr_root_dir = r'C:\Code\NeuralSpeech\FastCorrect\std_noised_aiui_football2'

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
        if cn_digit_map.__contains__(ch):
            cn_digits += ch
        else:
            if len(cn_digits) > 0:
                try:
                    digits = cn2an.cn2an(cn_digits, mode="smart")
                except Exception as e:
                    modified_sentence += cn_digits + ch
                    cn_digits = ""
                    continue
                modified_sentence += (str(digits) + ch)
                cn_digits = ""
            else:
                modified_sentence += ch
    if len(cn_digits) > 0:
        try:
            digits = cn2an.cn2an(cn_digits, mode="smart")
            modified_sentence += str(digits)
        except Exception as e:
            modified_sentence += cn_digits
    return modified_sentence
def asr_replace_func(input_file_path):
    input_file_name = os.path.basename(input_file_path)
    input_file_dir = os.path.dirname(input_file_path)
    output_file_name = "tmp_" + input_file_name
    outfile = codecs.open(os.path.join(input_file_dir, output_file_name), 'w', 'utf-8')
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

            if orig_sentence == hypo_sentence: #龙猫和讯飞完全一样
                ref_corpus_map[orig_sentence] = orig_sentence #强制更新为正确语料

            else:
                mod_orig_sentence = replace_cn_digits(orig_sentence)
                mod_hypo_sentence = replace_cn_digits(hypo_sentence)
                if mod_orig_sentence == mod_hypo_sentence: #讯飞是正确的
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
    os.remove(os.path.join(input_file_dir, input_file_name))
    os.rename(os.path.join(input_file_dir, output_file_name), os.path.join(input_file_dir, input_file_name))

def preprocess_sports_asr(root_dir):
    for root,dirs,files in os.walk(root_dir):
        for file in files:
            if not file.endswith(".txt"):
                continue
            # 跳过 noised_aiui_football3.txt，保留 filename_aiui_football3_asr.txt
            # if file.find("football.txt") != -1 and file.find("_asr") == -1:
            #     continue
            file_path = os.path.join(root, file)
            asr_replace_func(file_path) #运动语料出现的词语必须出现
            print(f"{file_path} has been processed.")
#s1 = replace_cn_digits("五 打 二")
#s2 = replace_cn_digits(" 5 打 2")
#print(s1)
# print(s2)
# print(s1==s2)
preprocess_sports_asr(sports_asr_root_dir)
preprocess_sports_asr(aiui_football_asr_root_dir)
preprocess_sports_asr(std_aiui_football_asr_root_dir)
#asr_replace_func(r"C:\Code\NeuralSpeech\FastCorrect\test\cba.txt", r"C:\Code\NeuralSpeech\FastCorrect\test2")
