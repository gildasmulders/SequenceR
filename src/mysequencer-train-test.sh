#! /bin/bash

echo "mysequencer-train-test.sh start"

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"

HELP_MESSAGE=$'Usage: ./mysequencer-train-test [--feature=[indent|tag|both]] [--steps=[int]] [--rm] [--checkpoint=[int]]
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
    --checkpoint=*)
    CHECK_STEPS="${i#*=}"
    shift # past argument=value
    ;;
    --rm)
    KEEP_MODEL="False"
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

NAME_FEAT=''

if [ -n "$FEATURE" ]; then
  NAME_FEAT="-${FEATURE}"
fi

if [ -z "$STEPS" ]; then
  STEPS=10000
fi

if [ -z "$CHECK_STEPS" ]; then
  CHECK_STEPS=${STEPS}
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
python3 $CURRENT_DIR/features_utils/add_tree_feature.py $ROOT_DIR/results/Golden/src-train.txt $CURRENT_DIR/tmp/src-train${NAME_FEAT}.txt $FEATURE
retval=$?
if [ $retval -ne 0 ]; then
  echo "Creation of featured src-train failed"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "for src-val"
python3 $CURRENT_DIR/features_utils/add_tree_feature.py $ROOT_DIR/results/Golden/src-val.txt $CURRENT_DIR/tmp/src-val${NAME_FEAT}.txt $FEATURE
retval=$?
if [ $retval -ne 0 ]; then
  echo "Creation of featured src-val failed"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "for src-test"
python3 $CURRENT_DIR/features_utils/add_tree_feature.py $ROOT_DIR/results/Golden/src-test.txt $CURRENT_DIR/tmp/src-test${NAME_FEAT}.txt $FEATURE
retval=$?
if [ $retval -ne 0 ]; then
  echo "Creation of featured src-test failed"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "Starting data preprocessing"
cd $OpenNMT_py
python3 preprocess.py -train_src $CURRENT_DIR/tmp/src-train${NAME_FEAT}.txt -train_tgt $ROOT_DIR/results/Golden/tgt-train.txt -valid_src $CURRENT_DIR/tmp/src-val${NAME_FEAT}.txt -valid_tgt $ROOT_DIR/results/Golden/tgt-val.txt -src_seq_length 1010 -tgt_seq_length 100 -src_vocab_size 1000 -tgt_vocab_size 1000 -dynamic_dict -share_vocab -save_data $CURRENT_DIR/tmp/final${NAME_FEAT} 2>&1 > $CURRENT_DIR/tmp/preprocess.out
echo 

NUM_FEAT_IDX=""
if [[ "$FEATURE" == "both" ]]; then
  NUM_FEAT_IDX="--numerical_feat_idx '[1]'"
fi

if [[ "$FEATURE" == "indent" ]]; then
  NUM_FEAT_IDX="--numerical_feat_idx '[0]'"
fi

MODEL_FILE_NAME="$ROOT_DIR/model/final-model${NAME_FEAT}"
if [ -f ${MODEL_FILE_NAME}_step_${STEPS}.pt ]; then
  n=1
  while [ -f $ROOT_DIR/model/final-model${NAME_FEAT}-${n}_step_${STEPS}.pt ]; do
    n=$(( n+1 ))
  done
  MODEL_FILE_NAME=$ROOT_DIR/model/final-model${NAME_FEAT}-${n}
fi

echo "Starting training of ${MODEL_FILE_NAME}"
cd $OpenNMT_py
python3 train.py -data $CURRENT_DIR/tmp/final${NAME_FEAT} -encoder_type brnn -enc_layers 2 -decoder_type rnn -dec_layers 2 -rnn_size 256 -global_attention general -batch_size 32 -word_vec_size 256 -bridge -copy_attn -reuse_copy_attn -train_steps ${STEPS} -gpu_ranks 0 -save_checkpoint_steps ${CHECK_STEPS} -save_model $MODEL_FILE_NAME $NUM_FEAT_IDX > $CURRENT_DIR/tmp/train.final.out
echo "train.sh complete" >> $CURRENT_DIR/tmp/train.out

echo "Translating test set"
cd $OpenNMT_py
python3 translate.py -model ${MODEL_FILE_NAME}_step_${STEPS}.pt -src $CURRENT_DIR/tmp/src-test${NAME_FEAT}.txt -beam_size 50 -n_best 50 -output $CURRENT_DIR/tmp/pred-test_beam50${NAME_FEAT}.txt -dynamic_dict 2>&1 > $CURRENT_DIR/tmp/translate50.out
echo

echo "Evaluating obtained performances"
python3 $ROOT_DIR/results/eval.py $CURRENT_DIR/tmp/pred-test_beam50${NAME_FEAT}.txt $ROOT_DIR/results/Golden/tgt-test.txt >> $ROOT_DIR/results/mysequencer/perf${NAME_FEAT}_${STEPS}.txt


if [[ "$KEEP_MODEL" == "False" ]]; then
  echo "Removing model"
  rm ${MODEL_FILE_NAME}_step_${STEPS}.pt
fi
echo

echo "Cleaning tmp folder"
rm -rf $CURRENT_DIR/tmp
echo

echo "RESULT"
echo
cat $ROOT_DIR/results/mysequencer/perf${NAME_FEAT}_${STEPS}.txt
echo

echo "mysequencer-train-test.sh done"
echo
exit 0
