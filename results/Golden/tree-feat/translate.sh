#! /bin/bash

cd $OpenNMT_py
python3 translate.py -model /SequenceR/model/final-model-tagged_step_20000.pt -src $data_path/tree-feat/src-test-tagged.txt -beam_size 50 -n_best 50 -output $data_path/tree-feat/pred-test_beam50_tagged.txt -dynamic_dict 2>&1 > $data_path/translate50.out
