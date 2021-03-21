#! /bin/bash

echo "mysequencer-train-test.sh start"

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"

export OpenNMT_py=$CURRENT_DIR/lib/OpenNMT-py
export data_path=$ROOT_DIR/results/Golden

HELP_MESSAGE=$'Usage: ./mysequencer-train-test [--indent] [--tag] [--number] [--kmost] [--line_index] [--distbug] [--steps=[int]] [--rm] [--checkpoint=[int]] [--word2vec] [--fix_embedding]
indent: annotate data with indentation count
tag: annotate data with Keyword/Value/Delimiter/SpecialSymbol/Identifier/Operator tags
number: number each word of each line of code starting with 0 at each new line
kmost: tag each word with its rank of frequency 
word2vec: use word2vec to create embeddings
fix_embedding: if specified, the embeddings are frozen during training
steps: nb of training steps to do (usual are 10000 or 20000)
checkpoint: nb of training steps after which we should save the model
rm: if specified, the created model is removed at the end'

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
    --line_index)
    array_feat+=(line_index)
    shift # past argument=value
    ;;
    --distbug)
    array_feat+=(distbug)
    shift # past argument=value
    ;;
    --word2vec)
    WORD2VEC="True"
    shift # past argument=value
    ;;
    --fix_embedding)
    FIX_EMBED="--fix_word_vecs_enc"
    shift # past argument=value
    ;;
    --help|-help|-h)
    echo "$HELP_MESSAGE"
    exit 0
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

if [[ "$WORD2VEC" == "True" ]]; then
  NAME_FEAT="${NAME_FEAT}-word2vec"
  echo "Starting word2vec training"
  python3 $CURRENT_DIR/features_utils/word2vec2torch.py --src $ROOT_DIR/results/Golden/src-train.txt --save_dict ${TMP_DIRECTORY}/src-train.dict --save_embed ${TMP_DIRECTORY}/word2vec_torch_embed.t7 --from_dict $ROOT_DIR/results/CodRep4/vocab.txt 
  retval=$?
  if [ $retval -ne 0 ]; then
    echo "Creation of word2vec embeddings failed"
    rm -rf ${TMP_DIRECTORY}
    exit 1
  fi
  WORD2VEC_vocab="--src_vocab ${TMP_DIRECTORY}/src-train.dict"
  WORD2VEC_embed="--pre_word_vecs_enc ${TMP_DIRECTORY}/word2vec_torch_embed.t7"
  echo "done"
  echo
fi


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

NUM_FEAT_NAMES_VOCAB="$num_feat"
NUM_FEAT_NAMES_VOCAB=`echo "$NUM_FEAT_NAMES_VOCAB" | sed "s/'//g"`

echo "Starting data preprocessing"
cd $OpenNMT_py
python3 preprocess.py -train_src ${TMP_DIRECTORY}/src-train${NAME_FEAT}.txt -train_tgt $ROOT_DIR/results/Golden/tgt-train.txt -valid_src ${TMP_DIRECTORY}/src-val${NAME_FEAT}.txt -valid_tgt $ROOT_DIR/results/Golden/tgt-val.txt -src_seq_length 1010 -tgt_seq_length 100 -src_vocab_size 1000 -tgt_vocab_size 1000 -dynamic_dict -share_vocab $WORD2VEC_vocab --numerical_feat_names "${NUM_FEAT_NAMES_VOCAB[@]}" -save_data ${TMP_DIRECTORY}/final${NAME_FEAT} 2>&1 > ${TMP_DIRECTORY}/preprocess.out
echo 

NUM_FEAT_NAMES_EMBED="$num_feat"
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
python3 train.py -data ${TMP_DIRECTORY}/final${NAME_FEAT} -encoder_type brnn -enc_layers 2 -decoder_type rnn -dec_layers 2 -rnn_size 256 -global_attention general -batch_size 32 -word_vec_size 256 -bridge -copy_attn -reuse_copy_attn -train_steps ${STEPS} -gpu_ranks 0 -save_checkpoint_steps ${CHECK_STEPS} -save_model $MODEL_FILE_NAME $FIX_EMBED $WORD2VEC_embed --numerical_feat_names "${NUM_FEAT_NAMES_EMBED[@]}" > ${TMP_DIRECTORY}/train.final.out
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
