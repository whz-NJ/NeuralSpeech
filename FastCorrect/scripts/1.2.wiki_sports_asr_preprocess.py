# -*- coding: utf-8 -*-
import os
import re
import codecs
import preprocess

# data_path = '../'
# data_names = ['sports.txt']
wiki_data_path = '/root/extracted/AA'
wiki_data_names = ['zh_wiki_00', 'zh_wiki_01', 'zh_wiki_02']
std_wiki_data_root_dir = '/root/std_wiki'

sports_asr_root_dir = r'C:\Code\NeuralSpeech\FastCorrect\noised_sports_corpus4'
std_sports_asr_root_dir = r'C:\Code\NeuralSpeech\FastCorrect\std_noised_sports_corpus4'

aiui_football_asr_root_dir = r'C:\Code\NeuralSpeech\FastCorrect\noised_aiui_football2'
# 这个脚本必须一次执行完，不能执行到中途停止，重新执行，这样可能会把 std_*_asr.txt 文件清空
std_aiui_football_asr_root_dir = r'C:\Code\NeuralSpeech\FastCorrect\std_noised_aiui_football2' #已经存在一版龙猫已经标注好的标注语料

def wiki_replace_func(input_file_path, output_file_dir):
    input_file_name = os.path.basename(input_file_path)
    if not os.path.isdir(output_file_dir):
        os.makedirs(output_file_dir)
    outfile = codecs.open(output_file_dir + '/std_' + input_file_name, 'w', 'utf-8')

    with codecs.open(input_file_path, 'r', 'utf-8') as myfile:
        sentences = []
        for line in myfile:
            if r'<doc ' in line or r'</doc>' in line or r'<doc>' in line:
                continue
            line = line.replace('&lt;br&gt;', '。')
            line = line.replace('zh-cn:', '。')
            line = line.replace('zh-tw:', '。')
            line = line.replace('zh-hk:', '。')
            line = line.replace('zh-hans:', '。')
            line = line.replace('zh-hant:', '。')
            line = line.replace('zh-sg:', '。')
            sentences.extend([sentence + '\n' for sentence in preprocess.normAndTokenize(line, min_sentence_len=2, split_sentences=True)])
            if len(sentences) >= 10000:
                outfile.writelines(sentences)
                sentences = []
        #文件扫描结束
        if len(sentences) > 0:
            outfile.writelines(sentences)

    outfile.close()

MIN_RULE_TOKEN_COUNT = 10000
def asr_replace_func(input_file_path, output_file_dir, ref_hypos_map):
    if not ref_hypos_map:
        ref_hypos_map = {}

    input_file_name = os.path.basename(input_file_path)
    if not os.path.isdir(output_file_dir):
        os.makedirs(output_file_dir)
    outfile = codecs.open(output_file_dir + '/std_' + input_file_name, 'w', 'utf-8')

    with codecs.open(input_file_path, 'r', 'utf-8') as myfile:
        sentences = []
        for line in myfile:
            if len(line) == 0 or line.isspace():
                continue
            fields = line.split('\t')
            if len(fields) != 2:
                continue
            orig_sentence = fields[0]
            hypo_sentence = fields[1]
            if len(orig_sentence) == 0 or len(hypo_sentence) == 0:
                continue
            # 不分句，这样正确语料才能包含，,、尽可能展示转写过程可能的正确语句
            orig_sentences = preprocess.normAndTokenize(orig_sentence, min_sentence_len=2, split_sentences=True)
            hypo_sentences = preprocess.normAndTokenize(hypo_sentence, min_sentence_len=2, split_sentences=True)
            if len(orig_sentences) == 0 or len(hypo_sentences) == 0 or len(orig_sentences) != len(hypo_sentences):
                continue

            for orig_sentence, hypo_sentence in zip(orig_sentences, hypo_sentences):
                marked_hypos = ref_hypos_map.get(orig_sentence, [])
                if hypo_sentence in marked_hypos:
                    continue #跳过已经标注过的语料
                sentences.append(orig_sentence + '\t' + hypo_sentence + '\n')
                for token in orig_sentence.split():
                    # preprocess.normAndTokenize() 方法会统计各个token出现次数
                    count = preprocess.tokens_count_dict.get(token, 0)
                    if count >= MIN_RULE_TOKEN_COUNT:
                        continue
                    # token一定要出现在词表中
                    preprocess.tokens_count_dict[token] = MIN_RULE_TOKEN_COUNT + count
                for token in hypo_sentence.split():
                    # preprocess.normAndTokenize() 方法会统计各个token出现次数
                    count = preprocess.tokens_count_dict.get(token, 0)
                    if count >= MIN_RULE_TOKEN_COUNT:
                        continue
                    # token一定要出现在词表中
                    preprocess.tokens_count_dict[token] = MIN_RULE_TOKEN_COUNT + count
            if len(sentences) >= 10000:
                outfile.writelines(sentences)
                sentences = []
        #文件扫描结束
        if len(sentences) > 0:
            outfile.writelines(sentences)

    outfile.close()

def preprocess_sports_asr(root_dir, input_base_dir, output_base_dir):
    for root,dirs,files in os.walk(root_dir):
        for file in files:
            if not file.endswith(".txt"):
                continue
            if file.startswith("std_"): #跳过输出文件
                continue
            file_path = os.path.join(root, file)
            common_sub_dir = root.replace(input_base_dir, "").lstrip("/").lstrip("\\")
            output_file_dir = os.path.join(output_base_dir, common_sub_dir)
            asr_replace_func(file_path, output_file_dir, None) #运动语料出现的词语必须出现
            print(f"{file_path} has been processed.")

def merge_preprocess_aiui_football_asr(root_dir, input_base_dir, output_base_dir):
    # 存储之前龙猫标注好的语料
    file_name_ref_hypos_map = {}
    for root,dirs,files in os.walk(output_base_dir):
        for file in files:
            if not file.endswith(".txt"):
                continue
            if not file.startswith("std_"): #跳过未标准化的文件
                continue
            ref_hypos_map = {}
            std_asr_file_path = os.path.join(root, file)
            with codecs.open(std_asr_file_path, 'r', 'utf-8') as myfile:
                for line in myfile:
                    fields = line.split("\t")
                    if len(fields) != 2:
                        continue
                    ref = fields[0].strip()
                    hypo = fields[1].strip()
                    hypos = ref_hypos_map.get(ref, [])
                    if hypo not in hypos:
                        hypos.append(hypo)
                    ref_hypos_map[ref] = hypos
            file_name_ref_hypos_map[file[4:]] = ref_hypos_map
    # 将ASR输出语料和龙猫标注语料合并
    for root,dirs,files in os.walk(root_dir):
        for file in files:
            if not file.endswith(".txt"):
                continue
            if file.startswith("std_"): #跳过输出文件
                continue
            if file not in file_name_ref_hypos_map:
                print("unknown aiui football asr file: " + file)
                continue
            ref_hypos_map = file_name_ref_hypos_map[file]
            file_path = os.path.join(root, file)
            common_sub_dir = root.replace(input_base_dir, "").lstrip("/").lstrip("\\")
            output_file_dir = os.path.join(output_base_dir, common_sub_dir)
            asr_replace_func(file_path, output_file_dir, ref_hypos_map) #运动语料出现的词语必须出现
            print(f"{file_path} has been processed.")

def run():
    # 用强制纠错规则中的词初始化词表
    # correction_rule_files = [r'/root/fastcorrect/scripts/std_force_correction_rules.txt',
    #                          r'/root/fastcorrect/scripts/hard_force_correction_rules.txt']
    correction_rule_files = [r'./force_correction_rules.txt',
                             r'./hard_force_correction_rules.txt']
    for correction_rule_file in correction_rule_files:
        with open(correction_rule_file, 'r', encoding='utf-8') as infile:
            for rule in infile:
                fields = rule.split('\t')
                orig_words = fields[0].strip()
                orig_sentences = preprocess.normAndTokenize(orig_words, min_sentence_len=1)
                error_words = fields[1].strip()
                error_sentences = preprocess.normAndTokenize(error_words, min_sentence_len=1)
                sentences = orig_sentences
                sentences.extend(error_sentences)
                tokens = []
                for sentence in sentences:
                    tokens.extend(sentence.split())
                for token in tokens:
                    tmp_token = token.upper()
                    if tmp_token != token: #同时包含大小写字母，则统一转换为小写
                        tmp_token = token.lower()
                        count = preprocess.tokens_count_dict.get(tmp_token, 0)
                    else: #否则统一用大写
                        count = preprocess.tokens_count_dict.get(tmp_token, 0)
                    if count >= MIN_RULE_TOKEN_COUNT:
                        continue
                    # 强制纠错中的token一定要出现在词表中
                    preprocess.tokens_count_dict[tmp_token] = MIN_RULE_TOKEN_COUNT + count + 1

    #处理各运动项目ASR转写出的语料
    preprocess_sports_asr(sports_asr_root_dir, sports_asr_root_dir, std_sports_asr_root_dir)
    #将 aiui_football转写语料和龙猫标注语料合并
    merge_preprocess_aiui_football_asr(aiui_football_asr_root_dir, aiui_football_asr_root_dir, std_aiui_football_asr_root_dir)
    #处理各wiki文件
    # for data_name in wiki_data_names:
    #     wiki_replace_func(os.path.join(wiki_data_path, data_name), std_wiki_data_root_dir)
    #     print('{0} has been processed.'.format(data_name))

    #保存词表
    with codecs.open(os.path.join(std_sports_asr_root_dir, 'dict.CN_char.txt'), 'w', 'utf-8') as dictfile:
        sorted_token_counts = sorted(preprocess.tokens_count_dict.items(), key= lambda  x:x[1], reverse=True)
        tokens = []
        count = 0
        for token_count in sorted_token_counts:
            tokens.append(token_count[0] + " " + str(token_count[1]) +'\n')
            if len(tokens) > 10000:
                dictfile.writelines(tokens)
                tokens = []
            count += 1
        if len(tokens) > 0:
            dictfile.writelines(tokens)


if __name__ == '__main__':
    run()

