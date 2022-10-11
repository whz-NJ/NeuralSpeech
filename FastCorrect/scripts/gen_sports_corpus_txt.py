import os

from docx import Document
import win32com
import win32com.client
import preprocess

corpus_root_dir = "../sports_corpus"
processed_corpus_root_dir = "../sports_corpus3"
# corpus_root_dir = r"C:\Users\OS\Desktop\足球"
# processed_corpus_root_dir = r"C:\Users\OS\Desktop\足球2"

def replace_dot_path(path):
    result = ""
    pwd = os.getcwd()
    if path.startswith(".."):
        ppwd = os.path.dirname(pwd)
        result = os.path.join(ppwd, path[3:]) #子目录不能包含最开始的 /
    elif path.startswith("."):
        result = os.path.join(pwd, path[2:]) #子目录不能包含最开始的 /
    else:
        result = path
    return result
corpus_root_dir = replace_dot_path(corpus_root_dir)
processed_corpus_root_dir = replace_dot_path(processed_corpus_root_dir)

def open_docx_wps(path):
    try:
        doc = Document(path) #先用docx打开
    except: #打开失败，用wps打开
        try:
            wps = win32com.client.gencache.EnsureDispatch('kwps.application')
        except:
            wps = win32com.client.gencache.EnsureDispatch('wps.application')
        doc = wps.Documents.Open(path)
        pwd = os.getcwd()
        tmp_dir = os.path.join(pwd, 'tmp')
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        new_path = os.path.join(tmp_dir, os.path.basename(path))
        doc.SaveAs2(new_path, 12) #另存为新的docx文件
        wps.Documents.Close(win32com.client.constants.wdDoNotSaveChanges)
        wps.Quit
        os.remove(path) #老的docx文件删除
        os.rename(new_path, path) #文件还原到源语料路径下
    doc = Document(path) #再次尝试用docx打开
    return doc

def loadAllCorpus(root_dir):
    for root,dirs,files in os.walk(root_dir):
        if root.find('五大联赛') == -1 and root.find('世界杯') == -1:#只处理足球相关语料
            continue
        for file in files:
            if file.find('滑雪') != -1 or file.find('雪车') != -1: #只处理足球相关语料
                continue
            file_path = os.path.join(root, file)
            saved_corpus_path = file_path.replace(corpus_root_dir, processed_corpus_root_dir)
            saved_corpus_dir = os.path.dirname(saved_corpus_path)
            if not os.path.exists(saved_corpus_dir):
                os.makedirs(saved_corpus_dir)

            if saved_corpus_path.endswith(".docx"):
                saved_corpus_path = saved_corpus_path[:-4] + "txt"
            elif saved_corpus_path.endswith(".doc"):
                saved_corpus_path = saved_corpus_path[:-3] + "txt"
            if os.path.exists(saved_corpus_path): #跳过已经处理过的文件
                continue

            corpus_list = []
            if file.endswith(".doc"):
                try:
                    wps = win32com.client.gencache.EnsureDispatch('kwps.application')
                except:
                    wps = win32com.client.gencache.EnsureDispatch('wps.application')
                print("opening doc file: " + file_path)
                doc = wps.Documents.Open(file_path)
                new_file_path = file_path[:-3] + "docx"
                doc.SaveAs2(new_file_path, 12)
                #doc.Close()
                #wps.Documents.Close()
                wps.Documents.Close(win32com.client.constants.wdDoNotSaveChanges)
                wps.Quit
                os.remove(file_path)
                file_path = new_file_path
            if file_path.endswith(".docx"):
                doc = open_docx_wps(file_path)
                for paragraph in doc.paragraphs[1:]:
                    sentences = preprocess.normAndTokenize(paragraph.text, min_sentence_len=2, split_sentences=True)
                    for sentence in sentences:
                        sentence = sentence.replace(" ", "")
                        corpus_list.append(sentence + "\n")
                #doc.Close()
            elif file_path.endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as infile:
                    for line in infile.readlines():
                        sentences = preprocess.normAndTokenize(line, min_sentence_len=2, split_sentences=True)
                        for sentence in sentences:
                            sentence = sentence.replace(" ", "")
                            corpus_list.append(sentence + "\n")
            with open(saved_corpus_path, 'w', encoding='utf-8') as outfile:
                outfile.writelines(corpus_list)
loadAllCorpus(corpus_root_dir)


