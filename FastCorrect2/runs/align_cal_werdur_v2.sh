wiki_files=$(ls -al data/wiki_data/ref_noised_std_zh_wiki_* | awk '{print $NF}')
max_lines=500000
for wiki_file in ${wiki_files}
do
    post_fix=${wiki_file:38}
    if [ $(expr length ${post_fix}) -gt 3 ]; then
        continue
    fi
    rm -rf data/wiki_data/hypo_noised_std_zh_wiki_${post_fix}_*
    rm -rf data/wiki_data/ref_noised_std_zh_wiki_${post_fix}_*
    lines=$(wc -l data/wiki_data/ref_noised_std_zh_wiki_${post_fix} | awk '{print $1}')
    part_files_num=$(expr ${lines} / ${max_lines})
    remains=$(expr ${lines} - ${part_files_num} \* ${max_lines})
    part_no=0
    while [[ ${part_no} -lt ${part_files_num} ]]
    do
        start_line_no=$(expr ${part_no} \* ${max_lines} + 1)
        end_line_no=$(expr ${start_line_no} + ${max_lines} - 1)
        sed -n "${start_line_no},${end_line_no}p" data/wiki_data/hypo_noised_std_zh_wiki_${post_fix} > data/wiki_data/hypo_noised_std_zh_wiki_${post_fix}_${part_no}
        sed -n "${start_line_no},${end_line_no}p" data/wiki_data/ref_noised_std_zh_wiki_${post_fix} > data/wiki_data/ref_noised_std_zh_wiki_${post_fix}_${part_no}
        part_no=$(expr ${part_no} + 1)
    done

    if [ ${remains} -gt 0 ]; then
        tail -n ${remains} data/wiki_data/hypo_noised_std_zh_wiki_${post_fix} > data/wiki_data/hypo_noised_std_zh_wiki_${post_fix}_${part_files_num}
        tail -n ${remains} data/wiki_data/ref_noised_std_zh_wiki_${post_fix} > data/wiki_data/ref_noised_std_zh_wiki_${post_fix}_${part_files_num}
    fi

    part_wiki_files=$(ls -al data/wiki_data/ref_noised_std_zh_wiki_${post_fix}_* | awk '{print $NF}')
    for part_wiki_file in ${part_wiki_files}
    do
        post_fix2=${part_wiki_file:41}
        python scripts/align_cal_werdur_fast.py data/wiki_data/hypo_noised_std_zh_wiki_${post_fix}_${post_fix2} data/wiki_data/ref_noised_std_zh_wiki_${post_fix}_${post_fix2}
    done
done
