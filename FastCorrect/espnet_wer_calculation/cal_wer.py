# encoding: utf-8
import json
import bson
import os
import re
import sys
import glob
import pdb
s1 = {'a', 'b'}

# input_file_dirs=[r'/root/cal_wer/input/hdc/', r'/root/cal_wer/input/qyh/']
# output_file_dirs = [r'/root/cal_wer/output/hdc/', r'/root/cal_wer/output/qyh/']
#
# input_file_dirs=[r'/root/cal_wer/input/test']
# output_file_dirs=[r'/root/cal_wer/output/test']

input_file_dirs=[r'/root/cal_wer/input/whz']
output_file_dirs = [r'/root/cal_wer/output/whz']

seperator_map = {}
for ch in r':：,，;；<>.。！!？?()（）[]【】「」—“”'+"\n":
    seperator_map[ch] = ch
ignored_tokens = set()
for ch in r'{}"':
    ignored_tokens.add(ch)

root_dir = os.getcwd()
sys.path.append(root_dir)

def get_label_asr_output_files():
    for idx in range(len(input_file_dirs)):
        input_dir = input_file_dirs[idx]
        output_dir = output_file_dirs[idx]
        os.chdir(input_dir)
        for asr_file_name in glob.glob(r'*asr.txt'):
            label_file_name = asr_file_name.replace('_asr.txt','')
            label_file_name = label_file_name.replace('-asr.txt', '')
            output_file_name = label_file_name + ".txt"
            label_file_name = label_file_name + ".txt"
            label_file_path = os.path.join(input_dir, label_file_name)
            asr_file_path = os.path.join(input_dir, asr_file_name)
            output_file_path = os.path.join(output_dir, output_file_name)
            yield (label_file_path, asr_file_path, output_file_path)

def get_tokens(line):
    def append_english_digits(append_english=False, append_digits=False, append_cn_digits=False):
        nonlocal tokens, english, digits, cn_digits
        if append_english and len(english) > 0:
            if len(english) > 1:
                if english.upper() != english: #如果单词不是全大写，则转为全小写（统一）
                    english = english.lower()
            else: # 如果是字母，统一用大写
                english = english.upper()
            if english != "***": #跳过 ***
                tokens.append(english)
            english = ''
        if append_digits and len(digits) > 0: #数字分开(否则词典太大)
            tokens.append(digits)
            digits = ''
        if append_cn_digits and len(cn_digits) > 0:
            for digit in cn_digits:
                tokens.append(digit)
            cn_digits = ''
        return True

    tokens = []
    english = ''
    digits = ''
    cn_digits = ''
    line = line.strip()
    idx = 0
    while idx < len(line):
        ch = line[idx]
        if ch in ignored_tokens:
            idx += 1
            continue
        elif seperator_map.__contains__(ch): #句子分隔符
            append_english_digits(True, True, True) #如果有中文数字，保持原样，不转换为阿拉伯数字
            tokens.append(ch)
        elif '0' <= ch <= '9': #数字
            append_english_digits(append_english=True, append_cn_digits=True) #如果有中文数字，保持原样，不转换为阿拉伯数字
            digits += ch
        elif '\u4e00' <= ch <= '\u9fa5' or '\u3400' <= ch <= '\u4DB5':  # 汉字
            append_english_digits(append_english=True, append_digits=True)
            cn_digits += ch
        elif ch == ' ' or ch == "\t" or ch == '\n' or ch =='\r':
            append_english_digits(True, True, True) #跳过语料中的空格（函数结束前统一加空格作为各token分隔符），中文数字保持原样，不转换为阿拉伯数字
        else: #其他都认为是英文字母
            append_english_digits(append_digits=True, append_cn_digits=True) #中文数字保持原样，不转换为阿拉伯数字
            english += ch
        idx = idx + 1
    #一行扫描结束
    append_english_digits(True, True, True) #中文数字保持原样，不转换为阿拉伯数字
    if len(tokens) > 0:
        tokens.append('\n')
    # pdb.set_trace()
    return tokens

def load_tokens_line_info(txt_file_path):
    idx_seperator_map = {}
    token_idx_map = {}
    tokens_in_file = []
    txt_file = open(txt_file_path, 'r', encoding='UTF-8')
    tokens_cnt = 0
    for txt_line in txt_file:
        txt_line = txt_line.strip().rstrip('"}')
        tokens = []
        if txt_line.find('"text":') >= 0:
            m = re.search(r'\{?"s":\d+\,"e":\d+\,"text":"(\S*)', txt_line, re.IGNORECASE)
            if m:
                text = m.group(1)
                tokens = get_tokens(text)
        else:
            tokens = get_tokens(txt_line)
        if len(tokens) > 0:
            for idx in range(len(tokens)):
                token = tokens[idx]
                if not seperator_map.__contains__(token):
                    token_idx_map[len(tokens_in_file)] = tokens_cnt + idx
                    tokens_in_file.append(token)
                else:
                    idx_seperator_map[tokens_cnt+idx] = token
            #pdb.set_trace()
            tokens_cnt += len(tokens)

    txt_file.close()
    return tokens_in_file, idx_seperator_map, token_idx_map

def create_eval_json_file(label_tokens, asr_tokens, output_file_path):
    tts_objects = {}
    tts_id = str(bson.ObjectId())
    label = "".join(label_tokens)
    asr_result = "".join(asr_tokens)
    output0 = {}
    output0['rec_text'] = asr_result + '<eos>';
    output0['rec_token'] = " ".join(asr_tokens) + ' <eos>'
    output0['text'] = label
    output0['token'] = " ".join(label_tokens)
    output1 = []
    output1.append(output0)
    output = {}
    output['output'] = output1
    tts_objects[tts_id] = output
    result_object = {}
    result_object['utts'] = tts_objects
    result_string = json.dumps(result_object, ensure_ascii=False, indent = 2)

    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(result_string)

def cal_wer(json_file_path):
    result_dir = os.path.dirname(json_file_path)
    tmp_json_file_path = os.path.join(result_dir, "data.1.json")
    cmd = f"cp {json_file_path} {tmp_json_file_path}"
    #print(cmd)
    os.system(cmd)

    cmd = f"{root_dir}/score_sclite.sh {root_dir} {result_dir} {root_dir}/train_sp_units.txt 2>&1 | tail -n 3 > {result_dir}/wer_short.txt"
    #print(cmd)
    os.system(cmd)

    ref_tokens = []
    hyp_tokens = []
    with open(f"{result_dir}/result.txt", 'r', encoding='utf-8') as result_file:
        result_lines = result_file.readlines()
        edit_ops = ''
        edit_op = ''
        ref_hyp_flag = -1
        path_begin = False
        for line in result_lines:
            line = line.strip()
            # if path_begin:
            #     print(line)
            if line.startswith(r"<PATH id"):
                path_begin = True
                edit_ops = ""
                #print("path begin")
                continue
            elif line in {'D', 'S', 'C', 'I'}:
                # print("op find")
                if path_begin:
                    edit_ops = edit_ops + line
                    edit_op = line
                    ref_hyp_flag = 0
                    continue
            elif len(line) ==0 and path_begin: #空行
                if edit_op != "":
                    if ref_hyp_flag == 0:
                        #print("ref emtpy token")
                        ref_hyp_flag = 1
                    elif ref_hyp_flag == 1:
                        ref_hyp_flag = 0
                        #print("hypo emtpy token")
                        edit_op = ""
            elif edit_op != "" and path_begin:
                m = re.search(r'"(\S+)"', line, re.IGNORECASE)
                if m:
                    if ref_hyp_flag == 0:
                        #print("ref token" + m.group(1))
                        ref_tokens.append(m.group(1))
                        ref_hyp_flag = 1
                    elif ref_hyp_flag == 1:
                        #print("hyp token" + m.group(1))
                        hyp_tokens.append(m.group(1))
                        ref_hyp_flag = 0
                        edit_op = ""
        werdurs = [] #源文本经过的编辑操作（变为转写文本）
        lost_hypo_header_len = 0
        for idx in range(len(edit_ops)):
            edit_op = edit_ops[idx]
            if edit_op == 'C': #相同
                if len(werdurs) > 0 or lost_hypo_header_len == 0:
                    werdurs.append(1)
                else:
                    assert ref_tokens[0] != hyp_tokens[0]
                    werdurs.append(-1*lost_hypo_header_len - 1)
            elif edit_op == 'D': #源文本有，转写文本没有
                werdurs.append(0)
            elif edit_op == 'I': #转写文本多出来的，源文本没有对应
                if len(werdurs) > 0:
                    last_wer_dur = werdurs[-1]
                    if last_wer_dur > 0: #转写文本正确，并且后面转写文本多出来 last_wer_dur-1个字
                        werdurs[-1] = last_wer_dur + 1
                    elif last_wer_dur == 0: #源文本需要删除，当前这个token是转写文本多出来的，此时应该是S
                        assert False
                    else: # 转写出来错误，又来一个转写文本token
                        werdurs[-1] = last_wer_dur - 1
                else:
                    lost_hypo_header_len += 1
            elif edit_op == 'S': #转写错误
                if len(werdurs) > 0:
                    werdurs.append(-1)
                else:
                    assert ref_tokens[0] != hyp_tokens[0]
                    werdurs.append(-1*lost_hypo_header_len - 1)
        # print(hyp_tokens)
        # print(len(hyp_tokens))
        # print(werdurs)
        # print(len(werdurs))
        assert len(ref_tokens) == len(werdurs)
        return werdurs

def main():
    def append_del_sub_words(append_del=False, append_sub=False):
        nonlocal delete_words, label_asr_word_pairs, ref_line
        if append_del and delete_words != "":
            ref_line = ref_line + f"【{(delete_words)}:】"
            delete_words = ""
        if append_sub and len(label_asr_word_pairs) != 0:
            ref_words = ""
            hyp_words = ""
            for pair in label_asr_word_pairs:
                ref_words += pair[0]
                hyp_words += pair[1]
            ref_line = ref_line + f"【{ref_words}:{hyp_words}】"
            label_asr_word_pairs = []
    for (label_file_path, asr_file_path, output_file_path) in get_label_asr_output_files():
        print(f'begin to process file: {label_file_path} ...')
        label_tokens, idx_seperator_map, token_idx_map = load_tokens_line_info(label_file_path)
        asr_tokens, _, _ = load_tokens_line_info(asr_file_path)
        sorted_seperator_idx_list = sorted(idx_seperator_map.keys())
        idx_seperator_list = [(idx, idx_seperator_map[idx]) for idx in sorted_seperator_idx_list]
        label_file_name = os.path.basename(label_file_path)
        output_dir = os.path.dirname(output_file_path)
        json_file_name = label_file_name.replace(".txt", ".json")
        json_file_path = os.path.join(output_dir, json_file_name)
        create_eval_json_file(label_tokens, asr_tokens, json_file_path)
        werdurs = cal_wer(json_file_path)
        assert len(werdurs) == len(label_tokens)

        hypo_seperator_idx = 0
        ref_lines = []
        (seperator_idx, seperator) = idx_seperator_list[hypo_seperator_idx]
        ref_line = ""
        hyp_idx = 0
        words_cnt = len(label_tokens)
        sub_words_cnt = 0
        del_words_cnt = 0
        ins_words_cnt = 0
        snt_cnt = 0
        err_snt_cnt = 0
        err_snt_flag = False
        delete_words = "" #将部分正确文本删除（才能得到转写文本）
        label_asr_word_pairs = [] #替换正确文本
        for ref_token_idx in range(len(label_tokens)):
            ref_token = label_tokens[ref_token_idx]
            wer_dur = int(werdurs[ref_token_idx])
            if wer_dur == 1: ##相等
                append_del_sub_words(append_del=True, append_sub=True)
                ref_line = ref_line + ref_token
                hyp_idx += 1
            elif wer_dur == 0: ##在hyp文本中没有对应的字（需把ref文本这个字删除）
                append_del_sub_words(append_sub=True)
                del_words_cnt += 1 #将正确文本的当前token删除
                delete_words = delete_words + ref_token
                err_snt_flag = True
            elif wer_dur == -1: ##ref结果中字变了
                append_del_sub_words(append_del=True)
                sub_words_cnt += 1 #替换了ref文本
                label_asr_word_pairs.append([ref_token, asr_tokens[hyp_idx]])
                err_snt_flag = True
                hyp_idx += 1
            elif wer_dur >= 2: ##ref文本当前字和hyp相同，后面hyp文本多出 wer_dur-1 个字
                append_del_sub_words(append_del=True, append_sub=True)
                ref_line = ref_line + f"【{ref_token}:{''.join(asr_tokens[hyp_idx:hyp_idx + wer_dur])}】"
                ins_words_cnt += (wer_dur -1) #ref文本添加了 wer_dur-1个字
                err_snt_flag = True
                hyp_idx += wer_dur
            else: ##当前字错误，后面ref文本是另外wer_dur个字
                append_del_sub_words(append_del=True, append_sub=True)
                ref_line = ref_line + f"【{ref_token}:{''.join(asr_tokens[hyp_idx:hyp_idx + (-1*wer_dur)])}】"
                sub_words_cnt += 1 #ref文本替换了1个字
                ins_words_cnt += (-1 * wer_dur - 1) #ref文本添加了 wer_dur-1个字
                err_snt_flag = True
                hyp_idx += (-1 * wer_dur)
            token_idx = token_idx_map[ref_token_idx]
            if token_idx == (seperator_idx-1):
                last_seperator_idx = seperator_idx-1;
                while seperator_idx == (last_seperator_idx+1):
                    if seperator != "\n":
                        ref_line += seperator
                    else:
                        append_del_sub_words(append_del=True, append_sub=True)
                        ref_line += seperator
                        ref_lines.append(ref_line)
                        ref_line = ""
                        snt_cnt += 1
                        if err_snt_flag:
                            err_snt_cnt += 1
                        err_snt_flag = False
                    last_seperator_idx = seperator_idx
                    hypo_seperator_idx += 1
                    if(hypo_seperator_idx < len(idx_seperator_list)):
                        (seperator_idx, seperator) = idx_seperator_list[hypo_seperator_idx]
        assert hyp_idx == len(asr_tokens)

        if len(ref_line) > 0:
            ref_lines.append(ref_line)
        err_words_cnt = sub_words_cnt + del_words_cnt + ins_words_cnt

        statistics_result = [f"#Snt={snt_cnt} #Wrd={words_cnt}\n"]
        statistics_result.append(f"Sub Rate={(sub_words_cnt*100.0/words_cnt):.3f} Del Rate={(del_words_cnt*100.0/words_cnt):.3f} Ins Rate={(ins_words_cnt*100.0/words_cnt):.3f}\n")
        statistics_result.append(f"Snt Correct Rate={(100 - err_snt_cnt*100.0/snt_cnt):.3f} Word Correct Rate={(100 - err_words_cnt * 100.0 / words_cnt):.3f}\n")
        for statistics_line in statistics_result:
            print(statistics_line.strip())
        print("\n")
        with open(output_file_path,"w", encoding='utf-8') as f:
            f.writelines(statistics_result)
            f.write("\n")
            f.writelines(ref_lines)

if __name__ == "__main__":
    main()

