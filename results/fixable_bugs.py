import argparse

def main(args):    
    voc = set()
    with open(args.vocab, 'r') as voc_file:
        for line in voc_file.readlines():
            voc.add(line.strip())
    src_file = open(args.src, 'r')
    tgt_file = open(args.tgt, 'r')
    src_lines = src_file.readlines()
    tgt_lines = tgt_file.readlines()
    src_file.close()
    tgt_file.close()
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
    print(f"There are {impossible_nb}/{tot_nb} ({round((float(impossible_nb)/float(tot_nb))*100, 2)}%) samples impossible to predict due to OOV tokens")




if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-vocab", required=True)
    parser.add_argument("-src", required=True)
    parser.add_argument("-tgt", required=True)
    args = parser.parse_args()
    main(args)