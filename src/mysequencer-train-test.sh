#! /bin/bash

echo "mysequencer-train-test.sh start"

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"

HELP_MESSAGE=$'Usage: ./mysequencer-train-test --feature=[indent|tag|both] --steps=[int] --keep_model=[True|False]
feature: Which feature to use to enhance the data
steps: nb of training steps to do (usual are 10000 or 20000)
keep_model: boolean, whether we should keep the built model or not'
for i in "$@"
do
case $i in
    --feature=*)
    FEATURE="${i#*=}"
    shift # past argument=value
    ;;
    --steps=*)
    STEPS="${i#*=}"
    shift # past argument=value
    ;;
    --keep_model=*)
    KEEP_MODEL="${i#*=}"
    shift # past argument=value
    ;;
    *)
          # unknown option
    ;;
esac
done

if [ ! -f $OpenNMT_py/preprocess.py ]; then
  echo "OpenNMT_py environment variable should be set"
  echo "$HELP_MESSAGE"
  exit 1
fi

if [ -z "$FEATURE" ]; then
  echo "FEATURE unset!"
  echo "$HELP_MESSAGE"
  exit 1
fi

if [ -z "$STEPS" ]; then
  STEPS=10000
fi

if [ -z "$KEEP_MODEL" ]; then
  KEEP_MODEL="True"
fi

echo "Input parameter:"
echo "FEATURE = ${FEATURE}"
echo "STEPS = ${STEPS}"
echo "KEEP_MODEL = ${KEEP_MODEL}"
echo

echo "Creating temporary working folder"
mkdir -p $CURRENT_DIR/tmp
echo

echo "Creating data with features..."
echo "for src-train"
python3 $CURRENT_DIR/Buggy_Context_Abstraction/add_tree_feature.py $ROOT_DIR/results/Golden/src-train.txt $CURRENT_DIR/tmp/src-train-${FEATURE}.txt $FEATURE
retval=$?
if [ $retval -ne 0 ]; then
  echo "Creation of featured src-train failed"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "for src-val"
python3 $CURRENT_DIR/Buggy_Context_Abstraction/add_tree_feature.py $ROOT_DIR/results/Golden/src-val.txt $CURRENT_DIR/tmp/src-val-${FEATURE}.txt $FEATURE
retval=$?
if [ $retval -ne 0 ]; then
  echo "Creation of featured src-val failed"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "for src-test"
python3 $CURRENT_DIR/Buggy_Context_Abstraction/add_tree_feature.py $ROOT_DIR/results/Golden/src-test.txt $CURRENT_DIR/tmp/src-test-${FEATURE}.txt $FEATURE
retval=$?
if [ $retval -ne 0 ]; then
  echo "Creation of featured src-test failed"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "Starting data preprocessing"
cd $OpenNMT_py
python3 preprocess.py -train_src $CURRENT_DIR/tmp/src-train-${FEATURE}.txt -train_tgt $ROOT_DIR/results/Golden/tgt-train.txt -valid_src $CURRENT_DIR/tmp/src-val-${FEATURE}.txt -valid_tgt $ROOT_DIR/results/Golden/tgt-val.txt -src_seq_length 1010 -tgt_seq_length 100 -src_vocab_size 1000 -tgt_vocab_size 1000 -dynamic_dict -share_vocab -save_data $CURRENT_DIR/tmp/final-${FEATURE} 2>&1 > $CURRENT_DIR/tmp/preprocess.out
echo 

echo "Starting training.."
cd $OpenNMT_py
python3 train.py -data $CURRENT_DIR/tmp/final-${FEATURE} -encoder_type brnn -enc_layers 2 -decoder_type rnn -dec_layers 2 -rnn_size 256 -global_attention general -batch_size 32 -word_vec_size 256 -bridge -copy_attn -reuse_copy_attn -train_steps ${STEPS} -gpu_ranks 0 -save_model $ROOT_DIR/model/final-model-${FEATURE} > $CURRENT_DIR/tmp/train.final.out
echo "train.sh complete" >> $CURRENT_DIR/tmp/train.out

echo "Translating test set"
cd $OpenNMT_py
python3 translate.py -model $ROOT_DIR/model/final-model-${FEATURE}_step_${STEPS}.pt -src $CURRENT_DIR/tmp/src-test-${FEATURE}.txt -beam_size 50 -n_best 50 -output $CURRENT_DIR/tmp/pred-test_beam50_${FEATURE}.txt -dynamic_dict 2>&1 > $CURRENT_DIR/tmp/translate50.out
echo

echo "Evaluating obtained performances"
python3 $ROOT_DIR/results/eval.py $CURRENT_DIR/tmp/pred-test_beam50_${FEATURE}.txt $ROOT_DIR/results/Golden/tgt-test.txt > $ROOT_DIR/results/mysequencer/perf_${FEATURE}_${STEPS}.txt


echo "Removing model if needed"
if [ "$KEEP_MODEL" == "False" ]; then
  rm $ROOT_DIR/model/final-model-${FEATURE}_step_${STEPS}.pt
fi
echo

echo "Cleaning tmp folder"
rm -rf $CURRENT_DIR/tmp
echo

echo "mysequencer-train-test.sh done"
echo
exit 0
