import os, sys, json

code = sys.argv[1]

DATA   = os.environ['DATA']
MODELS = os.environ['MODELS']
PROJECT = os.environ['PROJECT']
BATCHFILES = os.environ['BATCHFILES']
LOGS = os.environ['LOGS']

data_dir  = f"{DATA}/ud-treebanks-v2.4"
save_dir  = f"{MODELS}/ud_custom_models"

if not os.path.isdir(save_dir):
    print('Create directory:', save_dir)
    os.mkdir(save_dir)

with open(f'{PROJECT}/ud2.4_iso.json') as f:
    d = json.loads(f.read())
reversed_d = {v:k for k,v in d.items()}
lang_dir = reversed_d[code]

logpath = f"{LOGS}/UDPipe"
if not os.path.isdir(logpath):
    print('Create directory:', logpath)
    os.mkdir(logpath)

batch_string = f"""#!/bin/sh

#SBATCH -t 96:00:00
#SBATCH -n 1
#SBATCH -J "{code}_tr_udpipe"
#SBATCH --mem-per-cpu=16GB
#SBATCH --account=nn9447k
#SBATCH --output={logpath}/train_{code}-%j.out

source ~/.bashrc

module purge
module load gcc

srun udpipe --train \\
        --tagger \\
        --tokenizer {save_dir}/{code}.model {data_dir}/{lang_dir}/{code}-ud-train.conllu"""


batch_path = f'{BATCHFILES}/train_UDPipe.sh'
with open(batch_path, 'w') as f:
    f.write(batch_string)

    
os.system(f'sbatch {batch_path}')
