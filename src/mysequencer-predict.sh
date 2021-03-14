#! /bin/bash

echo "mysequencer-predict.sh start"

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"

HELP_MESSAGE=$'Usage: ./mysequencer-predict.sh [--buggy_file=[abs path]] [--buggy_line=[int]] [--beam_size=[int]] [--output=[abs path]] [--model=[abs/path/to/model]]
buggy_file: Absolute path to the buggy file
buggy_line: Line number of buggy line
beam_size: Beam size used in seq2seq model
output: Absolute path for output
model: Absolute path to the model that should be used'
for i in "$@"
do
case $i in
    --buggy_file=*)
    BUGGY_FILE_PATH="${i#*=}"
    shift # past argument=value
    ;;
    --buggy_line=*)
    BUGGY_LINE="${i#*=}"
    shift # past argument=value
    ;;
    --beam_size=*)
    BEAM_SIZE="${i#*=}"
    shift # past argument=value
    ;;
    --output=*)
    OUTPUT="${i#*=}"
    shift # past argument=value
    ;;
    --model=*)
    MODEL="${i#*=}"
    shift # past argument=value
    ;;
    --help|-help|-h)
    echo "$HELP_MESSAGE"
    exit 0
    ;;
    *)
          # unknown option
    ;;
esac
done

if [ -z "$BUGGY_FILE_PATH" ]; then
  BUGGY_FILE_PATH="$ROOT_DIR/test.java"
elif [[ "$BUGGY_FILE_PATH" != /* ]]; then
  echo "BUGGY_FILE_PATH must be absolute path !"
  exit 1
fi

if [ -z "$BUGGY_LINE" ]; then
  BUGGY_LINE=17
fi

if [ -z "$BEAM_SIZE" ]; then
  BEAM_SIZE=20
fi

if [ -z "$OUTPUT" ]; then
  OUTPUT="$ROOT_DIR/test-results"
elif [[ "$OUTPUT" != /* ]]; then
  echo "OUTPUT must be absolute path !"
  exit 1
fi

if [ -z "$MODEL" ]; then
  MODEL="$ROOT_DIR/model/model.pt"
fi

echo "Input parameter:"
echo "BUGGY_FILE_PATH = ${BUGGY_FILE_PATH}"
echo "BUGGY_LINE = ${BUGGY_LINE}"
echo "BEAM_SIZE = ${BEAM_SIZE}"
echo "OUTPUT = ${OUTPUT}"
echo "MODEL = ${MODEL}"
echo

BUGGY_FILE_NAME=${BUGGY_FILE_PATH##*/}
BUGGY_FILE_BASENAME=${BUGGY_FILE_NAME%.*}

# Pre-processing arguments
model_part="${MODEL#*final-model}"
model_part="${model_part%_step*}"
array_feat=(${model_part//-/ })

if [[ "$MODEL" == */model.pt ]]; then
  array_feat=()
fi

SAVE_IFS="$IFS"
IFS="-"
NAME_FEAT="${array_feat[*]}"
IFS="$SAVE_IFS"

if [ ${#array_feat[@]} -gt 0 ]; then
  NAME_FEAT="-${NAME_FEAT}"
fi

echo "Creating temporary working folder"
mkdir -p $CURRENT_DIR/tmp
echo

echo "Abstracting the source file"
java -jar $CURRENT_DIR/lib/abstraction-1.0-SNAPSHOT-jar-with-dependencies.jar $BUGGY_FILE_PATH $BUGGY_LINE $CURRENT_DIR/tmp
retval=$?
if [ $retval -ne 0 ]; then
  echo "Cannot generate abstraction for the buggy file"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "Tokenizing the abstraction"
python3 $CURRENT_DIR/Buggy_Context_Abstraction/tokenize.py $CURRENT_DIR/tmp/${BUGGY_FILE_BASENAME}_abstract.java $CURRENT_DIR/tmp/${BUGGY_FILE_BASENAME}_abstract_tokenized.txt
retval=$?
if [ $retval -ne 0 ]; then
  echo "Tokenization failed"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "Truncate the abstraction to 1000 tokens"
perl $CURRENT_DIR/Buggy_Context_Abstraction/trimCon.pl $CURRENT_DIR/tmp/${BUGGY_FILE_BASENAME}_abstract_tokenized.txt $CURRENT_DIR/tmp/${BUGGY_FILE_BASENAME}_abstract_tokenized_truncated.txt 1000
retval=$?
if [ $retval -ne 0 ]; then
  echo "Truncation failed"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "Adding features to the truncated abstraction"
python3 $CURRENT_DIR/features_utils/add_tree_feature.py $CURRENT_DIR/tmp/${BUGGY_FILE_BASENAME}_abstract_tokenized_truncated.txt $CURRENT_DIR/tmp/${BUGGY_FILE_BASENAME}_abstract_tokenized_truncated${NAME_FEAT}.txt ${array_feat[@]}
retval=$?
if [ $retval -ne 0 ]; then
  echo "Addition of features failed"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "Generating predictions"
python3 $CURRENT_DIR/lib/OpenNMT-py/translate.py -model $MODEL -src $CURRENT_DIR/tmp/${BUGGY_FILE_BASENAME}_abstract_tokenized_truncated${NAME_FEAT}.txt -output $CURRENT_DIR/tmp/predictions.txt -beam_size $BEAM_SIZE -n_best $BEAM_SIZE &>/dev/null


echo

echo "Post process predictions"
python3 $CURRENT_DIR/Patch_Preparation/postPrcoessPredictions.py $CURRENT_DIR/tmp/predictions.txt $CURRENT_DIR/tmp
retval=$?
if [ $retval -ne 0 ]; then
  echo "Post process generates none valid predictions"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "Creating output directory ${OUTPUT}"
mkdir -p $OUTPUT
echo

echo "Generating patches"
python3 $CURRENT_DIR/Patch_Preparation/generatePatches.py $BUGGY_FILE_PATH $BUGGY_LINE $CURRENT_DIR/tmp/predictions_JavaSource.txt $OUTPUT
echo

echo "Generating diffs"
for patch in $OUTPUT/*; do
  diff -u -w $BUGGY_FILE_PATH $patch/$BUGGY_FILE_NAME > $patch/diff
done
echo


echo "Cleaning tmp folder"
rm -rf $CURRENT_DIR/tmp
echo

echo "Found $(ls $OUTPUT | wc -l | awk '{print $1}') patches for $BUGGY_FILE_NAME stored in $OUTPUT"
echo "sequencer-predict.sh done"
echo
cat $OUTPUT/*/*.java
rm -rf $OUTPUT
exit 0
