#submit_alignment_jobs.py 
import sys, os, re, pprint

# Arg1: directory with merged files
target_dir = os.path.abspath(sys.argv[1])

# Arg2 output directory for alignment files
output_dir = os.path.abspath(sys.argv[2])
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
batch_file_dir = "/usit/abel/u1/trembczm/pronoun_project/batchfiles/alignment"
logfile_dir    = "/usit/abel/u1/trembczm/pronoun_project/logfiles/alignment"
if not os.path.isdir(batch_file_dir):
    print('Create directory:', batch_file_dir)
    os.mkdir(batch_file_dir)
if not os.path.isdir(logfile_dir):
    print('Create directory:', logfile_dir)
    os.mkdir(logfile_dir)
    

files = list(filter(lambda x: re.match(r'.*\.[a-z]{2}-[a-z]{2}', x), os.listdir(target_dir)))
print(f'Valid input files  ("{target_dir}"):')
pprint.pprint(files)
print()
print('Create and submit batchfiles..')


batch_files = []


for file in files:
    pair = file.split('.')[-1]
    batch_string = f"""#!/bin/sh

#SBATCH -t 48:00:00
#SBATCH -n 1
#SBATCH -J "{pair}_align"
#SBATCH --mem-per-cpu=48GB
#SBATCH --account=nn9447k
#SBATCH --output={logfile_dir}/align_{pair}-%j.out
source ~/.bashrc
source activate py37

module purge
module load gcc



srun python3 /usit/abel/u1/trembczm/software/eflomal/align.py \\
        -i {os.path.join(target_dir, file)} \\
        -m 3  \\
        -f {os.path.join(output_dir, file)}.fwd \\
        -r {os.path.join(output_dir, file)}.rev
        
srun python3 /usit/abel/u1/trembczm/software/eflomal/makepriors.py \\
        -i {os.path.join(target_dir, file)} \\
        -f {os.path.join(output_dir, file)}.fwd \\
        -r {os.path.join(output_dir, file)}.rev \\
        --priors {os.path.join(output_dir, file)}.priors
"""
    batch_file = f'batch_{file}.sh'
    batch_path = os.path.join(batch_file_dir, batch_file)
    with open(batch_path, 'w') as f:
        f.write(batch_string)
    batch_files.append(batch_path)
pprint.pprint(batch_files)

print('Submitting batchfiles:')
for batch_file in batch_files:
    print(batch_file)
    os.system(f'sbatch {batch_file}')
    print()
