import sys
input_file = sys.argv[1] # output of add_noise.py
output_hypo_file = sys.argv[2]
output_ref_file = sys.argv[3]

ref_lines = []
hypo_lines = []
with open(input_file, 'r', encoding='utf-8') as infile:
    for line in infile.readlines():
        fields = line.split('\t')
        ref_line = fields[0].strip()
        hypo1 = fields[1].strip()
        hypo2 = fields[2].strip()
        hypo3 = fields[3].strip()
        hypo4 = fields[4].strip()
        ref_line = " ".join(ref_line).strip() + "\n"
        hypo = (hypo1 + "#" + hypo2 + "#" + hypo3 + "#" + hypo4)
        hypo = " ".join(hypo).strip() + "\n"
        ref_lines.append(ref_line)
        hypo_lines.append(hypo)

with open(output_hypo_file,"w") as f:
    f.writelines(hypo_lines)

with open(output_ref_file,"w") as f:
    f.writelines(ref_lines)
