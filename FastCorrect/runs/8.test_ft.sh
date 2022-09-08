# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

EXP_HOME=$(cd `dirname $0`; pwd)/..
cd $EXP_HOME


#SAVE_DIR=/root/fastcorrect/models/finetune   #<PATH-to-AISHELL1-Save-Dir>
SAVE_DIR=/root/fastcorrect/models/finetune.ftb
export PYTHONPATH=$EXP_HOME/FC_utils:$PYTHONPATH
DATA_DIR=/root/std_ftb_sports_corpus_en.bin
test_epochs=best  # Should be decided by dev set performance

#EVAL_ROOT_DIR=/root/sports_corpus2
EVAL_ROOT_DIR=/root/std_ftb_sports_corpus_en
for test_epoch in ${test_epochs}; do
echo "test epoch: $test_epoch"

mkdir -p ${SAVE_DIR}/log_asr_e${test_epoch}
edit_thre=-1.0

export CUDA_VISIBLE_DEVICES=0
#nohup python -u eval_aishell.py ${EVAL_ROOT_DIR} "dev" ${SAVE_DIR} 0 0 ${test_epoch} >> ${SAVE_DIR}/log_aishell_e${test_epoch}/nohup.b0ttest00.log 2>&1 &
#nohup python -u eval_asr.py ${EVAL_ROOT_DIR} "dev" ${SAVE_DIR} 0 0 ${test_epoch} >> ${SAVE_DIR}/log_asr_e${test_epoch}/nohup.b0ttest01.log 2>&1 &
#export CUDA_VISIBLE_DEVICES=1
# nohup python -u eval_aishell.py ${EVAL_ROOT_DIR} "test" ${SAVE_DIR} 0 0 ${test_epoch} >> ${SAVE_DIR}/log_aishell_e${test_epoch}/nohup.b0ttest01.log 2>&1 &
nohup python -u eval_asr.py ${EVAL_ROOT_DIR} "test" ${SAVE_DIR} ${DATA_DIR} 0 0 ${test_epoch} >> ${SAVE_DIR}/log_asr_e${test_epoch}/nohup.b0ttest01.log 2>&1 &

wait
done

