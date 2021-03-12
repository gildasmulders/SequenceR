import sys
from gensim.models import Word2Vec
import torch
import argparse


def main(args):
    data = open(args.src, 'r').readlines()
    data = [line.split() for line in data]
    model = Word2Vec(data, min_count=1, size=256, workers=3, window=5, sg=1)
    ## Getting words from previously built vocabulary
    word_list = []
    if args.from_dict:
        pre_dict = open(args.from_dict, 'r')
        word_list = [ word.strip() for word in pre_dict.readlines() if word.strip() not in ['<unk>', '<blank>', '<s>', '</s>'] ]
    else:
        word_list = model.wv.index2word[:1000]
    ## Saving dictionary
    if args.save_dict:
        w2v_dict = open(args.save_dict, 'w')
        for idx, word in enumerate(word_list):
            w2v_dict.write(f"{word} {idx}\n")
        w2v_dict.close()
    ## Saving embedding (torch style)
    if args.save_embed:
        w2v_emb = torch.FloatTensor([model.wv[word] for word in word_list])
        torch.save(w2v_emb, args.save_embed)
    sys.exit(0)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--save_dict", default=False)
    parser.add_argument("--save_embed", default=False)
    parser.add_argument("--from_dict", default=False)
    args = parser.parse_args()
    main(args)