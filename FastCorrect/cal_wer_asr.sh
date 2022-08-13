# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

sckt_path='/root/fastcorrect/sctk-2.4.10/bin'

#result_data_file='/root/fastcorrect/asr_eval_data/dev0/data.json'
result_data_file='/root/fastcorrect/asr_eval_data/test0/data.json'
#result_data_file='/root/fastcorrect/models/finetune/results_best_asr_b0_t0.0/dev/data.json'
#result_data_file='/root/fastcorrect/models/finetune/results_best_asr_b0_t0.0/test/data.json'

result_dir=$(dirname $result_data_file)

#if ! [ $1 ]; then
#  echo "Usage: bash cal_wer_aishell.sh <path-to-result> <path-to-sctk-bin>"
#  exit 1
#fi

#if ! [ $2 ]; then
#  echo "Usage: bash cal_wer_aishell.sh <path-to-result> <path-to-sctk-bin>"
#  exit 1
#fi


EXP_HOME=$(cd `dirname $0`; pwd)
export PATH=$EXP_HOME/espnet_wer_calculation:$sckt_path:$PATH
export PYTHONPATH=$EXP_HOME/espnet_wer_calculation:$PYTHONPATH
echo $PATH
dict=$EXP_HOME/eval_data/lang_1char/train_sp_units.txt
#$1

cp ${result_data_file} ${result_dir}/data.1.json #一个发音人
bash $EXP_HOME/espnet_wer_calculation/score_sclite.sh ${result_dir} ${dict}  2>&1 | tail -n 3 > ${result_dir}/wer_short.txt

cat ${result_dir}/wer_short.txt
cat ${result_dir}/result.txt | grep Sum | tail -n 1 | sed 's/|/ | /g' | awk '{print $11/$5}' > ${result_dir}/wer_short_2point.txt
echo -n "Word Error Rate: "
cat ${result_dir}/wer_short_2point.txt


