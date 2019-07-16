#!/bin/sh
# Creates a batchfile for tokenizing and tagging for the given file

# Load Python
module purge
module load gcc python3/3.7.0.gnu

source ~/.bashrc
# arg1: path to file to be tokenized/tagged
# input file is expected to end with the respective language for example: abc.xy.en

# Call Python script / create batchfile
echo "(Tokenizing/Tagging) - create batchfile for $1"
python3 $SCRIPTS/UDPipe/tokenize_create_batchfile.py $1

# Submit batch to queue
sbatch $BATCHFILES/tokenize.sh
