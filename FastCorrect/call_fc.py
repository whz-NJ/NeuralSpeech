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

corpus_article_path = r'/root/asr/articles/［世界杯］1_4决赛：乌拉圭VS法国.txt'
asr_result_article_path = r'/root/asr/articles/std_［世界杯］1_4决赛：乌拉圭VS法国_asr.txt'
epoch = 'best'

model_name_or_path = "/root/fastcorrect/models/finetune"
iter_decode_max_iter = 0
edit_thre = 0
checkpoint_file = f"checkpoint_{epoch}.pt"
# the model will only use the dictionary in data_name_or_path.
data_name_or_path = "/root/fastcorrect/data/werdur_data_aishell.bin" # <Path-to-AISHELL1-Training-Binary-Data>
bpe = "sentencepiece"
sentencepiece_model = "/root/fastcorrect/sentencepiece/FastCorrect_zhwiki_sentencepiece.model" # <path-to-sentencepiece_model>, you can use arbitrary sentencepiece for our pretrained model since it is a char-level model

transf_gec = FastCorrectModel.from_pretrained(model_name_or_path, checkpoint_file=checkpoint_file, data_name_or_path=data_name_or_path, bpe=bpe, sentencepiece_model=sentencepiece_model)

transf_gec.eval()
transf_gec.cuda()

asr_result_article_name = os.path.basename(asr_result_article_path)
asr_result_article_dir = os.path.dirname(asr_result_article_path)
fc_asr_result_article_name = "fc_" + asr_result_article_name
fc_asr_result_article_path = os.path.join(asr_result_article_dir, fc_asr_result_article_name)

corpus_article_file = open(corpus_article_path, 'r', encoding='UTF-8')
corpus_lines = []
for line in corpus_article_file:
    corpus_lines.append(line.strip())
corpus_article_file.close()

asr_result_file = open(asr_result_article_path, 'r', encoding='UTF-8')
asr_result_lines = []
for line in asr_result_file:
    asr_result_lines.append(line.strip())
asr_result_file.close()

fc_asr_result_lines = []
asr_eval_dict = {}
fc_asr_eval_dict = {}
asr_eval_dict['utts'] = {}
fc_asr_eval_dict['utts'] = {}
for corpus_text,asr_text in zip(corpus_lines, asr_result_lines):
    try:
        key = str(bson.ObjectId())
        asr_eval_dict["utts"][key] = {}
        asr_eval_dict["utts"][key]['output'] = []
        asr_eval_dict["utts"][key]['output'].append({})
        asr_eval_dict["utts"][key]["output"][0]["rec_text"] = asr_text + "<eos>"
        asr_eval_dict["utts"][key]["output"][0]["rec_token"] = " ".join(asr_text)
        asr_eval_dict["utts"][key]["output"][0]["text"] = corpus_text
        asr_eval_dict["utts"][key]["output"][0]["token"] = " ".join(corpus_text)

        asr_text = " ".join(asr_text)
        asr_text = transf_gec.binarize(asr_text)
        batched_hypos = transf_gec.generate(asr_text, iter_decode_max_iter=iter_decode_max_iter)
        translated = [transf_gec.decode(hypos[0]['tokens']) for hypos in batched_hypos][0]

        if isinstance(translated, tuple):
            translated = translated[0]
        fc_asr_result_lines.append(translated + "\n")
        fc_asr_eval_dict["utts"][key] = {}
        fc_asr_eval_dict["utts"][key]['output'] = []
        fc_asr_eval_dict["utts"][key]['output'].append({})
        fc_asr_eval_dict["utts"][key]["output"][0]["rec_text"] = translated + "<eos>"
        fc_asr_eval_dict["utts"][key]["output"][0]["rec_token"] = " ".join(translated)
        fc_asr_eval_dict["utts"][key]["output"][0]["text"] = corpus_text
        fc_asr_eval_dict["utts"][key]["output"][0]["token"] = " ".join(corpus_text)

    except Exception as e:
        print(asr_text + "\n")
        raise e
        continue

with codecs.open(fc_asr_result_article_path, 'w', 'utf-8') as fc_asr_result_file:
    fc_asr_result_file.writelines(fc_asr_result_lines)

json.dump(asr_eval_dict, open(os.path.join(asr_result_article_dir, 'asr_data.json'), 'w', encoding='utf-8'), indent=2, sort_keys=False, ensure_ascii=False)
json.dump(fc_asr_eval_dict, open(os.path.join(asr_result_article_dir, 'fc_asrdata.json'), 'w', encoding='utf-8'), indent=2, sort_keys=False, ensure_ascii=False)

