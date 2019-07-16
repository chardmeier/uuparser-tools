#!/bin/sh

module purge
module load gcc python3/3.7.0.gnu

source ~/.bashrc
# arg1: treebank language code

echo "create batchfile for $1"
python3 $SCRIPTS/UDPipe/create_ud_train_batch.py $1
sbatch $BATCHFILES/train_UDPipe.sh
