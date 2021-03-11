#! /bin/bash

echo "mysequencer-train-test.sh start"

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"

HELP_MESSAGE=$'Usage: ./mysequencer-train-test [--indent] [--tag] [--number] [--kmost] [--steps=[int]] [--rm] [--checkpoint=[int]]
indent: annotate data with indentation count
tag: annotate data with Keyword/Value/Delimiter/SpecialSymbol/Identifier/Operator tag
number: number each word of each line of code starting with 0 at each new line
kmost: tag each word with its rank of frequency 
steps: nb of training steps to do (usual are 10000 or 20000)
keep_model: boolean, whether we should keep the built model or not'

array_feat=()
for i in "$@"
do
case $i in
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
    --indent)
    array_feat+=(indent)
    shift # past argument=value
    ;;
    --tag)
    array_feat+=(tag)
    shift # past argument=value
    ;;
    --number)
    array_feat+=(number)
    shift # past argument=value
    ;;
    --kmost)
    array_feat+=(kmost)
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

SAVE_IFS="$IFS"
IFS="-"
NAME_FEAT="${array_feat[*]}"
IFS="$SAVE_IFS"

if [ ${#array_feat[@]} -gt 0 ]; then
  NAME_FEAT="-${NAME_FEAT}"
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
echo "FEATURES = ${array_feat[@]}"
echo "STEPS = ${STEPS}"
echo "KEEP_MODEL = ${KEEP_MODEL}"
echo

TMP_DIRECTORY="$CURRENT_DIR/tmp"
if [ -d $CURRENT_DIR/tmp ]; then
  n=1
  while [ -d "$CURRENT_DIR/tmp_${n}" ]; do
    n=$(( n+1 ))
  done
  TMP_DIRECTORY="$CURRENT_DIR/tmp_${n}"
fi

echo "Creating temporary working folder"
mkdir -p ${TMP_DIRECTORY}
echo

echo "Creating data with features..."
echo "for src-train"
num_feat=`python3 $CURRENT_DIR/features_utils/add_tree_feature.py $ROOT_DIR/results/Golden/src-train.txt ${TMP_DIRECTORY}/src-train${NAME_FEAT}.txt ${array_feat[@]}`
retval=$?
if [ $retval -ne 0 ]; then
  echo "Creation of featured src-train failed"
  rm -rf ${TMP_DIRECTORY}
  exit 1
fi
echo

echo "for src-val"
num_feat=`python3 $CURRENT_DIR/features_utils/add_tree_feature.py $ROOT_DIR/results/Golden/src-val.txt ${TMP_DIRECTORY}/src-val${NAME_FEAT}.txt ${array_feat[@]}`
retval=$?
if [ $retval -ne 0 ]; then
  echo "Creation of featured src-val failed"
  rm -rf ${TMP_DIRECTORY}
  exit 1
fi
echo

echo "for src-test"
num_feat=`python3 $CURRENT_DIR/features_utils/add_tree_feature.py $ROOT_DIR/results/Golden/src-test.txt ${TMP_DIRECTORY}/src-test${NAME_FEAT}.txt ${array_feat[@]}`
retval=$?
if [ $retval -ne 0 ]; then
  echo "Creation of featured src-test failed"
  rm -rf ${TMP_DIRECTORY}
  exit 1
fi
echo

arr_num_feats=(${num_feat//-/ })
NUM_FEAT_NAMES_VOCAB="${arr_num_feats[0]}"
NUM_FEAT_NAMES_VOCAB=`echo "$NUM_FEAT_NAMES_VOCAB" | sed "s/'//g"`


echo "Starting data preprocessing"
cd $OpenNMT_py
python3 preprocess.py -train_src ${TMP_DIRECTORY}/src-train${NAME_FEAT}.txt -train_tgt $ROOT_DIR/results/Golden/tgt-train.txt -valid_src ${TMP_DIRECTORY}/src-val${NAME_FEAT}.txt -valid_tgt $ROOT_DIR/results/Golden/tgt-val.txt -src_seq_length 1010 -tgt_seq_length 100 -src_vocab_size 1000 -tgt_vocab_size 1000 -dynamic_dict -share_vocab --numerical_feat_names "$NUM_FEAT_NAMES_VOCAB" -save_data ${TMP_DIRECTORY}/final${NAME_FEAT} 2>&1 > ${TMP_DIRECTORY}/preprocess.out
echo 

NUM_FEAT_NAMES_EMBED="${arr_num_feats[1]}"
NUM_FEAT_NAMES_EMBED=`echo "$NUM_FEAT_NAMES_EMBED" | sed "s/'//g"`

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
python3 train.py -data ${TMP_DIRECTORY}/final${NAME_FEAT} -encoder_type brnn -enc_layers 2 -decoder_type rnn -dec_layers 2 -rnn_size 256 -global_attention general -batch_size 32 -word_vec_size 256 -bridge -copy_attn -reuse_copy_attn -train_steps ${STEPS} -gpu_ranks 0 -save_checkpoint_steps ${CHECK_STEPS} -save_model $MODEL_FILE_NAME --numerical_feat_names "$NUM_FEAT_NAMES_EMBED" > ${TMP_DIRECTORY}/train.final.out
echo "train.sh complete" >> ${TMP_DIRECTORY}/train.out

echo "Translating test set"
cd $OpenNMT_py
python3 translate.py -model ${MODEL_FILE_NAME}_step_${STEPS}.pt -src ${TMP_DIRECTORY}/src-test${NAME_FEAT}.txt -beam_size 50 -n_best 50 -output ${TMP_DIRECTORY}/pred-test_beam50${NAME_FEAT}.txt -dynamic_dict 2>&1 > ${TMP_DIRECTORY}/translate50.out
echo

echo "Evaluating obtained performances"
python3 $ROOT_DIR/results/eval.py ${TMP_DIRECTORY}/pred-test_beam50${NAME_FEAT}.txt $ROOT_DIR/results/Golden/tgt-test.txt >> $ROOT_DIR/results/mysequencer/perf${NAME_FEAT}_${STEPS}.txt


if [[ "$KEEP_MODEL" == "False" ]]; then
  echo "Removing model"
  rm ${MODEL_FILE_NAME}_step_${STEPS}.pt
fi
echo

echo "Cleaning tmp folder"
rm -rf ${TMP_DIRECTORY}
echo

echo "RESULT"
echo
cat $ROOT_DIR/results/mysequencer/perf${NAME_FEAT}_${STEPS}.txt
echo

echo "mysequencer-train-test.sh done"
echo
exit 0
