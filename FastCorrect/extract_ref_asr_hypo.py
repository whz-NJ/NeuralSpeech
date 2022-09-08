ref_hypo_data_file='/root/fastcorrect/models/finetune.ftb/results_best_asr_b0_t0.0/test/data.json'
ref_asr_data_file='/root/std_ftb_sports_corpus_en/test/data.json'

import json
import codecs
import os
hypo_text_list = []
ref_text_list = []
asr_text_list = []
output_file_dir = os.path.dirname(ref_hypo_data_file)

with codecs.open(ref_hypo_data_file, "r", encoding="utf-8") as f:
    j = json.load(f)
    for x in j["utts"]:
        rec_text = j["utts"][x]["output"][0]["rec_text"]
        hypo_text = rec_text + "\n"
        text = j["utts"][x]["output"][0]["text"]
        ref_text = text + "\n"
        hypo_text_list.append(hypo_text)
        ref_text_list.append(ref_text)

with codecs.open(ref_asr_data_file, "r", encoding="utf-8") as f:
    j = json.load(f)
    for x in j["utts"]:
        rec_text = j["utts"][x]["output"][0]["rec_text"]
        asr_text = rec_text[:-5] + "\n" #丢弃最后的 <eos>
        asr_text_list.append(asr_text)

with open(os.path.join(output_file_dir, "ref.txt"), "w", encoding='utf-8') as f:
    f.writelines(ref_text_list)

with open(os.path.join(output_file_dir, "hypo.txt"), "w", encoding='utf-8') as f:
    f.writelines(hypo_text_list)

with open(os.path.join(output_file_dir, "asr.txt"), "w", encoding='utf-8') as f:
    f.writelines(asr_text_list)
