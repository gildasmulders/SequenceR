#! /bin/bash

echo "mysequencer-test.sh start"

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"

HELP_MESSAGE=$'Usage: ./mysequencer-train-test --feature=[indent|tag|both] --model=[path/to/model]
feature: Which feature to use to enhance the data
model: absolute path to model '
for i in "$@"
do
case $i in
    --feature=*)
    FEATURE="${i#*=}"
    shift # past argument=value
    ;;
    --model=*)
    MODEL="${i#*=}"
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

if [ -z "$MODEL" ]; then
  echo "MODEL Unset !"
  exit 1
fi

if [ -z "$KEEP_PRED" ]; then
  KEEP_PRED="True"
fi

NAME_FEAT=''

if [ -n "$FEATURE" ]; then
  NAME_FEAT="-${FEATURE}"
fi

echo "Creating temporary working folder"
mkdir -p $CURRENT_DIR/tmp
echo

echo "Creating data with features for src-test"
python3 $CURRENT_DIR/features_utils/add_tree_feature.py $ROOT_DIR/results/Golden/src-test.txt $CURRENT_DIR/tmp/src-test${NAME_FEAT}.txt $FEATURE
retval=$?
if [ $retval -ne 0 ]; then
  echo "Creation of featured src-test failed"
  rm -rf $CURRENT_DIR/tmp
  exit 1
fi
echo

echo "Translating test set"
cd $OpenNMT_py
python3 translate.py -model ${MODEL} -src $CURRENT_DIR/tmp/src-test${NAME_FEAT}.txt -beam_size 50 -n_best 50 -output $CURRENT_DIR/tmp/pred-test_beam50${NAME_FEAT}.txt -dynamic_dict 2>&1 > $CURRENT_DIR/tmp/translate50.out
echo

echo "Evaluating obtained performances"
python3 $ROOT_DIR/results/eval.py $CURRENT_DIR/tmp/pred-test_beam50${NAME_FEAT}.txt $ROOT_DIR/results/Golden/tgt-test.txt
echo

echo "Cleaning tmp folder"
rm -rf $CURRENT_DIR/tmp
echo




