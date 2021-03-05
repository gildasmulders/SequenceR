#! /bin/bash

echo 

./sequencer-predict.sh --buggy_file=/SequenceR/test.java --buggy_line=17 --beam_size=20 --output=/SequenceR/test-results --tree_feat="True"

exit 0
