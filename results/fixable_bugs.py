import argparse
import os
from collections import Counter
import matplotlib.pyplot as plt
import sys
from tqdm import tqdm

def main(args):
    voc = set()
    # with open(args.vocab, 'r') as voc_file:
    #     voc = set([line.strip() for line in voc_file.readlines()])
    src_lines = []    
    with open(args.src, 'r') as src_file:
        src_lines = src_file.readlines()
    src_lines_lower = [line.lower() for line in src_lines]

    path_to_here = os.path.abspath(os.path.dirname(__file__))
    path_to_train = os.path.join(path_to_here, "Golden/src-train.txt")
    full_counter = []
    with open(path_to_train) as train_file:
        all_src = []
        for line in train_file.readlines():
            for word in line.strip().split():
                all_src.append(word.strip())
        full_counter = Counter(all_src)
    tgt_lines = []
    with open(args.tgt, 'r') as tgt_file:    
        tgt_lines = tgt_file.readlines()
    tgt_lines_lower = [line.lower() for line in tgt_lines]
    most_commons = full_counter.most_common()
    #voc_sizes = [1, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000]
    voc_sizes = range(0, 5000, 25)
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

    our_voc_idx = [voc_sizes.index(1000)]
    plt.plot(voc_sizes, [round((float(imp_nb)/float(tot_nb))*100, 2) for imp_nb in imposs_list], 'b', label="Keeping the different cases")    
    plt.plot(voc_sizes[our_voc_idx[0]], [round((float(imposs_list[our_voc_idx[0]])/float(tot_nb))*100, 2)], 'bo')
    plt.plot(voc_sizes, [round((float(imp_nb)/float(tot_nb))*100, 2) for imp_nb in imposs_list_lower], 'r', label="To lower case")
    plt.plot(voc_sizes[our_voc_idx[0]], [round((float(imposs_list_lower[our_voc_idx[0]])/float(tot_nb))*100, 2)], 'ro')
    plt.axvline(1000)
    #xticks_vals = list(range(0, 20000, 2500)) + [1000]
    #plt.xticks(xticks_vals)
    plt.title("Effect of the vocabulary size on the OOV problem")
    plt.xlabel("Vocabulary size [#]")
    plt.ylabel("Unpredictable test samples [% of the full test set]")
    plt.legend()
    plt.savefig("Effect of the vocabulary size on the OOV problem_zoom.png")

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




if __name__=='__main__':
    path_to_here = os.path.abspath(os.path.dirname(__file__))
    path_to_voc = os.path.join(path_to_here, "CodRep4/vocab.txt")
    path_to_src = os.path.join(path_to_here, "Golden/src-test.txt")
    path_to_tgt = os.path.join(path_to_here, "Golden/tgt-test.txt")
    parser = argparse.ArgumentParser()
    parser.add_argument("-vocab", default=path_to_voc)
    parser.add_argument("-src", default=path_to_src)
    parser.add_argument("-tgt", default=path_to_tgt)
    args = parser.parse_args()
    main(args)