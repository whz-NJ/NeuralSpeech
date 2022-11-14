import os
import re

align_files_dir=r"./"

names_list=os.listdir(align_files_dir)
tgt_file_name_pattern = re.compile(r'(train|valid|test)_ref_std_noised(\d{2})_corpus(\d{3}).tgt')
full_file_name_pattern = re.compile(r'(train|valid|test)_hypo_std_noised(\d{2})_corpus(\d{3}).full')

out_files_dir = os.path.join(align_files_dir, "merged")
if not os.path.isdir(out_files_dir):
    os.makedirs(out_files_dir)

for ref_hypo in ('ref', 'hypo'):
    for cur_set_name in ('train', 'valid', 'test'):
        noised_sn_merged_lines_map = {}
        for name in names_list:
            if ref_hypo == 'ref':
                match = tgt_file_name_pattern.match(name)
            else:
                match = full_file_name_pattern.match(name)
            if match:
                set_name = match.group(1)
                noised_no = match.group(2)
                sn = match.group(3)
                if set_name != cur_set_name:
                    continue
                sn_merged_lines_map = noised_sn_merged_lines_map.get(noised_no, {})
                with open(os.path.join(align_files_dir, name), 'r', encoding='utf-8') as infile:
                    sn_merged_lines_map[sn] = infile.readlines()
                noised_sn_merged_lines_map[noised_no] = sn_merged_lines_map

        merged_lines = []
        noised_nos = sorted(noised_sn_merged_lines_map.keys())
        for noised_no in noised_nos:
            sn_merged_lines_map = noised_sn_merged_lines_map[noised_no]
            sns = sorted(sn_merged_lines_map.keys())
            for sn in sns:
                lines = sn_merged_lines_map.get(sn, [])
                merged_lines.extend(lines)

        if ref_hypo == 'ref':
            merged_file_name = f"{cur_set_name}_ref_std_noised_corpus.tgt"
        else:
            merged_file_name = f"{cur_set_name}_hypo_std_noised_corpus.full"
        with open(os.path.join(out_files_dir, merged_file_name), 'w', encoding='utf-8') as outfile:
            outfile.writelines(merged_lines)
