# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

sckt_path=/root/sctk/bin
input_data_dir=/root/fastcorrect2/models/pretrain/results_49_aishell_b0_t0.0_pdlambda_0.5_0.5/test

EXP_HOME=$(cd `dirname $0`; pwd)
export PATH=$EXP_HOME/espnet_wer_calculation:$sckt_path:$PATH
export PYTHONPATH=$EXP_HOME/espnet_wer_calculation:$PYTHONPATH
echo $PATH
dict=$EXP_HOME/eval_data/lang_1char/train_sp_units.txt

cp ${input_data_dir}/data.json ${input_data_dir}/data.1.json
bash $EXP_HOME/espnet_wer_calculation/score_sclite.sh ${input_data_dir} ${dict}  2>&1 | tail -n 3 > ${input_data_dir}/wer_short.txt

cat ${input_data_dir}/wer_short.txt
cat ${input_data_dir}/result.txt | grep Sum | tail -n 1 | sed 's/|/ | /g' | awk '{print $11/$5}' > ${input_data_dir}/wer_short_2point.txt
echo -n "Word Error Rate: "
cat ${input_data_dir}/wer_short_2point.txt
