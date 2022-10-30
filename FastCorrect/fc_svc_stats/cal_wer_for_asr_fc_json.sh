#!/bin/bash
result_data_file_dir='/root/fastcorrect/hdc_corpus'

sckt_path='/root/fastcorrect/sctk-2.4.10/bin'

EXP_HOME=$(cd `dirname $0`; pwd)/..
cd $EXP_HOME
EXP_HOME=$(cd `dirname $0`; pwd)

export PATH=$EXP_HOME/espnet_wer_calculation:$sckt_path:$PATH
export PYTHONPATH=$EXP_HOME/espnet_wer_calculation:$PYTHONPATH
dict=$EXP_HOME/eval_data/lang_1char/train_sp_units.txt
#$1
for fc_data_json_file in ${result_data_file_dir}/fc*.json
do
  if [ -d "$fc_data_json_file" ]; then
     continue
  fi
  fc_data_json_file_name=$(basename "$fc_data_json_file")
  asr_data_json_file_name=$(echo "${fc_data_json_file_name}" | sed -e "s/^fc_/asr_/")
  asr_data_json_file=$(dirname "$fc_data_json_file")/${asr_data_json_file_name}
  echo "begin to process ${fc_data_json_file_name}"

  cp "${asr_data_json_file}" ${result_data_file_dir}/data.1.json #一个发音人
  bash $EXP_HOME/espnet_wer_calculation/score_sclite.sh ${result_data_file_dir} ${dict}  2>&1 | tail -n 3 > ${result_data_file_dir}/wer_short.txt
  cat ${result_data_file_dir}/wer_short.txt
  cat ${result_data_file_dir}/result.txt | grep Sum | tail -n 1 | sed 's/|/ | /g' | awk '{print $11/$5}' > ${result_data_file_dir}/wer_short_2point.txt
  echo -n "Word Error Rate: "
  cat ${result_data_file_dir}/wer_short_2point.txt

  cp "${fc_data_json_file}" ${result_data_file_dir}/data.1.json #一个发音人
  bash $EXP_HOME/espnet_wer_calculation/score_sclite.sh ${result_data_file_dir} ${dict}  2>&1 | tail -n 3 > ${result_data_file_dir}/wer_short.txt
  cat ${result_data_file_dir}/wer_short.txt
  cat ${result_data_file_dir}/result.txt | grep Sum | tail -n 1 | sed 's/|/ | /g' | awk '{print $11/$5}' > ${result_data_file_dir}/wer_short_2point.txt
  echo -n "FC Word Error Rate: "
  cat ${result_data_file_dir}/wer_short_2point.txt
  echo ""
done
