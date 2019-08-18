from .config import *
from .helpers import create_dir, get_split_files
import os, pprint, re


class Batch:
    def __init__(self, name, memory, log_dir, timelimit='96:00:00', partition='normal', account='nn9447k'):
        self.name   = name
        self.memory = memory 
        log_path = os.path.join(LOGS, log_dir)
        create_dir(log_path)
        self.log_path  = log_path
        self.timelimit = timelimit
        self.partition = partition
        self.account   = account
        self.batch_string = ''

    def head(self):
        head_string = f"""#!/bin/sh

#SBATCH -t {self.timelimit}
#SBATCH -n 1
#SBATCH -J "{self.name}"
#SBATCH --mem-per-cpu={self.memory} --partition={self.partition}
#SBATCH --account={self.account}
#SBATCH --output={self.log_path}/{self.name}-%j.out

module purge
module load gcc

source ~/.bashrc
        """
        return head_string

    def align(self, input_dir, output_dir, filename):
        command_string = f"""
srun python3 /usit/abel/u1/trembczm/software/eflomal/align.py \\
        -i {os.path.join(input_dir, filename)} \\
        -m 3  \\
        -f {os.path.join(output_dir, filename)}.fwd \\
        -r {os.path.join(output_dir, filename)}.rev
        
srun python3 /usit/abel/u1/trembczm/software/eflomal/makepriors.py \\
        -i {os.path.join(target_dir, filename)} \\
        -f {os.path.join(output_dir, filename)}.fwd \\
        -r {os.path.join(output_dir, filename)}.rev \\
        --priors {os.path.join(output_dir, filename)}.priors"""

        self.batch_string = self.head() + command_string
        self.save_batchstring(name='latest_align.sh')

    def parse(self, model_path, input_path, output_dir):
        command_string = f"""
cd $PARSER
python src/parser.py --predict \\
        --outdir {output_dir} \\
        --modeldir {model_path} \\
        --disable-pred-eval \\
        --graph-based \\
        --testfile {input_path}"""
        self.batch_string = self.head() + command_string
        self.save_batchstring(name='latest_parse.sh')

    def train_uuparser(self, code):
        MODEL_DIR = os.path.join(MODELS, NAME_PARSER)
        create_dir(MODEL_DIR)

        command_string = f"""
cd {PARSER}
srun python src/parser.py \
     --graph-based \
     --outdir {MODEL_DIR} \
     --datadir {TREEBANKS} \
     --include {code} \
     --epochs 30 \
     --dynet-seed 123456788 \
     --dynet-mem 30000 \
     --word-emb-size 300"""
        self.batch_string = self.head() + command_string
        self.save_batchstring(name='latest_train_uuparser.sh')


    def train_udpipe(self, model_path, train_data_path):
        command_string = f"""
srun udpipe --train \\
    --tagger \\
    --tokenizer {model_path} {train_data_path}"""
        self.batch_string = self.head() + command_string
        self.save_batchstring(name='latest_train_udpipe.sh')

    def tokenize(self, model_path, input_path, output_file):
        command_string = f"""
srun /projects/nlpl/software/udpipe/latest/bin/udpipe --tokenize --tag {model_path} {input_path} > {output_file}
        """
        self.batch_string = self.head() + command_string
        self.save_batchstring(name='latest_tokenize.sh')

    def save_batchstring(self, name, history=False):
        if history:
            HISTORY = os.path.join(BATCHFILES, 'history')  # put in main config?
            create_dir(HISTORY)
            batch_file_path = os.path.join(HISTORY, name)
        else:
            batch_file_path = os.path.join(BATCHFILES, name)

        with open(batch_file_path, 'w') as f:
            f.write(self.batch_string)
        return batch_file_path

    def submit(self):
        batch_path = self.save_batchstring(name='submit.sh')

        shell_output = os.popen(f'sbatch {batch_path}').read() # getting output
        print(shell_output)
        job_id = shell_output.split()[-1]                      # extract job id

        batch_history_path = self.save_batchstring(name=f"{job_id}.sh", history=True)
        print(f'Batchfile location: {batch_history_path}')

