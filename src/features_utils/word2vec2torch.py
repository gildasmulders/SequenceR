import sys
from gensim.models import Word2Vec
import torch
import argparse
import numpy as np


def prep_line(line, word_set):
    out = ['<s>']
    for i, word in enumerate(line):
        if word in word_set:
            out += [word]
        else:
            out += ['<unk>']
        if word in ['{', '}', ';']:
            out += ['</s>']
            if i < (len(line) - 1):
                out += ['<s>']
        if out[-1] != '</s>':
            out += ['</s>']
    return out

def main(args):
        
    data = open(args.src, 'r').readlines()
    data = [line.split() for line in data]

    ## Getting words from previously built vocabulary
    word_list = []
    if args.from_dict:
        pre_dict = open(args.from_dict, 'r')
        word_list = [ word.strip() for word in pre_dict.readlines() ]
        word_set = set(word_list) - {'<unk>', '<blank>', '<s>', '</s>'}
        data = [ prep_line(data_line, word_set) for data_line in data ]

    model = Word2Vec(data, min_count=1, size=256, workers=3, window=5, iter=15, sg=1)    

    if not args.from_dict:
        word_list = model.wv.index2word[:1000]

    ## Saving dictionary
    if args.save_dict:
        w2v_dict = open(args.save_dict, 'w')
        for idx, word in enumerate(word_list[4:]):
            w2v_dict.write(f"{word} {idx}\n")
        w2v_dict.close()

    ## Saving embeddings (torch style)
    if args.save_embed:
        w2v_emb = torch.FloatTensor([model.wv[word] if word != '<blank>' else np.zeros(256, dtype='float32') for word in word_list])
        torch.save(w2v_emb, args.save_embed)
    sys.exit(0)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--save_dict", default=False)
    parser.add_argument("--save_embed", default=False)
    parser.add_argument("--from_dict", default=False)
    parser.add_argument("--train_specials", default=True)
    args = parser.parse_args()
    main(args)