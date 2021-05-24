import argparse
import os
from collections import Counter
import matplotlib.pyplot as plt
import sys
from tqdm import tqdm
import numpy as np

### REWRITE TGT BY REPLACING UNPREDICTABLE WORDS BY <UNK>
def rewrite_tgt(path_to_here, path_to_src, path_to_tgt, path_to_voc):   
    ## GETTING SRC TEST
    src_lines = []    
    with open(path_to_src, 'r') as src_file:
        src_lines = src_file.readlines()
    
    ## GETTING TGT TEST 
    tgt_lines = []
    with open(path_to_tgt, 'r') as tgt_file:    
        tgt_lines = tgt_file.readlines()

    ## GETTING VOC
    voc = set()
    with open(path_to_voc, 'r') as voc_file:    
        voc = set([tok.strip() for tok in voc_file.readlines()])
    ## INSERTING <UNK>
    len_files = len(src_lines)
    new_tgt = [0] * len_files
    for line_index in range(len_files):
        src_tokens = set(src_lines[line_index].split())
        if len(src_tokens) > 0:
            new_tgt[line_index] = " ".join([token if token in voc or token in src_tokens else "<unk>" for token in tgt_lines[line_index].split()])
    ## WRITING NEW TGT
    with open(os.path.join(path_to_here, "../new_tgt.txt"), 'a') as new_tgt_file:
        for line in new_tgt:
            new_tgt_file.write(line + "\n")
    
def get_easy_accuracy(path_to_here, path_to_src, path_to_tgt, path_to_voc, len_thresh, edist_tresh):
    path_to_pred = os.path.join(path_to_here, "../Golden/pred-test-golden_beam50.txt")

    ## GETTING GOLDEN TEST PRED
    pred_lines = []
    with open(path_to_pred, 'r') as pred_file:    
        pred_lines = pred_file.readlines()

    ## GETTING SRC TEST
    src_lines = []    
    with open(path_to_src, 'r') as src_file:
        src_lines = src_file.readlines()
    
    ## GETTING TGT TEST 
    tgt_lines = []
    with open(path_to_tgt, 'r') as tgt_file:    
        tgt_lines = tgt_file.readlines()

    ## GETTING VOC
    voc = set()
    with open(path_to_voc, 'r') as voc_file:    
        voc = set([tok.strip() for tok in voc_file.readlines()])

    line_idxes = list(range(len(tgt_lines)))
    ## REMOVING ALL "HARD" CASES
    for idx in range(len(tgt_lines)):
        ## REMOVING IDX OF IMPOSSIBLE TO PREDICT SAMPLES (OOV PROBLEM)
        removed = False
        src_voc = set(src_lines[idx].split())
        for token in tgt_lines[idx].split():
            if token not in voc and token not in src_voc:
                line_idxes.remove(idx)
                removed = True            
                break
        if not removed:
            line = src_lines[idx]
            splitted_line = line.split()
            if "<START_BUG>" in splitted_line and "<END_BUG>" in splitted_line:
                start_idx = splitted_line.index("<START_BUG>")
                end_idx = splitted_line.index("<END_BUG>")
                bug_length = end_idx-start_idx - 1
                ## REMOVING BUGGY LINES WITH MORE THAN 30 TOKENS
                if bug_length > len_thresh:
                    line_idxes.remove(idx)
                    removed = True
                else:
                    ## REMOVING BUGGY LINES WITH AN EDIT DISTANCE BIGGER THAN 15
                    bug = splitted_line[start_idx+1:end_idx]
                    tgt = tgt_lines[idx].split()
                    edit_dist = levenshtein(bug, tgt)
                    if edit_dist > edist_tresh:
                        line_idxes.remove(idx)
            else:
                line_idxes.remove(idx)
    
    tot_count = 0
    good_count = 0
    for easy_idx in line_idxes:
        if len(tgt_lines[easy_idx]) > 0:
            tot_count += 1
            if tgt_lines[easy_idx].strip() in [line.strip() for line in pred_lines[easy_idx*50:easy_idx*50+50]]:
                good_count += 1
    #print(f"Easy Accuracy: {good_count}/{tot_count}")
    return good_count, tot_count

def easier_data_graphs(path_to_here, path_to_src, path_to_tgt, path_to_voc):
    len_threshs = range(10,100, 2)
    len_accs = [[0, 0] for _ in range(len(len_threshs))]
    edist_threshs = range(1, 30)
    edist_accs = [[0, 0] for _ in range(len(edist_threshs))]
    
    for x in range(len(edist_threshs)):
        edist_accs[x][0], edist_accs[x][1] = get_easy_accuracy(path_to_here, path_to_src, path_to_tgt, path_to_voc, 10000 , edist_threshs[x]) 
    
    plt.xlabel("Edit distance between the buggy line and its fix")
    plt.plot(edist_threshs, [(x1*1.0)/(x2*1.0) for x1, x2 in edist_accs], 'b') 
    plt.ylabel("Accuracy", color="b")
    plt.tick_params(axis="y", labelcolor='b')
    plt.twinx()
    plt.plot(edist_threshs, [x[1] for x in edist_accs], 'r')
    plt.ylabel("Total number of samples", color="r")
    plt.tick_params(axis="y", labelcolor='r')
    plt.title("Effect of the edit distance on the accuracy of the Golden model")
    
    
    plt.savefig("Effect of the edit distance on the accuracy of the Golden model.png")

    print("Done")
            



### OOV ###
def oov(path_to_src, path_to_tgt, path_to_train):
    ## GETTING SRC TEST
    src_lines = []    
    with open(path_to_src, 'r') as src_file:
        src_lines = src_file.readlines()
    src_lines_lower = [line.lower() for line in src_lines]
    
    ## BUILDING VOC FROM TRAIN
    full_counter = []
    with open(path_to_train) as train_file:
        all_src = []
        for line in train_file.readlines():
            for word in line.strip().split():
                all_src.append(word.strip())
        full_counter = Counter(all_src)
    most_commons = full_counter.most_common()
    ## GETTING TGT TEST 
    tgt_lines = []
    with open(path_to_tgt, 'r') as tgt_file:    
        tgt_lines = tgt_file.readlines()
    tgt_lines_lower = [line.lower() for line in tgt_lines]    

    ## GETTING OOV values for range of voc_sizes
    voc_sizes = range(0, len(most_commons), 250)
    #voc_sizes = range(0, 5000, 25)
    #voc_sizes = [10**i for i in range(0,8)]
    imposs_list = [0] * len(voc_sizes)
    imposs_list_lower = [0] * len(voc_sizes)

    for idx in tqdm(range(len(voc_sizes))):
        voc_size = voc_sizes[idx]
        voc = set(x[0] for x in most_commons[:voc_size])
        impossible_nb, tot_nb = get_impossible_count(voc, src_lines, tgt_lines)
        imposs_list[idx] = impossible_nb
        voc2 = set([x.lower() for x in voc])
        impossible_nb_lower, tot_nb = get_impossible_count(voc2, src_lines_lower, tgt_lines_lower)
        imposs_list_lower[idx] = impossible_nb_lower

    ## PLOTTING
    our_voc_idx = [voc_sizes.index(1000)]
    plt.plot(voc_sizes, [round((float(imp_nb)/float(tot_nb))*100, 2) for imp_nb in imposs_list], 'b', label="Keeping the different cases")    
    plt.plot(voc_sizes[our_voc_idx[0]], [round((float(imposs_list[our_voc_idx[0]])/float(tot_nb))*100, 2)], 'bo')
    plt.plot(voc_sizes, [round((float(imp_nb)/float(tot_nb))*100, 2) for imp_nb in imposs_list_lower], 'r', label="To lower case")
    plt.plot(voc_sizes[our_voc_idx[0]], [round((float(imposs_list_lower[our_voc_idx[0]])/float(tot_nb))*100, 2)], 'ro')
    #plt.xscale('log')
    plt.axvline(1000)
    #xticks_vals = list(range(0, 20000, 2500)) + [1000]
    #plt.xticks(xticks_vals)
    plt.title("Effect of the vocabulary size on the OOV problem")
    plt.xlabel("Vocabulary size [# of types]")
    plt.ylabel("Unpredictable samples [% of the full test set]")
    plt.legend()
    plt.savefig("Effect of the vocabulary size on the OOV problem.png")

    print("Done")
    #print(f"There are {impossible_nb}/{tot_nb} ({round((float(impossible_nb)/float(tot_nb))*100, 2)}%) samples impossible to predict due to OOV tokens")


def get_impossible_count(voc, src_lines, tgt_lines):   
    len_files = len(src_lines)
    tot_nb = 0
    impossible_nb = 0
    for line_index in range(len_files):
        src_tokens = set(src_lines[line_index].split())
        if len(src_tokens) > 0:
            tot_nb += 1
            for token in set(tgt_lines[line_index].split()):
                if token not in voc and token not in src_tokens:
                    impossible_nb += 1
                    break
    return impossible_nb, tot_nb


### UNK ###
def unk(path_to_src, path_to_train):
    ## Getting test src
    src_lines = []    
    with open(path_to_src, 'r') as src_file:
        src_lines = src_file.readlines()
    
    ## Getting train data to build voc
    full_counter = []
    with open(path_to_train) as train_file:
        all_src = []
        for line in train_file.readlines():
            for word in line.strip().split():
                all_src.append(word.strip())
        full_counter = Counter(all_src)
    most_commons = full_counter.most_common()

    voc = set(x[0] for x in most_commons[:1000])
    ## Getting unk percentage for range of voc sizes
    #voc_sizes = range(0, len(most_commons), 500)
    voc_sizes = range(0, 5000, 25)
    #voc_sizes = [10**i for i in range(0,7)]
    mean_unk_perc_list = [0] * len(voc_sizes)
    for idx in tqdm(range(len(voc_sizes))):
        voc_size = voc_sizes[idx]
        voc = set(x[0] for x in most_commons[:voc_size])
        tmp_unk_prc = get_mean_unk_percentage(voc, src_lines)
        mean_unk_perc_list[idx] = sum(tmp_unk_prc)/float(len(tmp_unk_prc))
    
    ## PLOTTING
    our_voc_idx = voc_sizes.index(1000)
    plt.plot(voc_sizes, mean_unk_perc_list, 'r')    
    #plt.plot(voc_sizes[our_voc_idx], mean_unk_perc_list[our_voc_idx], 'bo')
    #plt.xscale('log')
    plt.axvline(1000)
    plt.ylim(0, 100)
    plt.title("Vocabulary size vs <unk> percentage in the input")
    plt.xlabel("Vocabulary size [# of types]")
    plt.ylabel("Mean percentage of <unk> [% of abstract buggy context]")
    #plt.legend()
    plt.savefig("Vocabulary size vs <unk> percentage in the input_zoom.png")

    print("Done")

def get_mean_unk_percentage(voc, src_lines):   
    len_files = len(src_lines)
    mean_unk = []
    for line_index in range(len_files):
        is_unk = [tok not in voc for tok in src_lines[line_index].split()]
        unk_nb = sum(is_unk)
        tot_nb = len(is_unk)
        unk_perc = (float(unk_nb)/float(tot_nb))*100
        mean_unk += [unk_perc]
    return mean_unk #/float(len_files)

## TYPE/TOKEN ratio
def type_usage(path_to_src, path_to_voc):
    src_lines = []
    with open(path_to_src, 'r') as src_file:
        src_lines = src_file.readlines()

    ## GETTING VOC
    voc = set()
    with open(path_to_voc, 'r') as voc_file:    
        voc = set([tok.strip() for tok in voc_file.readlines()])
    
    ratio_list = [0]*len(src_lines)
    for line_idx in range(len(src_lines)):
        line = src_lines[line_idx]
        splitted_line = line.split()
        for word in splitted_line:
            if word in voc:
                splitted_line.remove(word)
        type_cnt = len(set(splitted_line))
        token_cnt = len(splitted_line)
        ratio_list[line_idx] = token_cnt/type_cnt
    
    plt.hist(ratio_list, bins=[1, 2, 3, 4, 5, 6, 7, 8], align='left', rwidth=0.5)
    plt.xlim(0, 8)
    plt.xlabel("Token/type ratio")
    plt.ylabel("Nb of samples")
    plt.title("Type/token ratios for oov words in the test source samples")
    plt.savefig("Type_token ratio for oov words in the test source samples.png")

## BUGGY LINE LENGTHS
def get_buggy_line_length(path_to_src):
    src_lines = []
    with open(path_to_src, 'r') as src_file:
        src_lines = src_file.readlines()
    
    bug_lengths = []
    for line_idx in range(len(src_lines)):
        line = src_lines[line_idx]
        splitted_line = line.split()
        if "<START_BUG>" in splitted_line and "<END_BUG>" in splitted_line:
            start_idx = splitted_line.index("<START_BUG>")
            end_idx = splitted_line.index("<END_BUG>")
            bug_lengths.append(end_idx-start_idx - 1)
    
    plt.figure(figsize=(16, 9), dpi=200)
    plt.hist(bug_lengths, bins=range(0, 100, 1), align='left', rwidth=0.5)
    plt.xticks(range(0, 100,5))
    plt.xlim(0, 100)
    plt.xlabel("Nb of tokens")
    plt.ylabel("Nb of samples")
    plt.title("Number of token in the test buggy lines")
    plt.savefig("Number of token in the test buggy lines.png")


## EDIT DISTANCES BETWEEN BUGS AND FIXES
def get_line_fix_diff(path_to_src, path_to_tgt):
    src_lines = []
    with open(path_to_src, 'r') as src_file:
        src_lines = src_file.readlines()

    tgt_lines = []
    with open(path_to_tgt, 'r') as tgt_file:
        tgt_lines = tgt_file.readlines()
    
    diff_lengths = []
    for line_idx in range(len(src_lines)):
        line = src_lines[line_idx]
        splitted_line = line.split()
        if "<START_BUG>" in splitted_line and "<END_BUG>" in splitted_line:
            start_idx = splitted_line.index("<START_BUG>")
            end_idx = splitted_line.index("<END_BUG>")
            bug = splitted_line[start_idx+1:end_idx]
            tgt = tgt_lines[line_idx].split()
            diff_lengths.append(levenshtein(bug, tgt))
    
    plt.figure(figsize=(16, 9), dpi=200)
    plt.hist(diff_lengths, bins=range(0, 30, 1), align='left', rwidth=0.5)
    plt.xticks(range(0, 30, 5))
    plt.xlim(0, 30)
    plt.xlabel("Nb of tokens")
    plt.ylabel("Nb of samples")
    plt.title("Difference in the number of tokens between the buggy and the fixed line")
    plt.savefig("Difference in the number of tokens between the buggy and the fixed line.png")

def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    #print (matrix)
    return int((matrix[size_x - 1, size_y - 1]))

if __name__=='__main__':
    path_to_here = os.path.abspath(os.path.dirname(__file__))
    path_to_voc = os.path.join(path_to_here, "../CodRep4/vocab.txt")
    path_to_src = os.path.join(path_to_here, "../Golden/src-test.txt")
    path_to_tgt = os.path.join(path_to_here, "../Golden/tgt-test.txt")
    #path_to_tgt = os.path.join(path_to_here, "../tgt-test_unks.txt")
    path_to_train = os.path.join(path_to_here, "../Golden/src-train.txt")
    parser = argparse.ArgumentParser()
    parser.add_argument("-unk", action='store_true', default=False)
    parser.add_argument("-oov", action='store_true', default=False)
    parser.add_argument("-rewrite", action='store_true', default=False)
    parser.add_argument("-type", action='store_true', default=False)
    parser.add_argument("-buglen", action='store_true', default=False)
    parser.add_argument("-difflen", action='store_true', default=False)
    parser.add_argument("-easy_acc", action='store_true', default=False)
    parser.add_argument("-easy_graphs", action='store_true', default=False)
    args = parser.parse_args()
    if args.oov:
        oov(path_to_src, path_to_tgt, path_to_train)
    elif args.unk:
        unk(path_to_src, path_to_train)
    elif args.rewrite:
        rewrite_tgt(path_to_here, path_to_src, path_to_tgt, path_to_voc)
    elif args.type:
        type_usage(path_to_src, path_to_voc)
    elif args.buglen:
        get_buggy_line_length(path_to_src)
    elif args.difflen:
        get_line_fix_diff(path_to_src, path_to_tgt)
    elif args.easy_acc:
        get_easy_accuracy(path_to_here, path_to_src, path_to_tgt, path_to_voc, 30, 15)
    elif args.easy_graphs:
        easier_data_graphs(path_to_here, path_to_src, path_to_tgt, path_to_voc)
    else:
        print("Please use either one of these tags: -unk -oov -rewrite")