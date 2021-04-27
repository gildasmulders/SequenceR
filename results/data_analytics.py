import argparse
import os
from collections import Counter
import matplotlib.pyplot as plt
import sys
from tqdm import tqdm

### TODO : REWRITE TGT BY REPLACING UNPREDICTABLE WORDS BY <UNK>
def rewrite_tgt(voc_file, src_file, tgt_file):   

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
    return 0

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

if __name__=='__main__':
    path_to_here = os.path.abspath(os.path.dirname(__file__))
    #path_to_voc = os.path.join(path_to_here, "CodRep4/vocab.txt")
    path_to_src = os.path.join(path_to_here, "Golden/src-test.txt")
    path_to_tgt = os.path.join(path_to_here, "Golden/tgt-test.txt")
    path_to_train = os.path.join(path_to_here, "Golden/src-train.txt")
    parser = argparse.ArgumentParser()
    parser.add_argument("-unk", action='store_true', default=False)
    parser.add_argument("-oov", action='store_true', default=False)
    args = parser.parse_args()
    if args.oov:
        oov(path_to_src, path_to_tgt, path_to_train)
    elif args.unk:
        unk(path_to_src, path_to_train)