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
from app import restore_hotwords

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

model_name_or_path = "/root/fc/models/finetune.ftb4"
# model_name_or_path = r'C:\Users\OS\Downloads'
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

def correct(text):
    logger.info("text to be corrected: " + text)
    try:
        start = time.time()
        sentences = preprocess.normAndTokenize(text, min_sentence_len=1, split_sentences=True)
        corrections = []
        for sentence in sentences:
            tokens = sentence.split()
            if len(tokens) >= 2:
                bin_text = transf_gec.binarize(sentence)
                batched_hypos, wer_dur_pred = transf_gec.generate(bin_text, iter_decode_max_iter=iter_decode_max_iter)
                pred_tokens = []
                for hypos in batched_hypos:
                    #decoded_tokens = transf_gec.decode(hypos[0]['tokens'])
                    pred_tokens = transf_gec.string(hypos[0]['tokens']).split()
                    break
                logger.info(f"tokens and werdur: {', '.join(token + ':' + str(werdur) for (token, werdur) in zip(tokens, wer_dur_pred))}")
                logger.info(f"tokens predicted: {pred_tokens}")
                pred_tokens, wer_dur_pred = restore_hotwords.resotre(tokens, pred_tokens, wer_dur_pred)
                logger.info(f"tokens predicted2: {pred_tokens}")
            else:
                pred_tokens = [sentence.strip()]
                wer_dur_pred = [1]
            correction = {"tokens": tokens, "fc_tokens": pred_tokens, "wer_dur_pred": wer_dur_pred}
            corrections.append(correction)

        end = time.time()
        cost = str(round(end - start, ndigits=3))
        logger.info(f"cost {cost} seconds\n")
        return corrections
    except Exception as e:
        logger.error(str(e), exc_info=True)
        return []

#correct("卡塔尔世界杯")

webapp = Flask(__name__)
@webapp.route('/update_hotwords', methods=['POST'])
def update_hotwords():
    requst_body = request.get_data(as_text=True)
    request_json = json.loads(requst_body)
    hotwords_new = request_json['hotwords_new']
    hotwords_delete = request_json['hotwords_delete']
    update_result = restore_hotwords.update_hotwords(hotwords_new, hotwords_delete)

    result = {}
    result['result_code'] = '200'
    result["message"] = 'ok'
    if not update_result:
        result['result_code'] = '300'
        result["message"] = 'updating'
    json_string = json.dumps(result, ensure_ascii=False)
    response = make_response(json_string)
    response.headers['Content-Type'] = "application/json"
    return response

@webapp.route('/dump_hotwords', methods=['POST'])
def dump_hotwords():
    hotwords = restore_hotwords.dump_hotwords()

    result = {}
    result['result_code'] = '200'
    result["hotwords"] = hotwords
    json_string = json.dumps(result, ensure_ascii=False)
    response = make_response(json_string)
    response.headers['Content-Type'] = "application/json"
    return response

@webapp.route('/fast_correct', methods=['POST'])
def fast_correct():
    # parse request body
    # requst_body = request.get_data(as_text=True).decode('utf-8')
    requst_body = request.get_data(as_text=True)
    request_json = json.loads(requst_body)
    text = request_json['text']
    corrections = correct(text)
    if corrections and len(corrections) > 0:
        result = {}
        result['result_code'] = '200'
        result["corrections"] = corrections
        json_string = json.dumps(result, ensure_ascii=False)
        response = make_response(json_string)
        response.headers['Content-Type'] = "application/json"
        return response

    else:
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


