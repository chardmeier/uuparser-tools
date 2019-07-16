import sys, os
# train UUParser

code = sys.argv[1]

DATA   = os.environ['DATA']
MODELS = os.environ['MODELS']
PROJECT = os.environ['PROJECT']
BATCHFILES = os.environ['BATCHFILES']
LOGS = os.environ['LOGS']

logpath = f"{LOGS}/parser"
if not os.path.isdir(logpath):
    print('Create directory:', logpath)
    os.mkdir(logpath)

parser_models = f"{MODELS}/UUParser"
if not os.path.isdir(parser_models):
    print('Create directory:', parser_models)
    os.mkdir(parser_models)

batch_string = f"""#!/bin/sh

#SBATCH -t 96:00:00
#SBATCH -n 1
#SBATCH -J "{code}_tp"
#SBATCH --mem-per-cpu=60GB
#SBATCH --account=nn9447k
#SBATCH --output={logpath}/train_{code}-%j.out

source ~/.bashrc
#source activate dynet

module purge
module load gcc

PARSER="$PROJECT/uuparser/barchybrid/"
TBS="{DATA}/ud-treebanks-v2.4/"
OUT="{parser_models}"

cd $PARSER
srun python src/parser.py \
     --graph-based \
     --outdir $OUT \
     --datadir $TBS \
     --include {code} \
     --epochs 30 \
     --dynet-seed 123456788 \
     --dynet-mem 30000 \
     --word-emb-size 300"""

batch_path = f'{BATCHFILES}/train_parser.sh'
with open(batch_path, 'w') as f:
    f.write(batch_string)
    
os.system(f'sbatch {batch_path}')
