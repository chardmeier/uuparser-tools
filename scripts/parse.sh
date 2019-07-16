#!/bin/sh
# $1 - language code
# $2 - path to input file

source ~/.bashrc

python3 /usit/abel/u1/trembczm/pronoun_project/scripts/create_parse_batchfile.py $1 $2
sbatch /usit/abel/u1/trembczm/pronoun_project/batchfiles/parse_batchfile.sh
