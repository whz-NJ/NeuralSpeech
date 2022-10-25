# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

EXP_HOME=$(cd `dirname $0`; pwd)/..
cd $EXP_HOME


#SAVE_DIR=/root/fastcorrect/models/finetune   #<PATH-to-AISHELL1-Save-Dir>
#SAVE_DIR=/root/fastcorrect/models/finetune.ftb
SAVE_DIR=/root/fastcorrect/models/finetune.ftb4
export PYTHONPATH=$EXP_HOME/FC_utils:$PYTHONPATH
#DATA_DIR=/root/std_ftb_sports_corpus_en.bin
DATA_DIR=/root/std_noised_sports_corpus4.bin
#test_epochs="15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35"  # Should be decided by dev set performance
test_epochs="20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35"

#EVAL_ROOT_DIR=/root/sports_corpus2
#EVAL_ROOT_DIR=/root/std_ftb_sports_corpus_en
# 读取这个目录下 valid或test子目录下的 data.json 作为输入文件
EVAL_ROOT_DIR=/root/std_noised_sports_corpus4
for test_epoch in ${test_epochs}; do
  echo "test epoch: $test_epoch"

  mkdir -p ${SAVE_DIR}/log_asr_e${test_epoch}
  edit_thre=-1.0

  export CUDA_VISIBLE_DEVICES=0
  #nohup python -u eval_aishell.py ${EVAL_ROOT_DIR} "dev" ${SAVE_DIR} 0 0 ${test_epoch} >> ${SAVE_DIR}/log_aishell_e${test_epoch}/nohup.b0ttest00.log 2>&1 &
  #nohup python -u eval_asr.py ${EVAL_ROOT_DIR} "dev" ${SAVE_DIR} 0 0 ${test_epoch} >> ${SAVE_DIR}/log_asr_e${test_epoch}/nohup.b0ttest01.log 2>&1 &
  #export CUDA_VISIBLE_DEVICES=1
  # nohup python -u eval_aishell.py ${EVAL_ROOT_DIR} "test" ${SAVE_DIR} 0 0 ${test_epoch} >> ${SAVE_DIR}/log_aishell_e${test_epoch}/nohup.b0ttest01.log 2>&1 &
  nohup python -u eval_asr.py ${EVAL_ROOT_DIR} "valid" ${SAVE_DIR} ${DATA_DIR} 0 0 ${test_epoch} >> ${SAVE_DIR}/log_asr_e${test_epoch}/nohup.b0valid01.log 2>&1 &
  nohup python -u eval_asr.py ${EVAL_ROOT_DIR} "test" ${SAVE_DIR} ${DATA_DIR} 0 0 ${test_epoch} >> ${SAVE_DIR}/log_asr_e${test_epoch}/nohup.b0test01.log 2>&1 &

  wait
done