import os
import re

align_files_dir=r"./"

names_list=os.listdir(align_files_dir)
tgt_file_name_pattern = re.compile(r'(train|valid|test)_ref_std_noised(\d{2})_corpus(\d{3}).tgt')
full_file_name_pattern = re.compile(r'(train|valid|test)_hypo_std_noised(\d{2})_corpus(\d{3}).full')

for ref_hypo in ('ref', 'hypo'):
    for cur_set_name in ('train', 'valid', 'test'):
        sn_merged_lines_map = {}
        for name in names_list:
            if ref_hypo == 'ref':
                match = tgt_file_name_pattern.match(name)
            else:
                match = full_file_name_pattern.match(name)
            if match:
                set_name = match.group(1)
                noise_no = match.group(2)
                sn = match.group(3)
                if set_name != cur_set_name:
                    continue
                merged_lines = sn_merged_lines_map.get(sn, [])
                with open(os.path.join(align_files_dir, name), 'r', encoding='utf-8') as infile:
                    sn_merged_lines_map[sn] = infile.readlines()

        lines = []
        sns = sorted(sn_merged_lines_map.keys())
        for sn in sns:
            merged_lines = sn_merged_lines_map.get(sn, [])
            lines.extend(merged_lines)
        if ref_hypo == 'ref':
            merged_file_name = f"{cur_set_name}_ref_std_noised{noise_no}_corpus.tgt"
        else:
            merged_file_name = f"{cur_set_name}_hypo_std_noised{noise_no}_corpus.full"
        with open(os.path.join(align_files_dir, merged_file_name), 'w', encoding='utf-8') as outfile:
            outfile.writelines(lines)






