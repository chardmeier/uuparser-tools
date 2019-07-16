#!/bin/sh

# loading correct python3 enviroment with eflomal installed
source ~/.bashrc
source activate py37

# arg1: input directory (tokenized inputs)
IN_DIR=$1
OUT_DIR=$2
# arg2: output directory
MERGE_DIR="merged"

python3 ~/pronoun_project/scripts/alignment/merge.py $IN_DIR $MERGE_DIR
python3 ~/pronoun_project/scripts/alignment/submit_alignment_jobs.py $MERGE_DIR $OUT_DIR
