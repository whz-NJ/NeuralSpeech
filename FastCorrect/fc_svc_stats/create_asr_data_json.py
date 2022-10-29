import os
import json
import bson
import codecs
from scripts import preprocess

corpus_root_dir=r'C:\工作任务\AIUI\NLP模型测试\侯德成语料2'

asr_file_names = ["原始字幕_10_8云达不莱梅vs门兴格拉德巴赫.txt", "原始字幕_10_8国际米兰vs巴塞罗那.txt", "原始字幕_10_8拜仁慕尼黑vs勒沃库森.txt",
                  "原始字幕_10_8本菲卡vs巴黎圣日耳曼.txt", "原始字幕_10_8欧塞尔vs布雷斯特.txt", "原始字幕_10_8科隆vs多特蒙德.txt",
                  "原始字幕_10_9兰斯vs巴黎圣日耳曼.txt", "原始字幕_10_9切尔西vs狼队.txt", "原始字幕_10_9多特蒙德vs拜仁慕尼黑.txt", "原始字幕_10_9美因茨vsRB莱比锡.txt"]
ref_file_names = ["转写后标注字幕_【厂家】10_8云达不莱梅VS门兴格拉德巴赫.txt", "转写后标注字幕_【厂家】10_8国际米兰vs巴塞罗那.txt", "转写后标注字幕_【厂家】10_8拜仁慕尼黑vs勒沃库森.txt",
                  "转写后标注字幕_【厂家】10_8本菲卡vs巴黎圣日耳曼.txt", "转写后标注字幕_【厂家】10_8欧塞尔vs布雷斯特.txt", "转写后标注字幕_【厂家】10_8科隆vs多特蒙德.txt",
                  "转写后标注字幕_【厂家】10_9兰斯vs巴黎圣日耳曼.txt", "转写后标注字幕_【厂家】10_9切尔西vs狼队.txt", "转写后标注字幕_【厂家】10_9多特蒙德vs拜仁慕尼黑.txt", "转写后标注字幕_【厂家】10_9美因茨vsRB莱比锡.txt"]

asr_objects = {}
asr_objects["utts"] = {}
for asr_file_name,ref_file_name in zip(asr_file_names, ref_file_names):
    asr_file = codecs.open(os.path.join(corpus_root_dir, asr_file_name), 'r', 'utf-8')
    ref_file = codecs.open(os.path.join(corpus_root_dir, ref_file_name), 'r', 'utf-8')
    asr_lines = asr_file.readlines()
    ref_lines = ref_file.readlines()

    for asr_line,ref_line in zip(asr_lines, ref_lines):
        asr_sentences = preprocess.normAndTokenize(asr_line,min_sentence_len=3,split_sentences=True)
        ref_sentences = preprocess.normAndTokenize(ref_line,min_sentence_len=3,split_sentences=True)
        if len(asr_sentences) != len(ref_sentences):
            continue
        for asr_sentence,ref_sentence in zip(asr_sentences, ref_sentences):
            id = str(bson.ObjectId())
            output0 = {'rec_text': "".join(asr_sentence.split()), 'rec_token': " ".join(asr_sentence.split()),
                       'text': "".join("".join(ref_sentence.split())),
                       'token': " ".join(ref_sentence.split())}
            output1 = [output0]
            output = {'output': output1}
            asr_objects["utts"][id] = output

asr_string = json.dumps(asr_objects, ensure_ascii=False, indent=2)
asr_json_file_name = f"data_merged_{len(asr_file_names)}.json"
with open(os.path.join(corpus_root_dir, asr_json_file_name), "w", encoding='utf-8') as f:
    f.write(asr_string)
