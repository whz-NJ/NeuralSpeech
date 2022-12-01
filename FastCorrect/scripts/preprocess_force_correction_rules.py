rule_file='./force_correction_rules.txt'
filtered_rule_file='./std_force_correction_rules.txt'
# rule_file='./test_rules.txt'
# filtered_rule_file='./std_test_rules.txt'

from g2pM import G2pM
import preprocess
import Levenshtein

model = G2pM()

rules = []
with open(rule_file, 'r', encoding='utf-8') as infile:
    for count, rule in enumerate(infile.readlines()):
        fields = rule.split('\t')

        orig_words = fields[0].strip()
        orig_sentences = preprocess.normAndTokenize(orig_words, 1)
        orig_tokens = []
        for sentence in orig_sentences:
            orig_tokens.extend(sentence.split())
        orig_py = ''
        for token in orig_tokens:
            if len(token) == 1:
                ch = token[0]
                if '\u4e00' <= ch <= '\u9fa5' or '\u3400' <= ch <= '\u4DB5':
                    orig_py += preprocess.g2pM_dict[ch]
        if len(orig_py) == 0:
            print('skip too short rule: ' + rule.strip())
            continue

        error_words = fields[1].strip()
        error_sentences = preprocess.normAndTokenize(error_words, 1)
        error_tokens = []
        for sentence in error_sentences:
            error_tokens.extend(sentence.split())
        error_py = ''
        for token in error_tokens:
            if len(token) == 1:
                ch = token[0]
                if '\u4e00' <= ch <= '\u9fa5' or '\u3400' <= ch <= '\u4DB5':
                    error_py += preprocess.g2pM_dict[ch]
        if len(error_py) == 0:
            print('skip too short rule: ' + rule.strip())
            continue

        distance = Levenshtein.distance(orig_py, error_py)
        similarity = 1.0 - distance/max(len(orig_py), len(error_py))
        if similarity < 0.50:
            print('skip unlike rule: ' + rule.strip())
            continue
        rules.append(rule)

with open(filtered_rule_file, 'w', encoding='utf-8') as outfile:
    outfile.writelines(rules)
