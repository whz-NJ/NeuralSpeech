#!/bin/bash

# Copyright 2017 Johns Hopkins University (Shinji Watanabe)
#  Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

nlsyms=""
wer=false
bpe=""
bpemodel=""
remove_blank=true
filter=""
num_spkrs=1
help_message="Usage: $0 <data-output_dir> <dict>"

#. utils/parse_options.sh

if [ $# != 3 ]; then
    echo "${help_message}"
    exit 1;
fi

root_dir=$1
output_dir=$2
dic_dir=$3

${root_dir}/concatjson.py ${output_dir}/data.*.json > ${output_dir}/data.json

if [ $num_spkrs -eq 1 ]; then
  ${root_dir}/json2trn.py ${output_dir}/data.json ${dic_dir} --num-spkrs ${num_spkrs} --refs ${output_dir}/ref.trn --hyps ${output_dir}/hyp.trn

  if ${remove_blank}; then
      sed -i.bak2 -r 's/<blank> //g' ${output_dir}/hyp.trn
  fi
  if [ -n "${nlsyms}" ]; then
      cp ${output_dir}/ref.trn ${output_dir}/ref.trn.org
      cp ${output_dir}/hyp.trn ${output_dir}/hyp.trn.org
      filt.py -v ${nlsyms} ${output_dir}/ref.trn.org > ${output_dir}/ref.trn
      filt.py -v ${nlsyms} ${output_dir}/hyp.trn.org > ${output_dir}/hyp.trn
  fi
  if [ -n "${filter}" ]; then
      sed -i.bak3 -f ${filter} ${output_dir}/hyp.trn
      sed -i.bak3 -f ${filter} ${output_dir}/ref.trn
  fi

  sclite -r ${output_dir}/ref.trn trn -h ${output_dir}/hyp.trn trn -i rm -o all nl.sgml stdout > ${output_dir}/result.txt

  echo "write a CER (or TER) result in ${output_dir}/result.txt"
  grep -e Avg -e SPKR -m 2 ${output_dir}/result.txt

  if ${wer}; then
      if [ -n "$bpe" ]; then
  	    spm_decode --model=${bpemodel} --input_format=piece < ${output_dir}/ref.trn | sed -e "s/▁/ /g" > ${output_dir}/ref.wrd.trn
  	    spm_decode --model=${bpemodel} --input_format=piece < ${output_dir}/hyp.trn | sed -e "s/▁/ /g" > ${output_dir}/hyp.wrd.trn
      else
  	    sed -e "s/ //g" -e "s/(/ (/" -e "s/<space>/ /g" ${output_dir}/ref.trn > ${output_dir}/ref.wrd.trn
  	    sed -e "s/ //g" -e "s/(/ (/" -e "s/<space>/ /g" ${output_dir}/hyp.trn > ${output_dir}/hyp.wrd.trn
      fi
      sclite -r ${output_dir}/ref.wrd.trn trn -h ${output_dir}/hyp.wrd.trn trn -i rm -o all stdout > ${output_dir}/result.wrd.txt

      echo "write a WER result in ${output_dir}/result.wrd.txt"
      grep -e Avg -e SPKR -m 2 ${output_dir}/result.wrd.txt
  fi
elif [ ${num_spkrs} -lt 4 ]; then
  ref_trns=""
  hyp_trns=""
  for i in $(seq ${num_spkrs}); do
      ref_trns=${ref_trns}"${output_dir}/ref${i}.trn "
      hyp_trns=${hyp_trns}"${output_dir}/hyp${i}.trn "
  done
  json2trn.py ${output_dir}/data.json ${dic_dir} --num-spkrs ${num_spkrs} --refs ${ref_trns} --hyps ${hyp_trns}

  for n in $(seq ${num_spkrs}); do
      if ${remove_blank}; then
          sed -i.bak2 -r 's/<blank> //g' ${output_dir}/hyp${n}.trn
      fi
      if [ -n "${nlsyms}" ]; then
          cp ${output_dir}/ref${n}.trn ${output_dir}/ref${n}.trn.org
          cp ${output_dir}/hyp${n}.trn ${output_dir}/hyp${n}.trn.org
          filt.py -v ${nlsyms} ${output_dir}/ref${n}.trn.org > ${output_dir}/ref${n}.trn
          filt.py -v ${nlsyms} ${output_dir}/hyp${n}.trn.org > ${output_dir}/hyp${n}.trn
      fi
      if [ -n "${filter}" ]; then
          sed -i.bak3 -f ${filter} ${output_dir}/hyp${n}.trn
          sed -i.bak3 -f ${filter} ${output_dir}/ref${n}.trn
      fi
  done

  results_str=""
  for (( i=0; i<$((num_spkrs * num_spkrs)); i++ )); do
      ind_r=$((i / num_spkrs + 1))
      ind_h=$((i % num_spkrs + 1))
      results_str=${results_str}"${output_dir}/result_r${ind_r}h${ind_h}.txt "
      sclite -r ${output_dir}/ref${ind_r}.trn trn -h ${output_dir}/hyp${ind_h}.trn trn -i rm -o all stdout > ${output_dir}/result_r${ind_r}h${ind_h}.txt
  done

  echo "write CER (or TER) results in ${output_dir}/result_r*h*.txt"
  eval_perm_free_error.py --num-spkrs ${num_spkrs} \
      ${results_str} > ${output_dir}/min_perm_result.json
  sed -n '2,4p' ${output_dir}/min_perm_result.json

  if ${wer}; then
      for n in $(seq ${num_spkrs}); do
          if [ -n "$bpe" ]; then
              spm_decode --model=${bpemodel} --input_format=piece < ${output_dir}/ref${n}.trn | sed -e "s/▁/ /g" > ${output_dir}/ref${n}.wrd.trn
              spm_decode --model=${bpemodel} --input_format=piece < ${output_dir}/hyp${n}.trn | sed -e "s/▁/ /g" > ${output_dir}/hyp${n}.wrd.trn
          else
              sed -e "s/ //g" -e "s/(/ (/" -e "s/<space>/ /g" ${output_dir}/ref${n}.trn > ${output_dir}/ref${n}.wrd.trn
              sed -e "s/ //g" -e "s/(/ (/" -e "s/<space>/ /g" ${output_dir}/hyp${n}.trn > ${output_dir}/hyp${n}.wrd.trn
          fi
      done
      results_str=""
      for (( i=0; i<$((num_spkrs * num_spkrs)); i++ )); do
          ind_r=$((i / num_spkrs + 1))
          ind_h=$((i % num_spkrs + 1))
          results_str=${results_str}"${output_dir}/result_r${ind_r}h${ind_h}.wrd.txt "
          sclite -r ${output_dir}/ref${ind_r}.wrd.trn trn -h ${output_dir}/hyp${ind_h}.wrd.trn trn -i rm -o all stdout > ${output_dir}/result_r${ind_r}h${ind_h}.wrd.txt
      done

      echo "write WER results in ${output_dir}/result_r*h*.wrd.txt"
      eval_perm_free_error.py --num-spkrs ${num_spkrs} \
          ${results_str} > ${output_dir}/min_perm_result.wrd.json
      sed -n '2,4p' ${output_dir}/min_perm_result.wrd.json
  fi
fi

