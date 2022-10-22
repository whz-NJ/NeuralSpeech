# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

sckt_path='/root/fastcorrect/sctk-2.4.10/bin'

# epochs="15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35"
epochs="15 16 17 18"
asr_data_dir="/root/std_noised_sports_corpus4"
fc_model_dir="/root/fastcorrect/models/finetune.ftb4"

sets="valid test"

#result_dir='/root/fastcorrect/models/finetune/results_best_aishell_b0_t0.0/dev'
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

cal_wer() {
  type=$1
  result_dir=$2

  cp ${result_dir}/data.json ${result_dir}/data.1.json
  bash $EXP_HOME/espnet_wer_calculation/score_sclite.sh ${result_dir} ${dict}  2>&1 | tail -n 3 > ${result_dir}/wer_short.txt

  cat ${result_dir}/wer_short.txt
  cat ${result_dir}/result.txt | grep Sum | tail -n 1 | sed 's/|/ | /g' | awk '{print $11/$5}' > ${result_dir}/wer_short_2point.txt
  echo -n ${type}" Word Error Rate: "
  cat ${result_dir}/wer_short_2point.txt
}

for set_name in ${sets}
do
  result_dir=${asr_data_dir}/${set_name}
  cal_wer "asr_${set_name}" "${result_dir}"
done

for epoch in ${epochs}
do
  for set_name in ${sets}
  do
    # /root/fastcorrect/models/finetune.ftb4/results_15_asr_b0_t0.0/test
    result_dir=${fc_model_dir}/results_${epoch}_asr_b0_t0.0/${set_name}
    cal_wer "fc_${set_name}_${epoch}" "${result_dir}"
  done
done
