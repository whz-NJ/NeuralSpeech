import os
import json
import codecs
corpus_root_dir=r'C:\工作任务\AIUI\NLP模型测试\侯德成语料\比赛文本'

for root, dirs, files in os.walk(corpus_root_dir):
    for file in files:
        if not file.endswith(".json"):
            continue
        json_object = {}
        with codecs.open(os.path.join(root, file), 'r', encoding="utf-8") as json_file:
            j = json.load(json_file)
            jj = j["utts"]
            for x in jj:
                jj[x]["output"][0]["text"] = "".join(jj[x]["output"][0]["text"].split())
                jj[x]["output"][0]["token"] = " ".join(jj[x]["output"][0]["text"])
            json_object["utts"] = jj
        with codecs.open(os.path.join(root, file), 'w', encoding="utf-8") as json_file:
            json_string = json.dumps(json_object, ensure_ascii=False, indent=2)
            json_file.write(json_string)

