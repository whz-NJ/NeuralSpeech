# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

EXP_HOME=$(cd `dirname $0`; pwd)/..
cd $EXP_HOME

cd $EXP_HOME

DATA_PATH=data/wiki_data.bin   #<Path-to-Binary-Data> 输出目录
export PYTHONPATH=$EXP_HOME/FC_utils:$PYTHONPATH

TEXT=data/wiki_data   #<Path-to-Data-with-duration> 输入目录
# contains train.zh_CN, train.zh_CN_tgt, valid.zh_CN, valid.zh_CN_tgt
# *.zh_CN is indeed the *.src.werdur.full(align_cal_werdur_v2.py 的输出) in alignment result
# *.zh_CN_tgt is indeed the *.tgt(align_cal_werdur_v2.py 的输出) in alignment result
dict_path=data/werdur_data_aishell/dict.CN_char.txt  #<path-to-dictionary>

#max_lines=500000
#rm -rf $TEXT/train.zh_CN $TEXT/train.zh_CN_tgt $TEXT/valid.zh_CN $TEXT/valid.zh_CN_tgt
#tgt_files=$(ls -al $TEXT/ref_noised_std_zh_wiki_*.tgt | awk '{print $NF}')
#for tgt_file in ${tgt_files}
#do
#     postfix=${tgt_file:38}
#     ids=$(echo $postfix | awk -F. '{print $1}')
#     src_file=$TEXT/hypo_noised_std_zh_wiki_${ids}.src.werdur.full
#     lines=$(wc -l $tgt_file | awk '{print $1}')
#     if [ $lines -eq $max_lines ]; then
#         cat $src_file >> $TEXT/train.zh_CN
#         cat $tgt_file >> $TEXT/train.zh_CN_tgt
#     else
#         cat $src_file >> $TEXT/valid.zh_CN
#         cat $tgt_file >> $TEXT/valid.zh_CN_tgt
#     fi
#done

#We use shared dictionary extracted from training corpus
python $EXP_HOME/FC_utils/preprocess_fc.py --source-lang zh_CN --target-lang zh_CN_tgt \
    --task translation \
    --trainpref $TEXT/train --validpref $TEXT/valid \
    --padding-factor 8 \
    --src-with-nbest-werdur 4 \
    --destdir ${DATA_PATH} \
    --srcdict ${dict_path} --tgtdict ${dict_path}
    --workers 20
#    --joined-dictionary True \

