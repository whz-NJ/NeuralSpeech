# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

EXP_HOME=$(cd `dirname $0`; pwd)/..
cd $EXP_HOME

cd $EXP_HOME

#DATA_PATH=/root/asr.bin   #<Path-to-Binary-Data>
#DATA_PATH=/root/sports_aishell_corpus.bin
#DATA_PATH=/root/extracted/AA.bin
#DATA_PATH=/root/std_sports_corpus_en.bin
DATA_PATH=/root/std_ftb_sports_corpus_en.bin

export PYTHONPATH=$EXP_HOME/FastCorrect:$PYTHONPATH

# output of split_train_valid_test.py
#TEXT=/root/asr   #<Path-to-Data-with-duration>
#TEXT=/root/sports_aishell_corpus
#TEXT=/root/extracted/AA
#TEXT=/root/std_sports_corpus_en
TEXT=/root/std_ftb_sports_corpus_en
# contains train.zh_CN, train.zh_CN_tgt, valid.zh_CN, valid.zh_CN_tgt
# *.zh_CN is indeed the *.src.werdur.full in alignment result
# *.zh_CN_tgt is indeed the *.tgt in alignment result
#dict_path=/root/fastcorrect/data/werdur_data_aishell/dict.CN_char.txt  #<path-to-dictionary>
dict_path=/root/fastcorrect/dictionary/short.dict.CN_char.txt

#We use shared dictionary extracted from training corpus

python $EXP_HOME/FC_utils/preprocess_fc.py --source-lang zh_CN --target-lang zh_CN_tgt \
    --task translation \
    --trainpref $TEXT/train --validpref $TEXT/valid \
    --padding-factor 8 \
    --src-with-werdur \
    --destdir ${DATA_PATH} \
    --srcdict ${dict_path} --tgtdict ${dict_path} \
    --workers 20
