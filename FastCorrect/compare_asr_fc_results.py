import codecs
import json
import os

#asr_result_file_path='./eval_data/test/data.json'
asr_result_file_path='/root/fastcorrect/asr_eval_data/test0/data.json'
fc_asr_result_file_path='/root/fastcorrect/models/finetune/results_best_asr_b0_t0.0/test/data.json'

def load_error_corrects(result_file_path, errors_map, corrects_map):
    with codecs.open(result_file_path, encoding="utf-8") as result_file:
        result_json = json.load(result_file)
        for key in result_json["utts"].keys():
            item = result_json["utts"][key]["output"][0]
            rec_text = item["rec_text"].replace("<eos>", "")
            text = item["text"]
            if rec_text != text:
                errors_map[text] = rec_text
            else:
                corrects_map[text] = rec_text

for file_path in [asr_result_file_path, fc_asr_result_file_path]:
    errors_map = {}
    corrects_map = {}
    load_error_corrects(file_path, errors_map, corrects_map)
    sorted_errors = sorted(errors_map.items(), key=lambda x: x[0])
    sorted_corrects = sorted(corrects_map.items(), key=lambda x: x[0])

    errors_file_path = os.path.join(os.path.dirname(file_path), "errors.tsv")
    with open(errors_file_path, "w", encoding='utf-8') as errors_file:
        for error in sorted_errors:
            errors_file.write(error[0] + "\t" + error[1] + "\n")

    corrects_file_path = os.path.join(os.path.dirname(file_path), "corrects.tsv")
    with open(corrects_file_path, "w", encoding='utf-8') as corrects_file:
        for correct in sorted_corrects:
            corrects_file.write(correct[0] + "\t" + correct[1] + "\n")

