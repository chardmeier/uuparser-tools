#!/bin/sh

#SBATCH -t 48:00:00
#SBATCH -n 1
#SBATCH --mem-per-cpu=60GB
#SBATCH --account=nn9447k
#SBATCH --output=slurm-%J.out
source "/usit/abel/u1/trembczm/miniconda2/bin/activate"
module purge
module load gcc

PARSER="uuparser/barchybrid/"
TBS="/usit/abel/u1/trembczm/pronoun_project/ud-treebanks-v2.4/"
OUT="/usit/abel/u1/trembczm/pronoun_project/parser_out/"

cd $PARSER
srun python src/parser.py \
     --graph-based \
     --outdir $OUT \
     --datadir $TBS \
     --include $1 \
     --epochs 30 \
     --dynet-seed 123456788 \
     --dynet-mem 30000 \
     --word-emb-size 300
