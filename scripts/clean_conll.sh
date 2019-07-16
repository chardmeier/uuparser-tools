#!/bin/sh

module purge
module load gcc python3/3.7.0.gnu

python3 ~/pronoun_project/scripts/clean_conll.py $1
