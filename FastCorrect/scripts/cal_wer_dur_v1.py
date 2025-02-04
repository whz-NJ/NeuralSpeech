import preprocess
from g2pM import G2pM
import copy
model = G2pM()

g2pM_dict = preprocess.g2pM_dict

def init_number_vec(len_hyp, len_ref):
    return_vec = []
    for i in range(len_hyp):
        return_vec.append([0 for j in range(len_ref)])
    return return_vec


def calculate_wer_dur(hypo_list, ref_list):
    len_hyp = len(hypo_list)
    len_ref = len(ref_list)
    cost_matrix = init_number_vec(len_hyp + 1, len_ref + 1)

    ops_matrix = init_number_vec(len_hyp + 1, len_ref + 1)

    for i in range(len_hyp + 1):
        cost_matrix[i][0] = i
    for j in range(len_ref + 1):
        cost_matrix[0][j] = j

    id_ind = 0
    for i in range(1, len_hyp + 1):
        for j in range(1, len_ref + 1):
            ideal_index = i * len_ref / len_hyp
            if hypo_list[i - 1] == ref_list[j - 1]:
                cost_matrix[i][j] = cost_matrix[i - 1][j - 1]
            else:
                substitution = cost_matrix[i - 1][j - 1] + 1
                insertion = cost_matrix[i - 1][j] + 1
                deletion = cost_matrix[i][j - 1] + 1

                compare_val = [substitution, insertion, deletion]

                if (substitution > insertion) and (insertion == deletion):
                    min_val = insertion
                    if ideal_index >= j:
                        operation_idx = 2
                    else:
                        operation_idx = 3
                else:
                    min_val = min(compare_val)
                    operation_idx = compare_val.index(min_val) + 1
                cost_matrix[i][j] = min_val
                ops_matrix[i][j] = operation_idx

    i = len_hyp
    j = len_ref
    char_map = []
    current_chars = []
    res_chars = []
    while i >= 0 or j >= 0:
        i_idx = max(0, i)
        j_idx = max(0, j)

        if ops_matrix[i_idx][j_idx] == 0:
            if i - 1 >= 0 and j - 1 >= 0:
                current_chars.append(ref_list[j - 1])
                char_map.append([hypo_list[i - 1], current_chars])
                current_chars = []

            i -= 1
            j -= 1

        elif ops_matrix[i_idx][j_idx] == 2:
            char_map.append([hypo_list[i - 1], current_chars])
            current_chars = []
            i -= 1
        elif ops_matrix[i_idx][j_idx] == 3:
            current_chars.append(ref_list[j - 1])
            j -= 1
        elif ops_matrix[i_idx][j_idx] == 1:
            current_chars.append(ref_list[j - 1])
            char_map.append([hypo_list[i - 1], current_chars])
            current_chars = []
            i -= 1
            j -= 1
        else:
            raise ValueError("Impossible condition!")

        if i < 0 and j >= 0:
            res_chars.append(ref_list[j])
        elif j < 0 and i >= 0:
            char_map.append([hypo_list[i], current_chars])
            current_chars = []

    if res_chars:
        char_map[-1][-1].extend(res_chars)

    char_map.reverse()
    for i in range(len(char_map)):
        char_map[i][-1].reverse()

    result_map = [len(i[1]) for i in char_map]
    to_be_modify = [int((len(i[1]) == 1 and i[1][0] == i[0])) for i in char_map]

    assert sum(result_map) == len_ref
    assert len(result_map) == len_hyp

    for_wer_gather = []
    for i in range(len(result_map)):
        for j in range(result_map[i]):
            for_wer_gather.append(i)

    is_all_one = True
    for i in to_be_modify:
        if i != 1:
            is_all_one = False

    print("##########")

    print(len(hypo_list), hypo_list)
    print(len(ref_list), ref_list)

    if not is_all_one:
        src_string = ""
        tgt_string = ""
        for i in char_map:
            if (len(i[1]) == 1 and i[1][0] == i[0]):
                src_string += (" " + i[0])
                tgt_string += (" " + i[1][0])
            else:
                src_string += (" " + i[0])
                tgt_string += (" | " + " ".join(i[1]) + " |")
        print(src_string)
        print(tgt_string)

    return result_map


def init_vec(len_hyp, len_ref):
    return_vec = []
    for i in range(len_hyp):
        to_append = []
        for j in range(len_ref):
            to_append.append([])
        return_vec.append(to_append)
    return return_vec


def judge_stage(late_stage, early_stage):
    if late_stage[0] != early_stage[0]:
        if late_stage[1] != early_stage[1]:
            return 1
        else:
            return 2
    else:
        return 3

def cal_charwer(hypo_string, ref_string):
    hypo_string = "".join(hypo_string.strip().split())
    ref_string = "".join(ref_string.strip().split())
    if hypo_string == "":
        return len(ref_string)
    if ref_string == "":
        return len(hypo_string)
    len_hyp = len(hypo_string)
    len_ref = len(ref_string)
    cost_matrix = init_number_vec(len_hyp + 1, len_ref + 1)  # np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int16)

    ops_matrix = init_number_vec(len_hyp + 1, len_ref + 1)  # np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int8)

    for i in range(len_hyp + 1):
        cost_matrix[i][0] = i
    for j in range(len_ref + 1):
        cost_matrix[0][j] = j

    id_ind = 0
    for i in range(1, len_hyp + 1):
        for j in range(1, len_ref + 1):
            ideal_index = i * len_ref / len_hyp
            if hypo_string[i - 1] == ref_string[j - 1]:
                cost_matrix[i][j] = cost_matrix[i - 1][j - 1]
            else:
                substitution = cost_matrix[i - 1][j - 1] + 1
                insertion = cost_matrix[i - 1][j] + 1
                deletion = cost_matrix[i][j - 1] + 1

                compare_val = [substitution, insertion, deletion]

                if (substitution > insertion) and (insertion == deletion):
                    min_val = insertion
                    if ideal_index >= j:
                        operation_idx = 2
                    else:
                        operation_idx = 3
                else:
                    min_val = min(compare_val)
                    operation_idx = compare_val.index(min_val) + 1
                cost_matrix[i][j] = min_val
                ops_matrix[i][j] = operation_idx
    return cost_matrix[len_hyp][len_ref]

def cal_charwer_zh(hypo_string, ref_string):
    if hypo_string == []:
        hypo_string = ""
    if ref_string == []:
        ref_string = ""
    hypo_string = "".join(hypo_string.strip().split())
    ref_string = "".join(ref_string.strip().split())
    #print(hypo_string)
    #print(ref_string)
    if hypo_string:
        hypo_string = "".join([g2pM_dict.get(i, i) for i in hypo_string])
        #hypo_string = "".join(model(hypo_string, tone=False, char_split=False))
    if ref_string:
        ref_string = "".join([g2pM_dict.get(i, i) for i in ref_string])
        #ref_string = "".join(model(ref_string, tone=False, char_split=False))
    #print(hypo_string)
    #print(ref_string)
    if hypo_string == "":
        return len(ref_string)
    if ref_string == "":
        return len(hypo_string)

    len_hyp = len(hypo_string)
    len_ref = len(ref_string)
    cost_matrix = init_number_vec(len_hyp + 1, len_ref + 1)  # np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int16)

    # 0-equal；2-insertion；3-deletion；1-substitution
    ops_matrix = init_number_vec(len_hyp + 1, len_ref + 1)  # np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int8)

    for i in range(len_hyp + 1):
        cost_matrix[i][0] = i
    for j in range(len_ref + 1):
        cost_matrix[0][j] = j

    id_ind = 0
    for i in range(1, len_hyp + 1):
        for j in range(1, len_ref + 1):
            ideal_index = i * len_ref / len_hyp
            if hypo_string[i - 1] == ref_string[j - 1]:
                cost_matrix[i][j] = cost_matrix[i - 1][j - 1]
            else:
                substitution = cost_matrix[i - 1][j - 1] + 1
                insertion = cost_matrix[i - 1][j] + 1
                deletion = cost_matrix[i][j - 1] + 1

                compare_val = [substitution, insertion, deletion]

                if (substitution > insertion) and (insertion == deletion):
                    min_val = insertion
                    if ideal_index >= j:
                        operation_idx = 2
                    else:
                        operation_idx = 3
                else:
                    min_val = min(compare_val)
                    operation_idx = compare_val.index(min_val) + 1
                cost_matrix[i][j] = min_val
                ops_matrix[i][j] = operation_idx
    return cost_matrix[len_hyp][len_ref]

# The format of gramx.txt is <space-split ngram token> \t frequency
# such as:
# good morning\t1000\n
# the gramx.txt can be calculated based on unpaired text data.

#gram2_path = '<path-to-gram2>/gram2.txt'
# print("Loading gram2:", gram2_path)
gram2_dict = {}
#with open(gram2_path, 'r',
#          encoding='utf-8') as infile:
#    for i, line in enumerate(infile.readlines()):
#        gram2_dict[line.strip().split('\t')[0]] = int(line.strip().split('\t')[1])
#        if i % 1000000 == 0:
#            print(i, 'loaded!')

#gram3_path = '<path-to-gram2>/gram3.txt'
# print("Loading gram3:", gram3_path)
gram3_dict = {}
#with open(gram3_path, 'r',
#          encoding='utf-8') as infile:
#    for i, line in enumerate(infile.readlines()):
#        gram3_dict[line.strip().split('\t')[0]] = int(line.strip().split('\t')[1])
#        if i % 2000000 == 0:
#            print(i, 'loaded!')

#MAX_OCC = max(max(gram2_dict.values()), max(gram3_dict.values()))
MAX_OCC=100

def get_lm_score(tokens):
    if len(tokens) == 2:
        return gram2_dict.get(" ".join(tokens), 0)
    if len(tokens) == 3:
        return gram2_dict.get(" ".join(tokens), 0)
    assert len(tokens) >= 1
    return 0


def is_identity_token(token):
    return token[0] == token[1]



def judge_insertion(path, insert_begin, insert_end):
    assert insert_begin >= 1
    assert insert_end <= len(path) - 2
    left_token = path[insert_begin - 1]
    right_token = path[insert_end + 1]
    to_be_align = path[insert_begin: insert_end + 1]
    if is_identity_token(left_token) and not is_identity_token(right_token):
        return cal_charwer_zh(right_token[0],
                           "".join([j[1] for j in to_be_align] + [right_token[1]])), MAX_OCC * 100, [], [j[1] for j in
                                                                                                         to_be_align]
    elif (not is_identity_token(left_token) and is_identity_token(right_token)) or (
            insert_begin == insert_end and right_token[0].startswith('▁') and '▁' not in path[insert_begin]):
        return cal_charwer_zh(left_token[0], "".join([left_token[1]] + [j[1] for j in to_be_align])), MAX_OCC * 100, [j[1]
                                                                                                                   for j
                                                                                                                   in
                                                                                                                   to_be_align], []
    elif is_identity_token(left_token) and is_identity_token(right_token):
        all_charwer = [1000 for i in range(insert_end - insert_begin + 2)]
        all_charwer[0] = cal_charwer_zh(right_token[0], "".join([j[1] for j in to_be_align] + [right_token[1]]))
        all_charwer[-1] = cal_charwer_zh(left_token[0], "".join([left_token[1]] + [j[1] for j in to_be_align]))
        if len(all_charwer) == 3:
            assert len(to_be_align) == 2
            all_charwer[1] = cal_charwer_zh(left_token[0], "".join([left_token[1]] + [j[1] for j in to_be_align[:1]])) + cal_charwer_zh(right_token[0], "".join([j[1] for j in to_be_align[1:]] + [right_token[1]]))
        elif len(all_charwer) > 3:
            assert len(to_be_align) > 2
            all_charwer[1] = cal_charwer_zh(left_token[0], "".join([left_token[1]] + [j[1] for j in to_be_align[:1]])) + cal_charwer_zh(right_token[0], "".join([j[1] for j in to_be_align[1:]] + [right_token[1]]))
            all_charwer[-2] = cal_charwer_zh(left_token[0],
                                         "".join([left_token[1]] + [j[1] for j in to_be_align[:-1]])) + cal_charwer_zh(
                right_token[0], "".join([j[1] for j in to_be_align[-1:]] + [right_token[1]]))
        else:
            # do not calculate more than 4 gram
            pass

        min_charwer = min(all_charwer)
        # print(path, insert_begin, insert_end)
        # print(all_charwer)
        for_lmrerank = [i for i in range(insert_end - insert_begin + 2) if all_charwer[i] == min_charwer]
        if len(for_lmrerank) > 1:
            # print("Use lm to judge {} from position {}".format(path, for_lmrerank))
            all_lm_score = []
            for iter_choice in for_lmrerank:
                all_lm_score.append(
                    get_lm_score(
                        [left_token[1]] + [j[1] for j in to_be_align[:iter_choice]]
                    ) + get_lm_score(
                        [j[1] for j in to_be_align[iter_choice:]] + [right_token[1]]
                    )
                )
            max_lm_score = max(all_lm_score)
            max_lm_id = [i for i, j in zip(for_lmrerank, all_lm_score) if j == max_lm_score]
            half_value = (insert_end - insert_begin + 2) / 2 - 0.01
            final_choice = max_lm_id[0]
            dis2centor = (final_choice - half_value) ** 2
            for new_choice in max_lm_id[1:]:
                if (new_choice - half_value) ** 2 < dis2centor:
                    final_choice = new_choice
                    dis2centor = (new_choice - half_value) ** 2
        else:
            max_lm_score = MAX_OCC * 100
            final_choice = for_lmrerank[0]
        return min_charwer, max_lm_score, [j[1] for j in to_be_align[:final_choice]], [j[1] for j in
                                                                                       to_be_align[final_choice:]]
    else:
        all_charwer = [0 for i in range(insert_end - insert_begin + 2)]
        for i in range(insert_end - insert_begin + 2):
            all_charwer[i] = cal_charwer_zh(left_token[0], "".join(
                [left_token[1]] + [j[1] for j in to_be_align[:i]]
            )
                                         ) + cal_charwer_zh(right_token[0], "".join(
                [j[1] for j in to_be_align[i:]] + [right_token[1]]
            )
                                                         )
        min_charwer = min(all_charwer)
        for_lmrerank = [i for i in range(insert_end - insert_begin + 2) if all_charwer[i] == min_charwer]
        if len(for_lmrerank) > 1:
            all_lm_score = []
            for iter_choice in for_lmrerank:
                all_lm_score.append(
                    get_lm_score(
                        [left_token[1]] + [j[1] for j in to_be_align[:iter_choice]]
                    ) + get_lm_score(
                        [j[1] for j in to_be_align[iter_choice:]] + [right_token[1]]
                    )
                )
            max_lm_score = max(all_lm_score)
            max_lm_id = [i for i, j in zip(for_lmrerank, all_lm_score) if j == max_lm_score]
            half_value = (insert_end - insert_begin + 2) / 2 - 0.01
            final_choice = max_lm_id[0]
            dis2centor = (final_choice - half_value) ** 2
            for new_choice in max_lm_id[1:]:
                if (new_choice - half_value) ** 2 < dis2centor:
                    final_choice = new_choice
                    dis2centor = (new_choice - half_value) ** 2
        else:
            max_lm_score = MAX_OCC * 100
            final_choice = for_lmrerank[0]
        return min_charwer, max_lm_score, [j[1] for j in to_be_align[:final_choice]], [j[1] for j in
                                                                                       to_be_align[final_choice:]]


def cal_min_align(path):
    # path: [([], 'a'), ('b', 'b'), ('b', 'c'), ('d', 'd'), ('e', []), ('f', 'f')]
    path_char_wer = 0
    for i in path:
        path_char_wer += cal_charwer_zh(i[0], i[1])
    char_wer = 0
    return_match = [[i[0], []] for i in path if i[0]]

    assert len(return_match) != 0, "meet empty src!"
    begin = 0
    while path[begin][0] == []:
        return_match[0][-1].append(path[begin][1])
        begin += 1

    end = len(path) - 1
    while path[end][0] == []:
        return_match[-1][-1].insert(0, path[end][1])
        end -= 1

    lm_score = 0
    # new_charwer

    index_match = 0
    i = begin
    while i <= end:
        if path[i][0]:
            assert path[i][0] == return_match[index_match][0]
            if path[i][1]:
                return_match[index_match][-1].append(path[i][1])
            i += 1
            index_match += 1
        else:
            insert_begin = i
            i += 1
            while not path[i][0]:
                i += 1
            insert_end = i - 1
            _, new_lm_score, left_align, right_align = judge_insertion(path, insert_begin, insert_end)
            return_match[index_match - 1][1].extend(left_align)
            return_match[index_match][1].extend(right_align)
            # print(index_match, return_match, left_align, right_align)
            lm_score += new_lm_score

    for match_case in return_match:
        char_wer += cal_charwer_zh(match_case[0], "".join(match_case[1]))

    return path_char_wer, char_wer, lm_score, return_match


def calculate_wer_dur_1beam(hypo_list, ref_list):
    len_hyp = len(hypo_list)
    len_ref = len(ref_list)
    cost_matrix = init_number_vec(len_hyp + 1, len_ref + 1)  # np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int16)

    forward_matrix = init_vec(len_hyp + 1, len_ref + 1)
    backward_matrix = init_vec(len_hyp + 1, len_ref + 1)

    path_num_matrix_for = init_number_vec(len_hyp + 1,
                                          len_ref + 1)  # np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int16)
    path_num_matrix_back = init_number_vec(len_hyp + 1,
                                           len_ref + 1)  # np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int16)

    # 0-equal；2-insertion；3-deletion；1-substitution
    # ops_matrix = np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int8)

    cost_matrix[0][0] = 0
    path_num_matrix_for[0][0] = 1

    for i in range(1, len_hyp + 1):
        cost_matrix[i][0] = i
        forward_matrix[i - 1][0].append([i, 0])
        backward_matrix[i][0].append([i - 1, 0])
        path_num_matrix_for[i][0] += 1

    for j in range(1, len_ref + 1):
        cost_matrix[0][j] = j
        forward_matrix[0][j - 1].append([0, j])
        backward_matrix[0][j].append([0, j - 1])
        path_num_matrix_for[0][j] += 1

    id_ind = 0
    for i in range(1, len_hyp + 1):
        for j in range(1, len_ref + 1):
            # ideal_index = i * len_ref / len_hyp
            if hypo_list[i - 1] == ref_list[j - 1]:
                cost_matrix[i][j] = cost_matrix[i - 1][j - 1]
                forward_matrix[i - 1][j - 1].append([i, j])
                backward_matrix[i][j].append([i - 1, j - 1])
                path_num_matrix_for[i][j] += path_num_matrix_for[i - 1][j - 1]
                assert (cost_matrix[i - 1][j] + 1) >= cost_matrix[i][j]
                assert (cost_matrix[i][j - 1] + 1) >= cost_matrix[i][j]
                if cost_matrix[i][j] == (cost_matrix[i - 1][j] + 1):
                    forward_matrix[i - 1][j].append([i, j])
                    backward_matrix[i][j].append([i - 1, j])
                    path_num_matrix_for[i][j] += path_num_matrix_for[i - 1][j]
                if cost_matrix[i][j] == (cost_matrix[i][j - 1] + 1):
                    forward_matrix[i][j - 1].append([i, j])
                    backward_matrix[i][j].append([i, j - 1])
                    path_num_matrix_for[i][j] += path_num_matrix_for[i][j - 1]
            else:
                substitution = cost_matrix[i - 1][j - 1] + 1
                insertion = cost_matrix[i - 1][j] + 1
                deletion = cost_matrix[i][j - 1] + 1

                compare_val = [substitution, insertion, deletion]

                min_val = min(compare_val)
                if substitution == min_val:
                    forward_matrix[i - 1][j - 1].append([i, j])
                    backward_matrix[i][j].append([i - 1, j - 1])
                    path_num_matrix_for[i][j] += path_num_matrix_for[i - 1][j - 1]
                if insertion == min_val:
                    forward_matrix[i - 1][j].append([i, j])
                    backward_matrix[i][j].append([i - 1, j])
                    path_num_matrix_for[i][j] += path_num_matrix_for[i - 1][j]
                if deletion == min_val:
                    forward_matrix[i][j - 1].append([i, j])
                    backward_matrix[i][j].append([i, j - 1])
                    path_num_matrix_for[i][j] += path_num_matrix_for[i][j - 1]

                cost_matrix[i][j] = min_val

    path_num_matrix_back[len_hyp][len_ref] = path_num_matrix_for[len_hyp][len_ref]
    stack = [[len_hyp, len_ref]]
    while stack:
        currect_stage = stack[0]
        stack.remove(currect_stage)
        currect_path = path_num_matrix_back[currect_stage[0]][currect_stage[1]]
        all_back_stage = backward_matrix[currect_stage[0]][currect_stage[1]]
        all_back_weight = []
        for i in all_back_stage:
            all_back_weight.append(path_num_matrix_for[i[0]][i[1]])
        for i in range(len(all_back_stage)):
            new_stage = all_back_stage[i]
            path_num_matrix_back[new_stage[0]][new_stage[1]] += currect_path / (sum(all_back_weight)) * all_back_weight[
                i]
            if new_stage != [0, 0] and new_stage not in stack:
                insert_index = 0
                if not stack:
                    stack.append(new_stage)
                else:
                    while sum(new_stage) < sum(stack[insert_index]):
                        insert_index += 1
                        if insert_index == len(stack):
                            break
                    stack.insert(insert_index, new_stage)

    # collect all path:
    all_path = []
    all_path_identity = []
    path_id_matrix = init_vec(len_hyp + 1, len_ref + 1)
    path_id_matrix[len_hyp][len_ref].append(0)
    all_path_identity.append(0)
    all_path.append([])
    stack = [[len_hyp, len_ref]]
    while stack:
        currect_stage = stack[0]
        stack.remove(currect_stage)
        # currect_path = path_num_matrix_back[currect_stage[0]][currect_stage[1]]
        all_back_stage = backward_matrix[currect_stage[0]][currect_stage[1]]

        if len(all_back_stage) > 1:
            for new_stage in all_back_stage[1:]:
                for path_id in path_id_matrix[currect_stage[0]][currect_stage[1]]:
                    new_path_id = len(all_path)
                    new_path = copy.deepcopy(all_path[path_id])
                    new_identity = all_path_identity[path_id]
                    op_type = judge_stage(currect_stage, new_stage)
                    if op_type == 1:
                        new_path.append((hypo_list[new_stage[0]], ref_list[new_stage[1]]))
                        if hypo_list[new_stage[0]] == ref_list[new_stage[1]]:
                            new_identity += 1
                    elif op_type == 2:
                        new_path.append((hypo_list[new_stage[0]], []))
                    else:
                        assert op_type == 3
                        new_path.append(([], ref_list[new_stage[1]]))
                    all_path.append(new_path)
                    all_path_identity.append(new_identity)
                    path_id_matrix[new_stage[0]][new_stage[1]].append(new_path_id)
                if new_stage != [0, 0] and new_stage not in stack:
                    insert_index = 0
                    if not stack:
                        stack.append(new_stage)
                    else:
                        while sum(new_stage) < sum(stack[insert_index]):
                            insert_index += 1
                            if insert_index == len(stack):
                                break
                        stack.insert(insert_index, new_stage)

        new_stage = all_back_stage[0]
        for path_id in path_id_matrix[currect_stage[0]][currect_stage[1]]:
            op_type = judge_stage(currect_stage, new_stage)
            if op_type == 1:
                all_path[path_id].append((hypo_list[new_stage[0]], ref_list[new_stage[1]]))
                if hypo_list[new_stage[0]] == ref_list[new_stage[1]]:
                    all_path_identity[path_id] += 1
            elif op_type == 2:
                all_path[path_id].append((hypo_list[new_stage[0]], []))
            else:
                assert op_type == 3
                all_path[path_id].append(([], ref_list[new_stage[1]]))
            path_id_matrix[new_stage[0]][new_stage[1]].append(path_id)

        if new_stage != [0, 0] and new_stage not in stack:
            insert_index = 0
            if not stack:
                stack.append(new_stage)
            else:
                while sum(new_stage) < sum(stack[insert_index]):
                    insert_index += 1
                    if insert_index == len(stack):
                        break
                stack.insert(insert_index, new_stage)

    assert path_num_matrix_back[len_hyp][len_ref] == len(all_path)

    max_identity = max(all_path_identity)

    path4rerank = []
    for path, identity_value in zip(all_path, all_path_identity):
        if identity_value == max_identity:
            path4rerank.append(copy.deepcopy(path))
            path4rerank[-1].reverse()

    path_scores = []
    path_matchs = []
    path_id_scores = []
    min_char_wer = 10000
    min_path_char_wer = 10000
    max_lm_score = -10000
    max_final_id_score = -10000
    best_path_match = []
    best_path = None
    for path in path4rerank:
        path_char_wer, char_wer, lm_score, match_case = cal_min_align(path)
        final_id_score = sum([int(len(i[1]) == 1 and i[0] == i[1][0]) for i in match_case])
        path_id_scores.append(final_id_score)
        path_scores.append((char_wer, path_char_wer, lm_score))
        path_matchs.append(match_case)
        if final_id_score > max_final_id_score:
            best_path_match = match_case
            best_path = path
            max_lm_score = lm_score
            min_char_wer = char_wer
            min_path_char_wer = path_char_wer
            max_final_id_score = final_id_score
        elif final_id_score == max_final_id_score:
            if char_wer < min_char_wer:
                best_path_match = match_case
                best_path = path
                max_lm_score = lm_score
                min_char_wer = char_wer
                min_path_char_wer = path_char_wer
            elif char_wer == min_char_wer:
                if path_char_wer < min_path_char_wer:
                    best_path_match = match_case
                    best_path = path
                    max_lm_score = lm_score
                    min_path_char_wer = path_char_wer
                elif path_char_wer == min_path_char_wer:
                    best_path_match = match_case
                    best_path = path
                    max_lm_score = lm_score

    return best_path_match, best_path, min_path_char_wer

def calculate_wer_dur_v1(hypo_list, ref_list, return_path_only=False):
    len_hyp = len(hypo_list)
    len_ref = len(ref_list)
    for token in hypo_list:
        if len(token) == 1:
            if '\u4e00' <= token[0] <= '\u9fa5' or '\u3400' <= token[0] <= '\u4DB5':  # 汉字
                ch = token[0]
                if not g2pM_dict.__contains__(ch):  #英文字母或特殊符号的拼音是它本身，不加入 g2pM_dict
                    g2pM_dict[ch] = preprocess.unify_pinyin(model(ch, tone=False, char_split=True)[0])
    for token in ref_list:
        if len(token) == 1:
            if '\u4e00' <= token[0] <= '\u9fa5' or '\u3400' <= token[0] <= '\u4DB5':  # 汉字
                ch = token[0]
                if not g2pM_dict.__contains__(ch): #英文字母或特殊符号的拼音是它本身，不加入 g2pM_dict
                    g2pM_dict[ch] = preprocess.unify_pinyin(model(ch, tone=False, char_split=True)[0])
    cost_matrix = init_number_vec(len_hyp + 1, len_ref + 1)  # np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int16)

    forward_matrix = init_vec(len_hyp + 1, len_ref + 1)
    backward_matrix = init_vec(len_hyp + 1, len_ref + 1)

    path_num_matrix_for = init_number_vec(len_hyp + 1,
                                          len_ref + 1)  # np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int16)
    path_num_matrix_back = init_number_vec(len_hyp + 1,
                                           len_ref + 1)  # np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int16)

    # 0-equal；2-insertion；3-deletion；1-substitution
    # ops_matrix = np.zeros((len_hyp + 1, len_ref + 1), dtype=np.int8)

    cost_matrix[0][0] = 0
    path_num_matrix_for[0][0] = 1

    for i in range(1, len_hyp + 1):
        cost_matrix[i][0] = i
        forward_matrix[i - 1][0].append([i, 0])
        backward_matrix[i][0].append([i - 1, 0])
        path_num_matrix_for[i][0] += 1

    for j in range(1, len_ref + 1):
        cost_matrix[0][j] = j
        forward_matrix[0][j - 1].append([0, j])
        backward_matrix[0][j].append([0, j - 1])
        path_num_matrix_for[0][j] += 1

    id_ind = 0
    for i in range(1, len_hyp + 1):
        for j in range(1, len_ref + 1):
            if hypo_list[i - 1] == ref_list[j - 1]:
                cost_matrix[i][j] = cost_matrix[i - 1][j - 1]
                forward_matrix[i - 1][j - 1].append([i, j])
                backward_matrix[i][j].append([i - 1, j - 1])
                path_num_matrix_for[i][j] += path_num_matrix_for[i - 1][j - 1]
                assert (cost_matrix[i - 1][j] + 1) >= cost_matrix[i][j]
                assert (cost_matrix[i][j - 1] + 1) >= cost_matrix[i][j]
                if cost_matrix[i][j] == (cost_matrix[i - 1][j] + 1):
                    forward_matrix[i - 1][j].append([i, j])
                    backward_matrix[i][j].append([i - 1, j])
                    path_num_matrix_for[i][j] += path_num_matrix_for[i - 1][j]
                if cost_matrix[i][j] == (cost_matrix[i][j - 1] + 1):
                    forward_matrix[i][j - 1].append([i, j])
                    backward_matrix[i][j].append([i, j - 1])
                    path_num_matrix_for[i][j] += path_num_matrix_for[i][j - 1]
            else:
                substitution = cost_matrix[i - 1][j - 1] + 1
                insertion = cost_matrix[i - 1][j] + 1
                deletion = cost_matrix[i][j - 1] + 1

                compare_val = [substitution, insertion, deletion]

                min_val = min(compare_val)
                if substitution == min_val:
                    forward_matrix[i - 1][j - 1].append([i, j])
                    backward_matrix[i][j].append([i - 1, j - 1])
                    path_num_matrix_for[i][j] += path_num_matrix_for[i - 1][j - 1]
                if insertion == min_val:
                    forward_matrix[i - 1][j].append([i, j])
                    backward_matrix[i][j].append([i - 1, j])
                    path_num_matrix_for[i][j] += path_num_matrix_for[i - 1][j]
                if deletion == min_val:
                    forward_matrix[i][j - 1].append([i, j])
                    backward_matrix[i][j].append([i, j - 1])
                    path_num_matrix_for[i][j] += path_num_matrix_for[i][j - 1]

                cost_matrix[i][j] = min_val
    path_num_matrix_back[len_hyp][len_ref] = path_num_matrix_for[len_hyp][len_ref]
    stack = [[len_hyp, len_ref]]
    while stack:
        currect_stage = stack[0]
        stack.remove(currect_stage)
        currect_path = path_num_matrix_back[currect_stage[0]][currect_stage[1]]
        all_back_stage = backward_matrix[currect_stage[0]][currect_stage[1]]
        all_back_weight = []
        for i in all_back_stage:
            all_back_weight.append(path_num_matrix_for[i[0]][i[1]])
        for i in range(len(all_back_stage)):
            new_stage = all_back_stage[i]
            path_num_matrix_back[new_stage[0]][new_stage[1]] += currect_path / (sum(all_back_weight)) * all_back_weight[
                i]
            if new_stage != [0, 0] and new_stage not in stack:
                insert_index = 0
                if not stack:
                    stack.append(new_stage)
                else:
                    while sum(new_stage) < sum(stack[insert_index]):
                        insert_index += 1
                        if insert_index == len(stack):
                            break
                    stack.insert(insert_index, new_stage)

    max_path = path_num_matrix_back[len_hyp][len_ref]
    all_dia_value = [0 for i in range(len_ref + len_hyp + 1)]
    for i in range(0, len_hyp + 1):
        for j in range(0, len_ref + 1):
            if path_num_matrix_back[i][j] == max_path:
                assert all_dia_value[i + j] == 0
                all_dia_value[i + j] = (i, j)

    all_dia_value = [i for i in all_dia_value if i != 0]

    if len(all_dia_value) < 5:
        all_parts = [(hypo_list, ref_list)]
    else:
        all_parts = []
        all_split = [(0, 0)]
        for i in range(2, len(all_dia_value) - 1):
            if (all_dia_value[i - 1][0] - all_dia_value[i - 2][0] > 1) or (
                    all_dia_value[i - 1][1] - all_dia_value[i - 2][1] > 1):
                if (all_dia_value[i][0] - all_dia_value[i - 1][0] == 1) or (
                        all_dia_value[i][1] - all_dia_value[i - 1][1] == 1):
                    if hypo_list[all_dia_value[i][0] - 1] == ref_list[all_dia_value[i][1] - 1]:
                        all_split.append(all_dia_value[i])
        all_split.append((len_hyp, len_ref))

        if len(all_split) == 2:
            all_parts = [(hypo_list, ref_list)]
        else:
            hypo_start = 0
            ref_start = 0
            for i in range(1, len(all_split) - 1):
                all_parts.append((hypo_list[hypo_start:all_split[i][0]], ref_list[ref_start:all_split[i][1]]))
                hypo_start = all_split[i][0] - 1
                ref_start = all_split[i][1] - 1
            all_parts.append((hypo_list[hypo_start:], ref_list[ref_start:]))

    # print("len(all_parts):", len(all_parts))
    # print(all_parts)

    if len(all_parts) == 1:
        final_match, final_best_path, final_min_path_char_wer = calculate_wer_dur_1beam(all_parts[0][0], all_parts[0][1])
    else:
        all_inter_results = [calculate_wer_dur_1beam(i[0], i[1]) for i in all_parts]
        all_parts_match = [i[0] for i in all_inter_results]
        all_final_best_path = [i[1] for i in all_inter_results]
        final_min_path_char_wer = sum([i[2] for i in all_inter_results])
        # all_parts_match, final_best_path, _
        for i in range(0, len(all_parts_match) - 1):
            try:
                if all_parts_match[i][-1][1]:
                    assert all_parts_match[i][-1][0] == all_parts_match[i][-1][1][-1]
                if i != 0:
                    assert all_final_best_path[i][0] == all_final_best_path[i-1][-1]
                # assert len(all_parts_match[i][-1][1]) == 1
            except:
                raise_again = True
                if all_parts_match[i][-1][1]:
                    assert all_parts_match[i][-1][0] == all_parts_match[i][-1][1][-1]
                if i != 0:
                    assert all_final_best_path[i][0] != all_final_best_path[i-1][-1]
                    assert (all_final_best_path[i][0][0] != [] or all_final_best_path[i][0][1] != [])
                    assert (all_final_best_path[i-1][-1][0] != [] or all_final_best_path[i-1][-1][1] != [])
                    assert not (is_identity_token(all_final_best_path[i][0]) and is_identity_token(all_final_best_path[i-1][-1]))
                    if is_identity_token(all_final_best_path[i-1][-1]):
                        tmp_token = copy.deepcopy(all_final_best_path[i-1][-1])
                        all_final_best_path[i-1][-1] = copy.deepcopy(all_final_best_path[i][0])
                        all_final_best_path[i][0] = tmp_token
                        raise_again = False
                    elif is_identity_token(all_final_best_path[i][0]):
                        raise_again = False
                    else:
                        # skip this condition ( do not verify whether this condition exists, but the ratio is quite small
                        return None
                if raise_again:
                    print(i, all_parts_match)
                    print(hypo_list)
                    print(ref_list)
                    raise ValueError()
        # print(all_parts_match)
        final_match = all_parts_match[0]
        final_best_path = all_final_best_path[0]
        for i in range(1, len(all_parts_match)):
            if final_match[-1][1] == [] and all_parts_match[i][0][1] == []:
                # skip this condition ( do not verify whether this condition exists, but the ratio is quite small
                return None
            if final_match[-1][1] != []:
                final_match[-1][1] = final_match[-1][1][:-1]
                final_match[-1][1].extend(all_parts_match[i][0][1])
                final_match.extend(all_parts_match[i][1:])
            else:
                final_match[-1][1].extend(all_parts_match[i][0][1][1:])
                final_match.extend(all_parts_match[i][1:])
            final_best_path.extend(all_final_best_path[i][1:])
    if return_path_only:
        return final_best_path
    is_all_one = True
    for i in final_match:
        if len(i[1]) != 1 or i[0] != i[1][0]:
            is_all_one = False

    result_map = [len(i[1]) for i in final_match]
    to_be_modify = []
    for i in final_match:
        if (len(i[1]) == 1 and i[1][0] == i[0]):
            to_be_modify.append(1)
        else:
            to_be_modify.append(-1)

    assert sum(result_map) == len_ref, "{}, {}, {}".format(str(final_match), str(hypo_list), str(ref_list))
    assert len(result_map) == len_hyp

    return [i * j for i, j in zip(result_map, to_be_modify)], final_min_path_char_wer
