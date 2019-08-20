from .config import *
from .helpers import create_dir, get_split_files
import os, pprint, re, random


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
        self.batch_string = None
        self.shell_string = None
        self.srun_prefix  = 'srun '
        self.shebang = '#!/bin/sh\n'
        self.source  = '\nsource ~/.bashrc\n'
        self.modules = "module purge\nmodule load gcc"


    def construct_command(self, name, num_prefix=1):
        self.batch_string = self.head() + self.command_string.format(*[self.srun_prefix]*num_prefix)
        self.save_batchstring(name=f'latest_{name}.sh')
        self.shell_string = self.shebang + self.modules + self.command_string.format(*['']*num_prefix)

    def head(self):
        slurm_string = f"""
#SBATCH -t {self.timelimit}
#SBATCH -n 1
#SBATCH -J "{self.name}"
#SBATCH --mem-per-cpu={self.memory} --partition={self.partition}
#SBATCH --account={self.account}
#SBATCH --output={self.log_path}/{self.name}-%j.out"""
        return self.shebang + slurm_string + self.modules

    def align(self, input_dir, output_dir, filename):
        self.command_string = f"""
source activate py37
{'{}'}python3 {os.path.join(EFLOMAL, 'align.py')} \\
        -i {os.path.join(input_dir, filename)} \\
        -m 3  \\
        -f {os.path.join(output_dir, filename)}.fwd \\
        -r {os.path.join(output_dir, filename)}.rev
        
{'{}'}python3 {os.path.join(EFLOMAL, 'makepriors.py')} \\
        -i {os.path.join(input_dir, filename)} \\
        -f {os.path.join(output_dir, filename)}.fwd \\
        -r {os.path.join(output_dir, filename)}.rev \\
        --priors {os.path.join(output_dir, filename)}.priors"""
        self.construct_command('align', num_prefix=2)

    def parse(self, model_path, input_path, output_dir):
        self.command_string = f"""
cd {PARSER}
{'{}'}python src/parser.py --predict \\
        --outdir {output_dir} \\
        --modeldir {model_path} \\
        --disable-pred-eval \\
        --graph-based \\
        --testfile {input_path}"""
        self.construct_command('parse')


    def train_uuparser(self, code):
        MODEL_DIR = os.path.join(MODELS, NAME_PARSER)
        create_dir(MODEL_DIR)

        self.command_string = f"""
cd {PARSER}
{'{}'}python src/parser.py \
     --graph-based \
     --outdir {MODEL_DIR} \
     --datadir {TREEBANKS} \
     --include {code} \
     --epochs 30 \
     --dynet-seed 123456788 \
     --dynet-mem 30000 \
     --word-emb-size 300"""
        self.construct_command('train_parser')


    def train_udpipe(self, model_path, train_data_path):
        self.command_string = f"""
{'{}'}udpipe --train \\
    --tagger \\
    --tokenizer {model_path} {train_data_path}"""
        self.construct_command('train_udpipe')

    def tokenize(self, model_path, input_path, output_file):
        self.command_string = f"""
{'{}'}/projects/nlpl/software/udpipe/latest/bin/udpipe --tokenize --tag {model_path} {input_path} > {output_file}"""
        self.construct_command('tokenize')

    def save_batchstring(self, name, history=False, shell=False):
        if history:
            HISTORY = os.path.join(BATCHFILES, 'history')  # put in main config?
            create_dir(HISTORY)
            batch_file_path = os.path.join(HISTORY, name)
        else:
            batch_file_path = os.path.join(BATCHFILES, name)

        with open(batch_file_path, 'w') as f:
            if shell:
                f.write(self.shell_string)
            else:
                f.write(self.batch_string)
        return batch_file_path


    def shell(self):
        shell_path = self.save_batchstring(name='shell_job.sh', shell=True)
        rnd_id = random.randint(10000, 99999)
        logfile = os.path.join(self.log_path, f'{self.name}_{rnd_id}.log')
        batch_history_path = self.save_batchstring(name=f"{rnd_id}.sh", history=True, shell=True)
        print(f'Batchfile location: {batch_history_path}\n')
        command = f'sh {shell_path} &> {logfile} &'
        print(f'Executing:', command)
        shell_output = os.popen(command).read()
        print(shell_output)

    def submit(self):
        batch_path = self.save_batchstring(name='submit.sh')

        shell_output = os.popen(f'sbatch {batch_path}').read() # getting output
        print(shell_output, end='')
        job_id = shell_output.split()[-1]                      # extract job id

        batch_history_path = self.save_batchstring(name=f"{job_id}.sh", history=True)
        print(f'Batchfile location: {batch_history_path}\n')

