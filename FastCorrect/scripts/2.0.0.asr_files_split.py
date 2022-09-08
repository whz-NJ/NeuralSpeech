import os
import codecs

split_rate = [0.9, 0.05, 0.05]
processed_corpus_root_dir = "/root/std_sports_corpus_en"
asr_output_file_name = ""
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

train_asr_output_file_name = "train_std_noised_corpus.txt"
train_asr_output_file_path = os.path.join(processed_corpus_root_dir, train_asr_output_file_name)
if os.path.isfile(train_asr_output_file_path):
    os.remove(train_asr_output_file_path)
valid_asr_output_file_name = "valid_std_noised_corpus.txt"
valid_asr_output_file_path = os.path.join(processed_corpus_root_dir, valid_asr_output_file_name)
if os.path.isfile(valid_asr_output_file_path):
    os.remove(valid_asr_output_file_path)
test_asr_output_file_name = "test_std_noised_corpus.txt"
test_asr_output_file_path = os.path.join(processed_corpus_root_dir, test_asr_output_file_name)
if os.path.isfile(test_asr_output_file_path):
    os.remove(test_asr_output_file_path)

train_file_paths = []
valid_file_paths = []
test_file_paths = []
def splitTrainValidTest(root_dir):
    for root,dirs,files in os.walk(root_dir):
        if root == processed_corpus_root_dir:
            continue
        valid_files = []
        for file in files:
            if file.startswith("std_") and file.endswith("_asr.txt"):
                valid_files.append(file)
        if len(valid_files) < 3:
            print(f"too few files {len(valid_files)} under folder: {root_dir}")
            continue
        valid_files_num = int(split_rate[1]*float(len(valid_files)))
        test_files_num = int(split_rate[2]*float(len(valid_files)))
        if valid_files_num == 0:
            valid_files_num = 1
        if test_files_num == 0:
            test_files_num = 1

        train_files_num = len(valid_files) - valid_files_num - test_files_num
        if train_files_num <= 0:
            raise ValueError("Unsupported condition, root:" + root)
        corpus_asr_lines = []
        for file in valid_files[:train_files_num]:
            train_file_paths.append(os.path.join(root, file) + "\n")
            with open(os.path.join(root, file), 'r', encoding='utf-8') as corpus_file:
                corpus_asr_lines.extend(corpus_file.readlines())
        with open(train_asr_output_file_path, "a+", encoding='utf-8') as train_file:
            train_file.writelines(corpus_asr_lines)

        corpus_asr_lines = []
        for file in valid_files[train_files_num:train_files_num + valid_files_num]:
            valid_file_paths.append(os.path.join(root, file) + "\n")
            with open(os.path.join(root, file), 'r', encoding='utf-8') as corpus_file:
                corpus_asr_lines.extend(corpus_file.readlines())
        with open(valid_asr_output_file_path, "a+", encoding='utf-8') as valid_file:
            valid_file.writelines(corpus_asr_lines)

        corpus_asr_lines = []
        for file in valid_files[train_files_num + valid_files_num:]:
            test_file_paths.append(os.path.join(root, file) + "\n")
            with open(os.path.join(root, file), 'r', encoding='utf-8') as corpus_file:
                corpus_asr_lines.extend(corpus_file.readlines())
        with open(test_asr_output_file_path, "a+", encoding='utf-8') as test_file:
            test_file.writelines(corpus_asr_lines)

splitTrainValidTest(processed_corpus_root_dir)

train_file_paths_file_path = os.path.join(processed_corpus_root_dir, "train_file_paths.txt")
valid_file_paths_file_path = os.path.join(processed_corpus_root_dir, "valid_file_paths.txt")
test_file_paths_file_path = os.path.join(processed_corpus_root_dir, "test_file_paths.txt")
with open(train_file_paths_file_path, "w", encoding='utf-8') as train_file_paths_file:
    train_file_paths_file.writelines(train_file_paths)
with open(valid_file_paths_file_path, "w", encoding='utf-8') as valid_file_paths_file:
    valid_file_paths_file.writelines(valid_file_paths)
with open(test_file_paths_file_path, "w", encoding='utf-8') as test_file_paths_file:
    test_file_paths_file.writelines(test_file_paths)

