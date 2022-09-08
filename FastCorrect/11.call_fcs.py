import sys
import argparse
import os.path
import codecs
sys.path.append("/root/fastcorrect/FC_utils")

from fairseq import utils
utils.import_user_module(argparse.Namespace(user_dir='./FastCorrect'))
from FastCorrect.fastcorrect_model import FastCorrectModel
input_dir = r'/root/lxm_corpus'
epoch = 'best'
#epoch = '11'
model_name_or_path = "/root/fastcorrect/models/finetune"
#model_name_or_path = "/root/fastcorrect/models/pretrain"
iter_decode_max_iter = 0
edit_thre = 0
checkpoint_file = f"checkpoint_{epoch}.pt"
#checkpoint_file = f'fastcorrect_pretrain.pt'
# the model will only use the dictionary in data_name_or_path.
data_name_or_path = "/root/fastcorrect/data/werdur_data_aishell.bin" # <Path-to-AISHELL1-Training-Binary-Data>
bpe = "sentencepiece"
sentencepiece_model = "/root/fastcorrect/sentencepiece/FastCorrect_zhwiki_sentencepiece.model" # <path-to-sentencepiece_model>, you can use arbitrary sentencepiece for our pretrained model since it is a char-level model

transf_gec = FastCorrectModel.from_pretrained(model_name_or_path, checkpoint_file=checkpoint_file, data_name_or_path=data_name_or_path, bpe=bpe, sentencepiece_model=sentencepiece_model)

transf_gec.eval()
transf_gec.cuda()

for root, dirs, files in os.walk(input_dir):
    for file in files:
        if not file.endswith(".txt") or not file.startswith("std_"):
            continue

        asr_result_article_path = os.path.join(input_dir, file)
        asr_result_article_name = os.path.basename(asr_result_article_path)
        asr_result_article_dir = os.path.dirname(asr_result_article_path)
        fc_asr_result_article_name = "fc_" + asr_result_article_name
        fc_asr_result_article_path = os.path.join(asr_result_article_dir, fc_asr_result_article_name)

        asr_result_file = open(asr_result_article_path, 'r', encoding='UTF-8')
        asr_result_lines = []
        for line in asr_result_file:
            asr_result_lines.append(line.strip())
        asr_result_file.close()

        fc_asr_result_lines = []
        for asr_result_line in asr_result_lines:
            try:
                asr_text = " ".join(asr_result_line)
                asr_text = transf_gec.binarize(asr_text)
                batched_hypos = transf_gec.generate(asr_text, iter_decode_max_iter=iter_decode_max_iter)
                translated = [transf_gec.decode(hypos[0]['tokens']) for hypos in batched_hypos][0]

                if isinstance(translated, tuple):
                    translated = translated[0]
                fc_asr_result_lines.append(translated + "\n")

            except Exception as e:
                print(asr_text + "\n")
                raise e
                continue

        with codecs.open(fc_asr_result_article_path, 'w', 'utf-8') as fc_asr_result_file:
            fc_asr_result_file.writelines(fc_asr_result_lines)

