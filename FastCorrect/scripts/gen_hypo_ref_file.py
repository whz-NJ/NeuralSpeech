import sys
import preprocess
# input_file = sys.argv[1] # output of add_noise.py
# output_hypo_file = sys.argv[2]
# output_ref_file = sys.argv[3]
input_file = r'C:\Code\NeuralSpeech\FastCorrect\noised_std_sports.txt' # output of add_noise.py
output_hypo_file = r'C:\Code\NeuralSpeech\FastCorrect\hypo7.txt'
output_ref_file = r'C:\Code\NeuralSpeech\FastCorrect\ref7.txt'

ref_lines = []
hypo_lines = []
with open(input_file, 'r', encoding='utf-8') as infile:
    for line in infile.readlines():
        fields = line.split('\t')
        ref_line = fields[0].strip() + '\n'
        hypo = fields[1].strip() + '\n'
        # ref_line = " ".join(preprocess.tokenize(ref_line)) + '\n'
        # hypo = " ".join(preprocess.tokenize(hypo)) + '\n'
        ref_lines.append(ref_line)
        hypo_lines.append(hypo)

with open(output_hypo_file,"w", encoding='utf-8') as f:
    f.writelines(hypo_lines)

with open(output_ref_file,"w", encoding='utf-8') as f:
    f.writelines(ref_lines)
