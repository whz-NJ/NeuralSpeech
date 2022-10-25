import os
from scripts import preprocess

corpus_root_dir = "./sports_corpus"
asr_corpus_root_dir = "./noised_sports_corpus"
merged_corpus_root_dir = "./merged_noised_sports_corpus"

def loadAllCorpus():
    for root,dirs,files in os.walk(corpus_root_dir):
        if root.find('五大联赛') == -1 and root.find('世界杯') == -1:#只处理足球相关语料
            continue
        for file in files:
            if file.find('滑雪') != -1 or file.find('雪车') != -1: #只处理足球相关语料
                continue
            corpus_file_path = os.path.join(root, file)
            common_path = root.replace(corpus_root_dir, "")
            asr_corpus_file_dir = os.path.join(common_path, asr_corpus_root_dir)
            asr_corpus_file_path = os.path.join(asr_corpus_file_dir, file)

            asr_corpus_file = open(asr_corpus_file_path, 'r', encoding='UTF-8')
            asr_corpus_map = {}
            for asr_corpus_line in asr_corpus_file.readlines():
                fileds = asr_corpus_line.split("\t")
                if len(fileds) == 2:
                    corpus = fileds[0].strip()
                    asr_corpus = fileds[1].strip()
                    asr_corpus_set = asr_corpus_map.get(corpus, set())
                    asr_corpus_set.add(asr_corpus)
                    asr_corpus_map[corpus] = asr_corpus_set

            corpus_file = open(corpus_file_path, 'r', encoding='UTF-8')
            for corpus_line in corpus_file.readlines():
                corpus_line = corpus_line.strip()
                sentences = preprocess.normAndTokenize(corpus_line, min_sentence_len=2, split_sentences=True, end_with_seperator=True)
                paragraphs = [[]]
                for sentence in sentences:
                    seperator = sentence[-1:]
                    corpus = sentence[0: -1]
                    if seperator not in preprocess.seperator_map:
                        seperator = ""
                        corpus = sentence
                    asr_corpus_set = asr_corpus_map.get(corpus, set())
                    for asr_corpus in asr_corpus_set:
                        for paragraph in paragraphs:
                            paragraph.extend([asr_corpus + seperator])



