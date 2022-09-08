import os
import codecs

asr_output_file_path='/root/sports_corpus2/noised_corpus.txt'
split_rate = [0.9, 0.05, 0.05]
processed_corpus_root_dir = "/root/sports_corpus2"

def replace_dot_path(path):
    pwd = os.getcwd()
    if path.startswith(".."):
        ppwd = os.path.dirname(pwd)
        result = os.path.join(ppwd, path[3:]) #子目录不能包含最开始的 /
    elif path.startswith("."):
        result = os.path.join(pwd, path[2:]) #子目录不能包含最开始的 /
    else:
        result = path
    return result
processed_corpus_root_dir = replace_dot_path(processed_corpus_root_dir)

corpus_asr_map = {}
with codecs.open(asr_output_file_path, 'r', 'utf-8') as asr_file:
    for line in asr_file:
        corpus = line.split('\t')[0].strip()
        asr_result = line.split('\t')[1].strip()
        asr_results = corpus_asr_map.get(corpus, [])
        asr_results.append(asr_result)
        corpus_asr_map[corpus] = asr_results

asr_output_file_name = os.path.basename(asr_output_file_path)
asr_output_file_dir = os.path.dirname(asr_output_file_path)

train_asr_output_file_name = "train_" + asr_output_file_name
train_asr_output_file_path = os.path.join(asr_output_file_dir, train_asr_output_file_name)
if os.path.isfile(train_asr_output_file_path):
    os.remove(train_asr_output_file_path)
valid_asr_output_file_name = "valid_" + asr_output_file_name
valid_asr_output_file_path = os.path.join(asr_output_file_dir, valid_asr_output_file_name)
if os.path.isfile(valid_asr_output_file_path):
    os.remove(valid_asr_output_file_path)
test_asr_output_file_name = "test_" + asr_output_file_name
test_asr_output_file_path = os.path.join(asr_output_file_dir, test_asr_output_file_name)
if os.path.isfile(test_asr_output_file_path):
    os.remove(test_asr_output_file_path)


train_file_paths = []
valid_file_paths = []
test_file_paths = []
def splitTrainValidTest(root_dir):
    for root,dirs,files in os.walk(root_dir):
        if root == processed_corpus_root_dir:
            continue
        if len(files) < 3:
            print(f"too few files {len(files)} under folder: {root_dir}")
            continue
        valid_files_num = int(split_rate[1]*float(len(files)))
        test_files_num = int(split_rate[2]*float(len(files)))
        if valid_files_num == 0:
            valid_files_num = 1
        if test_files_num == 0:
            test_files_num = 1

        train_files_num = len(files) - valid_files_num - test_files_num
        if train_files_num <= 0:
            raise ValueError("Unsupported condition, root:" + root)
        corpus_asr_lines = []
        for file in files[:train_files_num]:
            train_file_paths.append(os.path.join(root, file) + "\n")
            with open(os.path.join(root, file), 'r', encoding='utf-8') as corpus_file:
                for corpus_line in corpus_file.readlines():
                    corpus_line2 = " ".join(corpus_line.strip())
                    asr_lines = corpus_asr_map.get(corpus_line2)
                    if not asr_lines:
                        print(f"{corpus_line} has no asr result")
                        continue
                    for asr_line in asr_lines:
                        corpus_asr_lines.append(corpus_line2 + "\t" + asr_line + "\n")
        with open(train_asr_output_file_path, "a+", encoding='utf-8') as train_file:
            train_file.writelines(corpus_asr_lines)

        corpus_asr_lines = []
        for file in files[train_files_num:train_files_num + valid_files_num]:
            valid_file_paths.append(os.path.join(root, file) + "\n")
            with open(os.path.join(root, file), 'r', encoding='utf-8') as corpus_file:
                for corpus_line in corpus_file.readlines():
                    corpus_line2 = " ".join(corpus_line.strip())
                    asr_lines = corpus_asr_map.get(corpus_line2)
                    if not asr_lines:
                        print(f"{corpus_line} has no asr result")
                        continue
                    for asr_line in asr_lines:
                        corpus_asr_lines.append(corpus_line2 + "\t" + asr_line + "\n")
        with open(valid_asr_output_file_path, "a+", encoding='utf-8') as valid_file:
            valid_file.writelines(corpus_asr_lines)

        corpus_asr_lines = []
        for file in files[train_files_num + valid_files_num:]:
            test_file_paths.append(os.path.join(root, file) + "\n")
            with open(os.path.join(root, file), 'r', encoding='utf-8') as corpus_file:
                for corpus_line in corpus_file.readlines():
                    corpus_line2 = " ".join(corpus_line.strip())
                    asr_lines = corpus_asr_map.get(corpus_line2)
                    if not asr_lines:
                        print(f"{corpus_line} has no asr result")
                        continue
                    for asr_line in asr_lines:
                        corpus_asr_lines.append(corpus_line2 + "\t" + asr_line + "\n")
        with open(test_asr_output_file_path, "a+", encoding='utf-8') as test_file:
            test_file.writelines(corpus_asr_lines)

        for dir in dirs:
            splitTrainValidTest(os.path.join(root, dir))

splitTrainValidTest(processed_corpus_root_dir)

train_file_paths_file_path = os.path.join(asr_output_file_dir, "train_file_paths.txt")
valid_file_paths_file_path = os.path.join(asr_output_file_dir, "valid_file_paths.txt")
test_file_paths_file_path = os.path.join(asr_output_file_dir, "test_file_paths.txt")
with open(train_file_paths_file_path, "w", encoding='utf-8') as train_file_paths_file:
    train_file_paths_file.writelines(train_file_paths)
with open(valid_file_paths_file_path, "w", encoding='utf-8') as valid_file_paths_file:
    valid_file_paths_file.writelines(valid_file_paths)
with open(test_file_paths_file_path, "w", encoding='utf-8') as test_file_paths_file:
    test_file_paths_file.writelines(test_file_paths)

