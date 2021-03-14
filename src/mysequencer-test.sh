#! /bin/bash

echo "mysequencer-test.sh start"

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"

HELP_MESSAGE=$'Usage: ./mysequencer-test [--model=[path/to/model]]
model: absolute path to model '

array_feat=()
for i in "$@"
do
case $i in
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

if [ ! -f $OpenNMT_py/preprocess.py ]; then
  echo "OpenNMT_py environment variable should be set"
  echo "$HELP_MESSAGE"
  exit 1
fi

if [ -z "$MODEL" ]; then
  echo "MODEL Unset !"
  exit 1
fi

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


TMP_DIRECTORY="$CURRENT_DIR/tmp"
if [ -d ${TMP_DIRECTORY} ]; then
  n=1
  while [ -d "$CURRENT_DIR/tmp_${n}" ]; do
    n=$(( n+1 ))
  done
  TMP_DIRECTORY="$CURRENT_DIR/tmp_${n}"
fi

echo "Creating temporary working folder"
mkdir -p ${TMP_DIRECTORY}
echo

echo "Creating data with features for src-test"
python3 $CURRENT_DIR/features_utils/add_tree_feature.py $ROOT_DIR/results/Golden/src-test.txt ${TMP_DIRECTORY}/src-test${NAME_FEAT}.txt ${array_feat[@]}
retval=$?
if [ $retval -ne 0 ]; then
  echo "Creation of featured src-test failed"
  rm -rf ${TMP_DIRECTORY}
  exit 1
fi
echo

echo "Translating test set"
cd $OpenNMT_py
python3 translate.py -model ${MODEL} -src ${TMP_DIRECTORY}/src-test${NAME_FEAT}.txt -beam_size 50 -n_best 50 -output ${TMP_DIRECTORY}/pred-test_beam50${NAME_FEAT}.txt -dynamic_dict 2>&1 > ${TMP_DIRECTORY}/translate50.out
echo

PERF_NAME=${MODEL#*step_}
echo "Evaluating obtained performances"
python3 $ROOT_DIR/results/eval.py ${TMP_DIRECTORY}/pred-test_beam50${NAME_FEAT}.txt $ROOT_DIR/results/Golden/tgt-test.txt >> $ROOT_DIR/results/mysequencer/perf${NAME_FEAT}_${PERF_NAME%.pt}.txt
echo

echo "Cleaning tmp folder"
rm -rf ${TMP_DIRECTORY}
echo

echo "RESULT"
cat $ROOT_DIR/results/mysequencer/perf${NAME_FEAT}_${PERF_NAME%.pt}.txt
echo

echo "mysequencer-test done"




