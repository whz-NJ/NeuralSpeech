import sys
import preprocess
import os

# output of add_noise.py
# input_file = r'C:\Code\NeuralSpeech\FastCorrect\noised_std_sports.txt'
# input_file_dir = 'C:\Code\NeuralSpeech\FastCorrect'
# input_file_names = [r'noised_std_sports.txt']
# input_file_dir = '/root/rpus2'
#input_file_names =[r'std_train_noised_corpus.txt', r'std_valid_noised_corpus.txt', r'std_test_noised_corpus.txt']
#input_file_dir = '/root/extracted/AA'
#input_file_dir = '/root/std_sports_corpus_en'
input_file_dir = '/root/std_ftb_sports_corpus_en'
#input_file_names =[r'noised9_std_zh_wiki_00',r'noised9_std_zh_wiki_01',r'noised9_std_zh_wiki_02']
#input_file_names =[r'noised1_std_zh_wiki_00',r'noised1_std_zh_wiki_01',r'noised1_std_zh_wiki_02',
#        r'noised3_std_zh_wiki_00',r'noised3_std_zh_wiki_01',r'noised3_std_zh_wiki_02',
#        r'noised5_std_zh_wiki_00',r'noised5_std_zh_wiki_01',r'noised5_std_zh_wiki_02',
#        r'noised7_std_zh_wiki_00',r'noised7_std_zh_wiki_01',r'noised7_std_zh_wiki_02']
input_file_names = ['train_std_noised_corpus.txt','valid_std_noised_corpus.txt','test_std_noised_corpus.txt']

for input_file_name in input_file_names:
    intput_file_path = os.path.join(input_file_dir, input_file_name)
    output_hypo_file_path = os.path.join(input_file_dir, "hypo_" + input_file_name)
    output_ref_file_path = os.path.join(input_file_dir, "ref_" + input_file_name)

    ref_lines = []
    hypo_lines = []
    with open(intput_file_path, 'r', encoding='utf-8') as infile:
        for line in infile.readlines():
            fields = line.split('\t')
            ref_line = fields[0].strip() + '\n'
            hypo = fields[1].strip() + '\n'
            ref_lines.append(ref_line)
            hypo_lines.append(hypo)

    with open(output_hypo_file_path,"w", encoding='utf-8') as f:
        f.writelines(hypo_lines)

    with open(output_ref_file_path,"w", encoding='utf-8') as f:
        f.writelines(ref_lines)


