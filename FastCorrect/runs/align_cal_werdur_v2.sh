noised_wiki_files=$(ls -al data/wiki_data/noised_zh_wiki_* | awk '{print $NF}')
for noised_wiki_file in ${noised_wiki_files}
do
    post_fix=$(echo ${noised_wiki_file:30})
    if [ $post_fix == '02_1' ]
    then
        continue
    fi
    python scripts/align_cal_werdur_v2.py data/wiki_data/noised_hypo_zh_wiki_${post_fix} data/wiki_data/noised_ref_zh_wiki_${post_fix}
done

