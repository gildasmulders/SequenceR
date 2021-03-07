#!/usr/bin/env python
import sys
import torch


def main(argv):
    vocab_file = argv[0]
    feat_num = int(argv[1])    
    vocab = torch.load(vocab_file)[feat_num+1][1].itos
    trick_dict = {'<blank>':2, '<unk>':1}
    try:
        embedding_matrix = torch.LongTensor([[0, float(x)] if (x!='<blank>' and x!='<unk>') else [trick_dict[x], 0] for x in vocab]) 
        torch.save(embedding_matrix, argv[2])
    except ValueError:
        print("You should only use this script for embedding numerical features")
    


if __name__=="__main__":
    main(sys.argv[1:])