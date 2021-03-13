#! /bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(dirname "$CURRENT_DIR")"

echo 

./sequencer-predict.sh --buggy_file="$ROOT_DIR/test.java" --buggy_line=17 --beam_size=20 --output="$ROOT_DIR/test-results"

exit 0
