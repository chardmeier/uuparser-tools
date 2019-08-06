import sys, os, re, ntpath
# arg1: target conll file to be parsed
input_path = os.path.abspath(sys.argv[1])
input_file = ntpath.basename(input_path)

DATA   = os.environ['DATA']
MODELS = os.environ['MODELS']
PROJECT = os.environ['PROJECT']
BATCHFILES = os.environ['BATCHFILES']
LOGS = os.environ['LOGS']
SCRIPTS = os.environ['SCRIPTS']
PARSER = os.environ['PARSER']

input_dir = os.path.dirname(input_path)
output_dir  = os.path.join(input_dir, 'parsed')

print('Output directory:', output_dir)
if not os.path.isdir(output_dir):
    print('Create directory:', output_dir)
    os.mkdir(output_dir)

lang = re.findall(r'.*\.[a-z]{2}-[a-z]{2}\.([a-z]{2})\.?[a-zA-Z]*', input_file)[0]
sys.path.append(SCRIPTS)
from default_code_mappings import default_mappings as d
model_path = f"{MODELS}/UUParser/{d[lang]}/"

log_path = f"{LOGS}/parser"
if not os.path.isdir(log_path):
    print('Create directory:', log_path)
    os.mkdir(log_path)
#--partition=hugemem
batch_string = f"""#!/bin/bash

#SBATCH -t 96:00:00
#SBATCH -n 1
#SBATCH -J "{lang}_parse"
#SBATCH --mem-per-cpu=120GB
#SBATCH --account=nn9447k
#SBATCH --output={log_path}/parse_{d[lang]}-%j.out

source ~/.bashrc

cd $PARSER
python src/parser.py --predict \\
        --outdir {output_dir} \\
        --modeldir {model_path} \\
        --disable-pred-eval \\
        --graph-based \\
        --testfile {input_path}"""


batch_path = f'{BATCHFILES}/parse.sh'
with open(batch_path, 'w') as f:
    f.write(batch_string)
    
os.system(f'sbatch {batch_path}')
