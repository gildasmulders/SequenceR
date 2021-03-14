#/usr/bin/env bash
complete -W "--indent --tag --number --kmost --steps= --rm --checkpoint= --word2vec --fix_embedding" mysequencer-train-test.sh

complete -W "--model=" mysequencer-test.sh

complete -W "--buggy_file= --buggy_line= --beam_size= --output= --model=" mysequencer-predict.sh
