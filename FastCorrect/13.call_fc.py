import sys
import argparse
import bson
import os.path
import codecs
import json
sys.path.append("/root/fastcorrect/FC_utils")

from fairseq import utils
utils.import_user_module(argparse.Namespace(user_dir='./FastCorrect'))
from FastCorrect.fastcorrect_model import FastCorrectModel

#corpus_article_path = r'/root/asr/articles/［世界杯］1_4决赛：乌拉圭VS法国.txt'
#asr_result_article_path = r'/root/asr/articles/std_［世界杯］1_4决赛：乌拉圭VS法国_asr.txt'
#corpus_article_path = r'/root/fastcorrect/models/finetune.ftb/results_best_asr_b0_t0.0/test/ref.txt'
asr_result_article_path = r'/root/fastcorrect/models/finetune.ftb/results_best_asr_b0_t0.0/test/asr.txt'
epoch = 'best'

model_name_or_path = "/root/fastcorrect/models/finetune.ftb"
iter_decode_max_iter = 0
edit_thre = 0
checkpoint_file = f"checkpoint_{epoch}.pt"
# the model will only use the dictionary in data_name_or_path.
data_name_or_path = "/root/std_ftb_sports_corpus_en.bin" # <Path-to-AISHELL1-Training-Binary-Data>
bpe = "sentencepiece"
sentencepiece_model = "/root/fastcorrect/sentencepiece/FastCorrect_zhwiki_sentencepiece.model" # <path-to-sentencepiece_model>, you can use arbitrary sentencepiece for our pretrained model since it is a char-level model

transf_gec = FastCorrectModel.from_pretrained(model_name_or_path, checkpoint_file=checkpoint_file, data_name_or_path=data_name_or_path, bpe=bpe, sentencepiece_model=sentencepiece_model)

transf_gec.eval()
transf_gec.cuda()

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
for asr_text in asr_result_lines:
    try:
        asr_text = " ".join(asr_text)
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


