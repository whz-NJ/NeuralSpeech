# -*- coding: utf-8 -*-
import os
import codecs

sports_asr_root_dir = "/root/noised_sports_corpus3"
for root, dirs, files in os.walk(sports_asr_root_dir):
    for file in files:
        if not file.endswith(".txt"):
            continue

        output_lines = []
        with codecs.open(os.path.join(root, file), 'r', 'utf-8') as infile:
            lines = infile.readlines()
            for line in lines:
                line = line.strip()
                if len(line) == 0:
                    continue
                line = line.replace(",", "")
                line = line.replace("，", "") + "\n"
                output_lines.append(line)
        outfile = codecs.open(os.path.join(root, "tmp_" + file), 'w', 'utf-8')
        outfile.writelines(output_lines)
        outfile.close()
        os.remove(os.path.join(root, file))
        os.rename(os.path.join(root, "tmp_" + file), os.path.join(root, file))

