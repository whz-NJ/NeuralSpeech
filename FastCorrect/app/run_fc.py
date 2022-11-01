# -*- coding: utf-8 -*-
import json
import sys
import argparse
import time
from flask import Flask
from flask import request, make_response
from loggers import bs_logger as logger
from app.config import *
from scripts import preprocess

#sys.path.append("/root/fastcorrect/FC_utils")
sys.path.append("./FC_utils")

from fairseq import utils
utils.import_user_module(argparse.Namespace(user_dir='./FastCorrect'))
from FastCorrect.fastcorrect_model import FastCorrectModel

epoch = 'best'
if EPOCH:
    epoch = EPOCH
logger.info(f'FastCorrect server with epoch {epoch} starting ...')

if 1 == GPU_INDEX_ON_OFF:
    os.environ["CUDA_VISIBLE_DEVICES"] = str(GPU_DEVICE)

# model_name_or_path = "/root/fc/fastcorrect/models/finetune.ftb"
model_name_or_path = "/root/fc/models/finetune.ftb4"
iter_decode_max_iter = 0
edit_thre = 0
checkpoint_file = f"checkpoint{epoch}.pt"
# the model will only use the dictionary in data_name_or_path.
data_name_or_path = "/root/fc/std_noised_sports_corpus4.bin" # <Path-to-AISHELL1-Training-Binary-Data>
bpe = "sentencepiece"
sentencepiece_model = "/root/fc/fastcorrect/sentencepiece/FastCorrect_zhwiki_sentencepiece.model" # <path-to-sentencepiece_model>, you can use arbitrary sentencepiece for our pretrained model since it is a char-level model

transf_gec = FastCorrectModel.from_pretrained(model_name_or_path, checkpoint_file=checkpoint_file, data_name_or_path=data_name_or_path, bpe=bpe, sentencepiece_model=sentencepiece_model)

transf_gec.eval()
if 1 == GPU_INDEX_ON_OFF:
    transf_gec.cuda()

webapp = Flask(__name__)

@webapp.route('/fast_correct', methods=['POST'])
def fast_correct():
    # parse request body
    # requst_body = request.get_data(as_text=True).decode('utf-8')
    requst_body = request.get_data(as_text=True)
    request_json = json.loads(requst_body)
    text = request_json['text']
    logger.info("text to be corrected: " + text)
    try:
        start = time.time()
        sentences = preprocess.normAndTokenize(text, min_sentence_len=1, split_sentences=True)
        corrections = []
        for sentence in sentences:
            tokens = sentence.split()
            if len(tokens) >= 2:
                logger.info(f"tokens to be corrected: {tokens}")
                bin_text = transf_gec.binarize(sentence)
                batched_hypos, wer_dur_pred = transf_gec.generate(bin_text, iter_decode_max_iter=iter_decode_max_iter)
                translated = [transf_gec.decode(hypos[0]['tokens']) for hypos in batched_hypos][0]
                if isinstance(translated, tuple):
                    translated = translated[0]
                pred_tokens = " ".join(translated)
                logger.info(f"tokens predicted: {pred_tokens}")
            else:
                translated = sentence.strip()
                pred_tokens = [translated]
                wer_dur_pred=[1]
            correction = {}
            correction["tokens"] = tokens
            correction["fc_tokens"] = pred_tokens
            correction["wer_dur_pred"] = wer_dur_pred
            corrections.append(correction)

        end = time.time()
        cost = str(round(end - start, ndigits=3))
        logger.info(f"cost {cost} seconds")

        result = {}
        result['result_code'] = '200'
        result["corrections"] = corrections
        json_string = json.dumps(result, ensure_ascii=False)
        response = make_response(json_string)
        response.headers['Content-Type'] = "application/json"
        return response

    except Exception as e:
        logger.error(str(e), exc_info=True)
        logger.error(str(e), exc_info=True)
        result = {}
        result['result_code'] = '300'
        result["fc_text"] = ""
        json_string = json.dumps(result, ensure_ascii=False)
        response = make_response(json_string, ensure_ascii=False)
        response.headers['Content-Type'] = "application/json"
        return response

if __name__ == '__main__':
    webapp.config['JSON_AS_ASCII'] = False
    webapp.run(host=SERVE_HOST, port=SERVE_PORT, threaded=True, debug=False)


