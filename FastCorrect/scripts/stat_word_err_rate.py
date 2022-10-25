import os
import signal
import cal_wer_dur_v1

input_file_dir=r'/root/std_noised_aiui_football2/五大联赛'


def set_timeout(num, callback):
    def wrap(func):
        def handle(signum, frame):
            raise RuntimeError

        def to_do(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handle)
                signal.alarm(num)
                # print('start alarm signal.')
                r = func(*args, **kwargs)
                # print('close alarm signal.')
                signal.alarm(0)  #
                return r
            except RuntimeError as e:
                callback()

        return to_do

    return wrap

def after_timeout():
    pass

#以ref_sen为基准，统计预测错误的字数和预测对的字数
@set_timeout(30, after_timeout)  # 30s limitation for align
def cnt_err_ok_words(hypo_sen, ref_sen):
    werdur, _ = cal_wer_dur_v1.calculate_wer_dur_v1(hypo_sen, ref_sen, return_path_only=False)
    # assert len(werdur) == len(hypo_sen)
    # assert len(ref_sen) == sum([abs(i) for i in werdur])
    err_words_cnt = sum([(i < 0) and (-1*i) or 0 for i in werdur])
    return err_words_cnt, len(ref_sen)-err_words_cnt

names_list=os.listdir(input_file_dir)
for name in names_list:
    file_path = os.path.join(input_file_dir, name)
    if not os.path.isfile(file_path):
        print(f"ignore dir {file_path}")
        continue
    file_name = name
    if file_name.startswith("std_") and file_name.endswith("_asr.txt"):
        err_words_cnt = 0
        ok_words_cnt = 0
        with open(file_path, 'r', encoding='utf-8') as corpus_file:
            for line in corpus_file.readlines():
                fields = line.split("\t")
                if len(fields) != 2:
                    continue
                ref = fields[0]
                hypo = fields[1]
                err_cnt,ok_cnt = cnt_err_ok_words(hypo, ref)
                err_words_cnt += err_cnt
                ok_words_cnt += ok_cnt
        if ok_words_cnt > 0:
            wer = err_words_cnt / (float)(err_words_cnt + ok_words_cnt)
            print(f"{file_name} wer={wer:.3f}")


